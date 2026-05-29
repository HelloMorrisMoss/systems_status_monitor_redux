from systems_status_monitor_redux.monitor.evaluators import evaluate_time, evaluate_disk, evaluate_custom, evaluate_http
from systems_status_monitor_redux.models.entities import CheckDefinition, Status, Rule

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

def test_evaluate_http_ok():
    check_def = CheckDefinition(id="h1", name="HTTP", type="http", params={"status_code": 200})
    res = evaluate_http(check_def, "OK body", "", 200)
    assert res.status == Status.OK
    assert "200" in res.summary

def test_evaluate_http_fail_status():
    check_def = CheckDefinition(id="h1", name="HTTP", type="http", params={"status_code": 200})
    res = evaluate_http(check_def, "Error", "", 500)
    assert res.status == Status.CRITICAL
    assert "500" in res.summary

def test_evaluate_http_fail_connection():
    check_def = CheckDefinition(id="h1", name="HTTP", type="http")
    res = evaluate_http(check_def, "", "Connection refused", -1)
    assert res.status == Status.CRITICAL
    assert "Connection failed" in res.summary

def test_evaluate_http_with_rules():
    check_def = CheckDefinition(
        id="h1", 
        name="HTTP", 
        type="http", 
        rules=[Rule(type="contains", pattern="HEALTHY")]
    )
    res = evaluate_http(check_def, '{"status": "HEALTHY"}', "", 200)
    assert res.status == Status.OK
    
    res2 = evaluate_http(check_def, '{"status": "SICK"}', "", 200)
    assert res2.status == Status.CRITICAL
