# Phase 1: Design - LAN Monitor Dashboard

## Architecture
The system follows a simple Producer-Consumer model where a background scheduler (Producer) updates system states, and a web server (Consumer) serves the dashboard.

- **Backend**: Python 3.11 with FastAPI (minimal, high performance).
- **Frontend**: Server-side rendered HTML (Jinja2) or a simple JSON-based SPA. Given the "minimal dependencies" principle, server-side rendering is preferred.
- **State Management**: In-memory store (Singleton) to hold the latest `CheckResult` for each `MonitoredSystem`. No persistence required initially as per specs.

## Data Model

### MonitoredSystem
- `id`: UUID
- `name`: string
- `address`: string
- `username`: string
- `password`: string (Sensitive, redacted in logs)
- `checks`: List[CheckDefinition]

### CheckDefinition
- `type`: "time" | "disk" | "custom" | "http"
- `params`: Dict (e.g., `{"drive": "C:"}`, `{"command": "tasklist"}`, `{"url": "http://localhost:8080/health"}`)
- `rules`: List[Rule] (for custom commands and HTTP content)

### CheckResult
- `status`: "OK" | "WARNING" | "CRITICAL" | "UNKNOWN"
- `summary`: string
- `timestamp`: datetime
- `details`: string (stdout or error message)

## Class Diagram (Conceptual)
- `DashboardApp`: Main entry point, configures routes.
- `SystemMonitor`: Background task runner.
- `SSHClient`: Wrapper around Paramiko for Windows-specific execution.
- `CheckEvaluator`: Logic to turn command output into `CheckResult`.

## Component Interaction
1. `SystemMonitor` loops through all `MonitoredSystem`s.
2. For each system, it opens an `SSHClient` connection.
3. Executes commands defined in `CheckDefinition`.
4. `CheckEvaluator` parses output.
5. Updates the central `StatusStore`.
6. Dashboard `/` route reads from `StatusStore`.
