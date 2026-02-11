# LAN Monitor Dashboard Quickstart

## Installation
1. Ensure Python 3.11 is installed.
2. Install dependencies:
   ```bash
   pip install fastapi uvicorn paramiko jinja2
   ```

## Configuration
Define your systems in a `config.yaml` or via environment variables (TBD).
Initial implementation will use a simple JSON file for system definitions.

Example `systems.json`:
```json
[
  {
    "name": "Legacy Box",
    "address": "10.0.0.5",
    "username": "admin",
    "password": "secretpassword",
    "checks": [
      {"type": "time"},
      {"type": "disk", "params": {"drive": "C:"}}
    ]
  }
]
```

## Running the App
```bash
python -m src.main
```
The dashboard will be available at `http://127.0.0.1:8000`.

## Health Check
Verify the service is running:
```bash
curl http://127.0.0.1:8000/health
```
