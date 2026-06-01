# LAN Monitor Dashboard Quickstart

## Installation
1. Ensure Python 3.11 is installed.
2. We use `uv` for dependency management. Install dependencies:
   ```powershell
   uv sync
   ```

## Configuration
Define your systems in a `systems.json` file in the project root.

Example `systems.json`:
```json
[
  {
    "id": "legacy-box",
    "name": "Legacy Box",
    "address": "10.0.0.5",
    "username": "admin",
    "password": "secretpassword",
    "checks": [
      {
        "id": "time-check",
        "name": "Time",
        "type": "time"
      },
      {
        "id": "disk-check",
        "name": "C Drive",
        "type": "disk",
        "params": {"drive": "C:", "warning_gb": 10, "critical_gb": 5}
      },
      {
        "id": "custom-service",
        "name": "My Service",
        "type": "custom",
        "command": "sc query MyService",
        "rules": [
          {"type": "contains", "pattern": "RUNNING"}
        ]
      }
    ]
  }
]
```

### Environment Variables
- `BIND_HOST`: Address to bind to (default: `0.0.0.0`)
- `PORT`: Port to listen on (default: `8000`)
- `SYSTEMS_CONFIG_PATH`: Path to the systems config (default: `systems.json`)
- `REFRESH_INTERVAL_SECONDS`: Interval between auto-refreshes (default: `30`)
- `STALENESS_WINDOW_SECONDS`: Time before a result is marked stale (default: `120`)

## Running the App
```powershell
uv run python -m systems_status_monitor_redux.main
```
or
```powershell
uv run systems-status-monitor-redux
```
The dashboard will be available at `http://localhost:8000` or `http://system_address:8000` remotely.

## Check Types
The following check types are supported:
- [Time Check](specs/001-lan-monitor-dashboard/docs/checks/time.md): Verifies system time.
- [Disk Check](specs/001-lan-monitor-dashboard/docs/checks/disk.md): Monitors free space.
- [Custom Command Check](specs/001-lan-monitor-dashboard/docs/checks/custom.md): Runs any shell command and validates output.
- [HTTP Check](specs/001-lan-monitor-dashboard/docs/checks/http.md): Validates web server status and response body.

## Health Check
Verify the service is running:
```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```
