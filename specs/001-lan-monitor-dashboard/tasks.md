**Propagated**: 2026-06-01 — Updated from spec.md refinement

# Phase 2: Task Breakdown — LAN Monitor Dashboard

This document translates the plan and design into actionable, verifiable tasks. Each task includes Definition of Done (DoD) and references to Functional Requirements (FR) and Success Criteria (SC) from `spec.md`.

## 0. Foundations & Project Scaffolding

0.1 Create source tree and bootstrap app (Option 1: Single Project)
- Paths: `src/`, `src/models/`, `src/monitor/`, `src/api/`, `src/templates/`, `src/utils/`, `tests/unit/`, `tests/integration/`
- Add `src/main.py` with a minimal FastAPI app and `/health` returning `{status: healthy, version}`
- DoD: App starts with `uvicorn src.main:app` or `python -m src.main`; `/health` returns 200 and JSON; structure matches plan
- Refs: FR-001 (indirect), Constitution Health

0.2 Dependency management
- Add `requirements.txt` (fastapi, uvicorn, paramiko, jinja2, pydantic>=2, pytest)
- Pin Python to 3.11 in docs; add `pytest.ini` basic config
- DoD: `pip install -r requirements.txt` succeeds; versions documented in `quickstart.md`
- Refs: Constitution V. Compatibility

0.3 Logging & config helpers
- Implement `src/utils/logging.py` for structured logs (ts, level, message, path, status, latency)
- Implement `src/utils/config.py` (env vars with safe defaults: host=127.0.0.1, port=8000, refresh_interval=30s, staleness_window=120s)
- DoD: Logs appear per request; secrets are redacted; config documented
- Refs: Constitution IV (Observability), II (Secure)

## 1. Models & Contracts

1.1 Pydantic models for core entities
- Implement `MonitoredSystem`, `CheckDefinition`, `Rule`, `CheckResult`, `SystemStatusSummary`
- Include enums for Status: OK, WARNING, CRITICAL, UNKNOWN; FailureCategory: unreachable, auth_failed, timeout, check_failed
- DoD: Models validated by unit tests; JSON serialization aligns with `contracts/api.md`
- Refs: FR-001, FR-003, FR-012

1.2 Config source for systems
- Provide `systems.json` loader in `src/models/config_loader.py`
- Support fields: name, address, username, password, checks[]
- DoD: Loader validates and returns list of `MonitoredSystem`; bad config yields actionable error
- Refs: FR-001, FR-013

## 2. SSH Client & Execution Layer

2.1 Paramiko wrapper
- `src/monitor/ssh_client.py`: connect(host, username, password, timeout); exec(cmd, timeout); redact secrets in errors; detect basic shell or run via `cmd /c`
- DoD: Unit tests with paramiko mocked; timeouts enforced; error categories surfaced
- Refs: FR-012, Constitution III, Minimum Timeouts

2.2 Command presets for checks (Windows/legacy friendly)
- Time: `time /T` (fallback `echo %DATE% %TIME%`)
- Disk: `wmic logicaldisk get caption,freespace,size`
- Custom: pass-through command string (user supplied)
- DoD: Presets returned by helper with docstrings; covered by tests
- Refs: FR-005, FR-006, FR-008

## 3. Evaluators (Output → CheckResult)

3.1 Time evaluator
- Parse `time /T` or `%DATE% %TIME%` output; set status OK and summary string; UNKNOWN on parse failure
- DoD: Unit tests for typical locales and edge cases
- Refs: FR-005

3.2 Disk evaluator
- Parse `wmic logicaldisk` into per-drive metrics; apply thresholds from `CheckDefinition.params` (warning, critical); summarize `XGB free / YGB total`
- DoD: Unit tests for OK, WARNING, CRITICAL; robust to missing drives
- Refs: FR-006, FR-007, SC-003

3.3 Custom command evaluator
- Evaluate pass/fail by (a) nonzero exit → fail, (b) rules on stdout/stderr (contains/not_contains/regex)
- DoD: Unit tests for rule combinations; large output safely truncated in `details`
- Refs: FR-008, FR-009, Edge Case (large output)

3.4 HTTP GET evaluator
- Evaluate pass/fail by (a) connection success, (b) status code (default 200), (c) rules on response body
- DoD: Unit tests for success, 404, 500, and content rules; timeouts handled
- Refs: FR-016, FR-017

## 4. State Store & Scheduler

4.1 In-memory StatusStore
- Map `system_id -> SystemStatusSummary` with per-check `CheckResult`; track `last_checked` and `overall` (worst-of rule)
- DoD: Unit tests for roll-up logic and partial results handling
- Refs: FR-003, FR-004, FR-015

4.2 Background scheduler
- `src/monitor/scheduler.py`: periodic refresh at `refresh_interval`; graceful error handling; cancel on shutdown
- DoD: Integration test with fake clock or short interval; no unbounded waits
- Refs: FR-010, Constitution Timeouts

4.3 Manual refresh trigger
- Expose function to enqueue immediate refresh across all systems
- DoD: Integration test verifies `last_checked` updates promptly
- Refs: FR-011, SC-002

## 5. API & Dashboard

5.1 API routes
- `GET /health`: liveness
- `GET /api/status`: current statuses (as per `contracts/api.md`)
- `POST /api/refresh`: 202 Accepted; starts immediate refresh
- DoD: Contract tests for shapes/fields; error handling with safe messages
- Refs: Contracts, FR-011, Constitution

