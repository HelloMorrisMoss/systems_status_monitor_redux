import json
from pathlib import Path
from typing import List
from pydantic import TypeAdapter
from src.models.entities import MonitoredSystem

def load_systems_config(config_path: str) -> List[MonitoredSystem]:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(path, "r") as f:
        data = json.load(f)
    
    # Using TypeAdapter for List[MonitoredSystem] in Pydantic v2
    adapter = TypeAdapter(List[MonitoredSystem])
    return adapter.validate_python(data)
