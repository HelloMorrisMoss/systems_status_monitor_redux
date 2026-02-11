import pytest
from src.monitor.store import StatusStore, rollup_status
from src.models.entities import SystemStatusSummary, Status, CheckResult, FailureCategory
from datetime import datetime

def test_rollup_status():
    results = [
        CheckResult(check_id="1", status=Status.OK, summary="ok"),
        CheckResult(check_id="2", status=Status.WARNING, summary="warn")
    ]
    assert rollup_status(results) == Status.WARNING

    results.append(CheckResult(check_id="3", status=Status.CRITICAL, summary="crit"))
    assert rollup_status(results) == Status.CRITICAL

    assert rollup_status([]) == Status.UNKNOWN

def test_store_update_get():
    store = StatusStore()
    summary = SystemStatusSummary(
        system_id="sys1",
        overall_status=Status.OK,
        last_checked=datetime.utcnow()
    )
    store.update_system_status(summary)
    
    assert store.get_system_status("sys1") == summary
    assert len(store.get_all_statuses()) == 1
    assert store.get_all_statuses()[0].system_id == "sys1"