5.2 HTML dashboard
- `GET /`: Jinja2 template renders one box per system; per-check statuses; overall status color; last checked
- DoD: Manual test renders sample `systems.json`; UI shows mixed states and failure categories
- Refs: FR-002, FR-003, FR-012, SC-001

5.3 Static styles
- Minimal CSS embedded or small file; statuses clearly distinguished
- DoD: Visual clarity for OK/WARNING/CRITICAL/UNKNOWN; partial results evident
- Refs: Edge Cases (partial success)

## 6. Failure Categories & Staleness

6.1 Failure categorization
- Map connection/auth/timeout/exec errors to non-sensitive categories; surface in UI and `/api/status`
- DoD: Unit tests for mapping; UI shows category label
- Refs: FR-012, SC-004

6.2 Staleness indicator
- If `now - last_checked > staleness_window`, mark summary as stale; display warning badge
- DoD: Unit test + UI check
- Refs: FR-015

## 7. Security & Privacy

7.1 Secret handling
- Never log passwords; redact in errors and request logs; config loader ensures secrets omitted from serialized responses
- DoD: Grep check in tests to ensure no secret leakage; code review checklist
- Refs: FR-013, Constitution II

7.2 Local-only default binding
- Bind to `127.0.0.1` unless `BIND_HOST` overridden
- DoD: Verified in `quickstart.md`; startup logs state bind address
- Refs: Constitution II

## 8. Testing Plan

8.1 Unit tests
- Models validation, evaluators (time/disk/custom), roll-up logic, failure mapping, truncation
- DoD: `pytest -q` passes locally; coverage for core paths

8.2 Integration tests
- API with FastAPI `TestClient`; mock SSH client to produce OK/WARN/CRIT/unreachable/auth_failed/timeouts
- DoD: Endpoints return as contracted; refresh updates timestamps within 60s simulated
- Refs: SC-002, Contracts

8.3 Operational checks
- Ensure `/health` unchanged behavior; manual dashboard walkthrough using sample `systems.json`
- DoD: Checklist completed and documented

## 9. Documentation & Ops

9.1 Update `quickstart.md`
- Add instructions for `systems.json` location, env vars, run commands, and Refresh All usage
- DoD: Follow doc to run from clean checkout in <10 minutes
- Refs: SC-005

9.2 Add `README` section or link to specs
- Brief feature overview and known limitations (no persistence, password-only for now)
- DoD: Section present; limitations explicit

## 10. Stretch (Post-MVP, optional)

- Key-based auth support plumbing (config fields, not wired) — Refs: FR-014 (design for future)
- `/ready` readiness endpoint
- Service status helper via `sc query` and `tasklist`
- Configurable per-check timeouts
- CSV/JSON export of current status

## 11. Detailed Check Documentation

11.1 Create detailed documentation for `time` check
- Path: `specs/001-lan-monitor-dashboard/docs/checks/time.md`
- Include: Description, configuration parameters, boilerplate example system
- DoD: File exists and follows structure from FR-019
- Refs: FR-018, FR-019

11.2 Create detailed documentation for `disk` check
- Path: `specs/001-lan-monitor-dashboard/docs/checks/disk.md`
- DoD: File exists and follows structure from FR-019
- Refs: FR-018, FR-019

11.3 Create detailed documentation for `custom` check
- Path: `specs/001-lan-monitor-dashboard/docs/checks/custom.md`
- DoD: File exists and follows structure from FR-019
- Refs: FR-018, FR-019

11.4 Create detailed documentation for `http` check
- Path: `specs/001-lan-monitor-dashboard/docs/checks/http.md`
- DoD: File exists and follows structure from FR-019
- Refs: FR-018, FR-019, SC-006

---

## Acceptance Matrix (traceability)

- FR-001 → Tasks 1.1, 1.2, 5.2
- FR-002 → Task 5.2
- FR-003 → Tasks 4.1, 5.2
- FR-004 → Tasks 4.1, 5.1/5.2 display
- FR-005 → Tasks 2.2, 3.1
- FR-006/FR-007 → Tasks 2.2, 3.2
- FR-008/FR-009 → Tasks 3.3
- FR-010 → Task 4.2
- FR-011 → Tasks 4.3, 5.1 (`POST /api/refresh`)
- FR-012 → Tasks 2.1, 6.1, 5.2
- FR-013 → Task 7.1
- FR-014 → Task 10 (design paths)
- FR-015 → Task 6.2
- FR-016 → Task 3.4
- FR-017 → Task 3.4
- FR-018 → Tasks 11.1-11.4
- FR-019 → Tasks 11.1-11.4
- SC-001 → Task 5.2
- SC-002 → Tasks 4.3, 5.1
- SC-003 → Tasks 3.2 tests
- SC-004 → Tasks 6.1 + UI
- SC-005 → Tasks 9.1
- SC-006 → Tasks 11.4

## Milestones

- M1: Foundations running (`/health`), scaffolding, deps (Tasks 0.x) — 0.5 day
- M2: Models, SSH client, evaluators (Tasks 1–3) — 1.5–2 days
- M3: State store + scheduler + refresh (Tasks 4.x) — 1 day
- M4: API + Dashboard UI (Tasks 5.x) — 1 day
- M5: Failure categories + staleness + tests (Tasks 6–8) — 1 day
- M6: Docs + polish (Tasks 9.x) — 0.5 day
- M7: Detailed Check Documentation (Tasks 11.x) — 0.5 day

Total MVP estimate: ~5.5 days (single engineer), excluding stretch goals.
