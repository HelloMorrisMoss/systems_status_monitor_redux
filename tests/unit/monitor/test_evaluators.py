import pytest
from src.monitor.evaluators import evaluate_time, evaluate_disk, evaluate_custom
from src.models.entities import CheckDefinition, Status, Rule

def test_evaluate_time():
    check_def = CheckDefinition(id="t1", name="Time", type="time")
    res = evaluate_time(check_def, "02:45 PM", "", 0)
    assert res.status == Status.OK
    assert "02:45 PM" in res.summary

def test_evaluate_disk_ok():
    check_def = CheckDefinition(id="d1", name="Disk", type="disk", params={"drive": "C", "warning_gb": 10, "critical_gb": 5})
    stdout = "Caption  FreeSpace     Size\r\nC:       20000000000   100000000000\r\n"
    res = evaluate_disk(check_def, stdout, "", 0)
    assert res.status == Status.OK
    assert "18.6GB free" in res.summary

def test_evaluate_disk_warning():
    check_def = CheckDefinition(id="d1", name="Disk", type="disk", params={"drive": "C", "warning_gb": 10, "critical_gb": 5})
    # ~7.45 GB free
    stdout = "Caption  FreeSpace     Size\r\nC:       8000000000    100000000000\r\n"
    res = evaluate_disk(check_def, stdout, "", 0)
    assert res.status == Status.WARNING

def test_evaluate_custom_contains():
    check_def = CheckDefinition(
        id="c1", 
        name="Custom", 
        type="custom", 
        rules=[Rule(type="contains", pattern="running")]
    )
    res = evaluate_custom(check_def, "service is running", "", 0)
    assert res.status == Status.OK
    
    res2 = evaluate_custom(check_def, "service is stopped", "", 0)
    assert res2.status == Status.CRITICAL

def test_evaluate_custom_regex():
    check_def = CheckDefinition(
        id="c1", 
        name="Custom", 
        type="custom", 
        rules=[Rule(type="regex", pattern="[0-9]+ units")]
    )
    res = evaluate_custom(check_def, "found 42 units in pool", "", 0)
    assert res.status == Status.OK
    
    res2 = evaluate_custom(check_def, "no units found", "", 0)
    assert res2.status == Status.CRITICAL
