import pytest
import json
from systems_status_monitor_redux.models.entities import MonitoredSystem
from systems_status_monitor_redux.models.config_loader import load_systems_config

def test_monitored_system_pydantic_validation():
    data = {
        "id": "sys1",
        "name": "System 1",
        "address": "1.2.3.4",
        "username": "user",
        "password": "pass",
        "checks": [
            {
                "id": "c1",
                "name": "Time Check",
                "type": "time"
            }
        ]
    }
    system = MonitoredSystem(**data)
    assert system.id == "sys1"
    assert system.password.get_secret_value() == "pass"
    assert len(system.checks) == 1
    assert system.checks[0].type == "time"

def test_load_systems_config(tmp_path):
    config_file = tmp_path / "systems.json"
    data = [
        {
            "id": "sys1",
            "name": "System 1",
            "address": "1.2.3.4",
            "username": "user",
            "password": "pass",
            "checks": []
        }
    ]
    config_file.write_text(json.dumps(data))
    
    systems = load_systems_config(str(config_file))
    assert len(systems) == 1
    assert systems[0].id == "sys1"

def test_load_systems_config_not_found():
    with pytest.raises(FileNotFoundError):
        load_systems_config("non_existent.json")
