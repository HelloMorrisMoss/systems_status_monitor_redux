# Tasks — LAN Monitor Dashboard

**Propagated**: 2026-06-01 — Formatted according to speckit standard

This document translates the plan and design into actionable, verifiable tasks. Each task includes references to Functional Requirements (FR) and Success Criteria (SC) from `spec.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create source tree and bootstrap app in `src/`, `tests/` (Refs: FR-001)
- [x] T002 Implement basic FastAPI app with `/health` in `src/systems_status_monitor_redux/main.py`
- [x] T003 Setup dependency management in `requirements.txt` and `pyproject.toml` (Refs: Constitution V)
- [x] T004 [P] Implement structured logging in `src/systems_status_monitor_redux/utils/logging.py` (Refs: Constitution IV)
- [x] T005 [P] Implement configuration handling in `src/systems_status_monitor_redux/utils/config.py` (Refs: Constitution II)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T006 Implement Pydantic models for core entities in `src/systems_status_monitor_redux/models/entities.py` (Refs: FR-001, FR-003, FR-012)
- [x] T007 Implement system config loader in `src/systems_status_monitor_redux/models/config_loader.py` (Refs: FR-001, FR-013)
- [x] T008 Implement Paramiko SSH client wrapper in `src/systems_status_monitor_redux/monitor/ssh_client.py` (Refs: FR-012, Constitution III)
- [x] T009 Implement in-memory state store in `src/systems_status_monitor_redux/monitor/store.py` (Refs: FR-003, FR-004, FR-015)
- [x] T010 [P] Implement secret redaction and 127.0.0.1 default binding in `src/systems_status_monitor_redux/utils/config.py` (Refs: FR-013, Constitution II)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - See current status at a glance (Priority: P1) 🎯 MVP

**Goal**: As an operator, I want a single dashboard page that shows one status box per monitored system and the status of each configured check.

**Independent Test**: Configure at least two systems with at least one check each; open the dashboard and verify each system has its own box showing overall status plus per-check statuses.

- [x] T011 [US1] Implement API routes for current status in `src/systems_status_monitor_redux/main.py` (Refs: FR-003, FR-004)
- [x] T012 [US1] Create Jinja2 HTML dashboard template in `src/systems_status_monitor_redux/templates/dashboard.html` (Refs: FR-002, SC-001)
- [x] T013 [US1] Implement background monitor scheduler in `src/systems_status_monitor_redux/monitor/scheduler.py` (Refs: FR-010)
- [x] T014 [US1] Implement failure categorization logic in `src/systems_status_monitor_redux/monitor/store.py` (Refs: FR-012, SC-004)
- [x] T015 [US1] Implement result staleness tracking in `src/systems_status_monitor_redux/monitor/store.py` and UI indicators in `src/systems_status_monitor_redux/templates/dashboard.html` (Refs: FR-015)
- [x] T016 [P] [US1] Add minimal CSS for status distinguishing in `src/systems_status_monitor_redux/static/dashboard.css`

**Checkpoint**: User Story 1 functional and testable independently.

---

## Phase 4: User Story 2 - Refresh now to confirm recovery (Priority: P2)

**Goal**: As an operator, I want a “Refresh All” action to immediately re-check all monitored systems.

**Independent Test**: Cause a check to change state; trigger Refresh All; verify the “last checked” time and visible statuses update.

- [x] T017 [US2] Implement manual refresh trigger in `src/systems_status_monitor_redux/monitor/scheduler.py` (Refs: FR-011)
- [x] T018 [US2] Add API endpoint `POST /api/refresh` to trigger immediate scan (Refs: FR-011, SC-002)
- [x] T019 [US2] Add refresh button to `src/systems_status_monitor_redux/templates/dashboard.html` (Refs: FR-011)

---

## Phase 5: User Story 3 - Configure checks per system (Priority: P3)

**Goal**: Support time, disk, custom command, and HTTP GET checks per system.

**Independent Test**: Configure System A with disk check and System B with custom check; verify each shows only its configured checks.

- [x] T020 [US3] Implement command presets for Windows checks (Time, Disk, cmd /c fallbacks) in `src/systems_status_monitor_redux/monitor/commands.py` (Refs: FR-005, FR-006)
- [x] T021 [P] [US3] Implement Time check evaluator in `src/systems_status_monitor_redux/monitor/evaluators.py` (Refs: FR-005)
- [x] T022 [P] [US3] Implement Disk check evaluator in `src/systems_status_monitor_redux/monitor/evaluators.py` (Refs: FR-006, FR-007, SC-003)
- [x] T023 [P] [US3] Implement Custom command evaluator with stdout rules and output truncation in `src/systems_status_monitor_redux/monitor/evaluators.py` (Refs: FR-008, FR-009)
- [x] T024 [P] [US3] Implement HTTP GET check evaluator in `src/systems_status_monitor_redux/monitor/evaluators.py` (Refs: FR-016, FR-017)

---

## Phase 6: User Story 4 - Detailed documentation for checks (Priority: P4)

**Goal**: Provide detailed documentation for each supported check type with clear examples.

**Independent Test**: Navigate to each check's README; verify description, parameters, and example exist.

- [x] T025 [P] [US4] Create detailed documentation for `time` check in `specs/001-lan-monitor-dashboard/docs/checks/time.md` (Refs: FR-018, FR-019)
- [x] T026 [P] [US4] Create detailed documentation for `disk` check in `specs/001-lan-monitor-dashboard/docs/checks/disk.md` (Refs: FR-018, FR-019)
- [x] T027 [P] [US4] Create detailed documentation for `custom` check in `specs/001-lan-monitor-dashboard/docs/checks/custom.md` (Refs: FR-018, FR-019)
- [x] T028 [P] [US4] Create detailed documentation for `http` check in `specs/001-lan-monitor-dashboard/docs/checks/http.md` (Refs: FR-018, FR-019, SC-006)
- [x] T029 [US4] Link detailed check documentation in root `README.md` (Refs: FR-018)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation, testing, and operational readiness.

- [x] T030 [P] Update `quickstart.md` with usage instructions (Refs: SC-005)
- [x] T031 [P] Document design for future key-based auth and known limitations in `README.md` (Refs: FR-014, FR-013)
- [x] T032 [P] Implement unit tests for evaluators and models in `tests/unit/` (Refs: SC-003)
- [x] T033 [P] Implement integration tests for API and scheduler in `tests/integration/` (Refs: SC-002)
- [x] T034 Perform final operational checks and manual dashboard walkthrough

---

## Phase 8: Stretch Goals (Optional)

**Purpose**: Post-MVP enhancements and future-proofing.

- [ ] T035 [P] Support key-based auth plumbing in `src/systems_status_monitor_redux/models/entities.py` (Refs: FR-014)
- [ ] T036 [P] Implement service status helper via `sc query` in `src/systems_status_monitor_redux/monitor/commands.py`
- [ ] T037 [P] Add configurable per-check timeouts in `src/systems_status_monitor_redux/models/entities.py`
- [ ] T038 Implement CSV/JSON export of current status in `src/systems_status_monitor_redux/main.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion.
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion.
- **Polish (Phase 7)**: Depends on all desired user stories being complete.
- **Stretch Goals (Phase 8)**: Depends on Phase 7 completion (optional).

