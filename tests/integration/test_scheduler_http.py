import pytest
import httpx
from unittest.mock import patch, MagicMock
from systems_status_monitor_redux.monitor.scheduler import MonitorScheduler
from systems_status_monitor_redux.models.entities import MonitoredSystem, CheckDefinition, Status, SecretStr
from systems_status_monitor_redux.monitor.store import store

@pytest.fixture
def mock_system():
    return MonitoredSystem(
        id="test-http-sys",
        name="Test HTTP System",
        address="1.2.3.4",
        username="user",
        password=SecretStr("pass"),
        checks=[
            CheckDefinition(
                id="h1",
                name="HTTP Check",
                type="http",
                params={"url": "http://example.com/health", "status_code": 200}
            )
        ]
    )

def test_refresh_system_http_success(mock_system):
    scheduler = MonitorScheduler(systems=[mock_system])
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    
    with patch("httpx.get", return_value=mock_response) as mock_get:
        scheduler._refresh_system(mock_system)
        
        mock_get.assert_called_once_with(
            "http://example.com/health", 
            timeout=5.0, 
            follow_redirects=True,
            proxy=None,
            trust_env=False
        )
        
        summary = store.get_all_statuses()[0]
        assert summary.system_id == "test-http-sys"
        assert summary.overall_status == Status.OK
        assert len(summary.check_results) == 1
        assert summary.check_results[0].status == Status.OK
        assert "200" in summary.check_results[0].summary

def test_refresh_system_http_with_proxy(mock_system):
    # Add proxy to check params
    mock_system.checks[0].params["proxy"] = "http://proxy.example.com:8080"
    scheduler = MonitorScheduler(systems=[mock_system])
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    
    with patch("httpx.get", return_value=mock_response) as mock_get:
        scheduler._refresh_system(mock_system)
        
        mock_get.assert_called_once_with(
            "http://example.com/health", 
            timeout=5.0, 
            follow_redirects=True,
            proxy="http://proxy.example.com:8080",
            trust_env=True
        )

def test_refresh_system_http_failure(mock_system):
    scheduler = MonitorScheduler(systems=[mock_system])
    
    with patch("httpx.get", side_effect=httpx.RequestError("Connection failed")) as mock_get:
        scheduler._refresh_system(mock_system)
        
        summary = store.get_all_statuses()[0]
        assert summary.overall_status == Status.CRITICAL
        assert "Connection failed" in summary.check_results[0].details
