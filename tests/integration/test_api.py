import pytest
from fastapi.testclient import TestClient
from systems_status_monitor_redux.main import app
from systems_status_monitor_redux.monitor.store import store
from systems_status_monitor_redux.models.entities import SystemStatusSummary, Status
from datetime import datetime

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_dashboard_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "LAN Monitor Dashboard" in response.text

def test_api_status_endpoint(client):
    # Inject fake data into store
    summary = SystemStatusSummary(
        system_id="test-sys",
        overall_status=Status.OK,
        last_checked=datetime.utcnow(),
        check_results=[]
    )
    store.update_system_status(summary)
    
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(s["system_id"] == "test-sys" for s in data)

def test_api_refresh_endpoint(client):
    response = client.post("/api/refresh")
    assert response.status_code == 202
    assert response.json()["status"] == "refresh triggered"
