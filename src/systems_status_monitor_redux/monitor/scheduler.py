import threading
import logging
import httpx
from datetime import datetime
from typing import List, Optional
from systems_status_monitor_redux.models.entities import MonitoredSystem, SystemStatusSummary, CheckResult, Status, FailureCategory
from systems_status_monitor_redux.monitor.ssh_client import SSHClientWrapper
from systems_status_monitor_redux.monitor.commands import get_check_command
from systems_status_monitor_redux.monitor.evaluators import get_evaluator
from systems_status_monitor_redux.monitor.store import store, rollup_status

logger = logging.getLogger(__name__)

class MonitorScheduler:
    def __init__(self, systems: List[MonitoredSystem], interval: int = 30):
        self.systems = systems
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._refresh_lock = threading.Lock()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info(f"Monitor scheduler started with interval {self.interval}s")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Monitor scheduler stopped")

    def _run(self):
        while not self._stop_event.is_set():
            self.refresh_all()
            # Wait for interval or stop event
            self._stop_event.wait(self.interval)

    def refresh_all(self):
        if not self._refresh_lock.acquire(blocking=False):
            logger.info("Refresh already in progress, skipping")
            return
        
        try:
            logger.info(f"Starting refresh for {len(self.systems)} systems")
            threads = []
            for system in self.systems:
                t = threading.Thread(target=self._refresh_system, args=(system,))
                t.start()
                threads.append(t)
            
            for t in threads:
                t.join()
            logger.info("Refresh complete")
        finally:
            self._refresh_lock.release()

    def _refresh_system(self, system: MonitoredSystem):
        logger.info(f"Refreshing system {system.name} ({system.address})")
        results = []
        failure_category = FailureCategory.NONE
        
        # 1. Handle HTTP checks (independent of SSH)
        for check_def in system.checks:
            if check_def.type == "http":
                url = check_def.params.get("url")
                if not url:
                    results.append(CheckResult(
                        check_id=check_def.id,
                        status=Status.UNKNOWN,
                        summary="Missing 'url' parameter for http check"
                    ))
                    continue
                
                try:
                    timeout = check_def.params.get("timeout", 5.0)
                    response = httpx.get(url, timeout=timeout, follow_redirects=True)
                    evaluator = get_evaluator("http")
                    results.append(evaluator(check_def, response.text, "", response.status_code))
                except httpx.RequestError as exc:
                    evaluator = get_evaluator("http")
                    results.append(evaluator(check_def, "", str(exc), -1))

        # 2. Handle SSH-based checks
        ssh_checks = [c for c in system.checks if c.type != "http"]
        if ssh_checks:
            with SSHClientWrapper(system.address, system.username, system.password.get_secret_value()) as client:
                success, category, msg = client.connect()
                if not success:
                    # If SSH fails, and we have SSH checks, we need to report that failure
                    # If we already had some results (from HTTP), we append SSH failure results
                    for check_def in ssh_checks:
                        results.append(CheckResult(
                            check_id=check_def.id,
                            status=Status.CRITICAL,
                            summary=f"SSH Connection failed: {category}",
                            details=msg
                        ))
                    failure_category = category or FailureCategory.CHECK_FAILED
                else:
                    for check_def in ssh_checks:
                        cmd = get_check_command(check_def.type, check_def.command)
                        exit_status, stdout, stderr = client.execute(cmd)
                        
                        evaluator = get_evaluator(check_def.type)
                        if evaluator:
                            res = evaluator(check_def, stdout, stderr, exit_status)
                            results.append(res)
                        else:
                            results.append(CheckResult(
                                check_id=check_def.id,
                                status=Status.UNKNOWN,
                                summary=f"Unknown check type: {check_def.type}"
                            ))

        summary = SystemStatusSummary(
            system_id=system.id,
            overall_status=rollup_status(results) if results else Status.UNKNOWN,
            last_checked=datetime.utcnow(),
            check_results=results,
            failure_category=failure_category
        )
        store.update_system_status(summary)
