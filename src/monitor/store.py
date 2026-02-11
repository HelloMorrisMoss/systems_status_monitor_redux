import threading
import logging
from typing import Dict, List, Optional
from datetime import datetime
from src.models.entities import SystemStatusSummary, Status, CheckResult, FailureCategory

logger = logging.getLogger(__name__)

class StatusStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._store: Dict[str, SystemStatusSummary] = {}

    def update_system_status(self, summary: SystemStatusSummary):
        with self._lock:
            self._store[summary.system_id] = summary

    def get_all_statuses(self) -> List[SystemStatusSummary]:
        with self._lock:
            return list(self._store.values())

    def get_system_status(self, system_id: str) -> Optional[SystemStatusSummary]:
        with self._lock:
            return self._store.get(system_id)

# Singleton instance
store = StatusStore()

def rollup_status(results: List[CheckResult]) -> Status:
    """
    Rolls up check results into an overall status (worst case).
    """
    if not results:
        return Status.UNKNOWN
    
    statuses = [r.status for r in results]
    if Status.CRITICAL in statuses:
        return Status.CRITICAL
    if Status.WARNING in statuses:
        return Status.WARNING
    if Status.UNKNOWN in statuses:
        return Status.UNKNOWN
    return Status.OK