### User Story Dependencies

- **User Story 1 (P1)**: Foundation ready.
- **User Story 2 (P2)**: Foundation ready + US1 (for UI).
- **User Story 3 (P3)**: Foundation ready.
- **User Story 4 (P4)**: User Story 3 complete.

---

## Parallel Execution Examples

```bash
# Implementation of evaluators can happen in parallel
Task: "T021 [P] [US3] Implement Time check evaluator in src/systems_status_monitor_redux/monitor/evaluators.py"
Task: "T022 [P] [US3] Implement Disk check evaluator in src/systems_status_monitor_redux/monitor/evaluators.py"
Task: "T023 [P] [US3] Implement Custom command evaluator with stdout rules and output truncation in src/systems_status_monitor_redux/monitor/evaluators.py"
Task: "T024 [P] [US3] Implement HTTP GET check evaluator in src/systems_status_monitor_redux/monitor/evaluators.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2.
2. Complete Phase 3 (US1).
3. **STOP and VALIDATE**: Test User Story 1 independently.

---

## Acceptance Matrix (traceability)

- FR-001 → T001, T006, T007
- FR-002 → T012
- FR-003 → T006, T009, T011
- FR-004 → T009, T011
- FR-005 → T020, T021
- FR-006 → T020, T022
- FR-007 → T022
- FR-008 → T023
- FR-009 → T023
- FR-010 → T013
- FR-011 → T017, T018, T019
- FR-012 → T006, T008, T014
- FR-013 → T007, T010
- FR-014 → T031
- FR-015 → T009, T015
- FR-016 → T024
- FR-017 → T024
- FR-018 → T025, T026, T027, T028, T029
- FR-019 → T025, T026, T027, T028
- SC-001 → T012
- SC-002 → T018, T033
- SC-003 → T022, T032
- SC-004 → T014
- SC-005 → T030
- SC-006 → T028

---

## Milestones

- M1: Foundations running (`/health`), scaffolding, deps (T001-T005) — COMPLETED
- M2: Models, SSH client, state store (T006-T010) — COMPLETED
- M3: Core Dashboard & Scheduler (T011-T016) — COMPLETED
- M4: Refresh Functionality (T017-T019) — COMPLETED
- M5: Multi-check Support (T020-T024) — COMPLETED
- M6: Detailed Documentation (T025-T029) — COMPLETED
- M7: Final Polish & Testing (T030-T034) — COMPLETED (base implementation)
- M8: Stretch Goals (T035-T038) — NOT STARTED

Total MVP estimate: ~5.5 days (single engineer).
