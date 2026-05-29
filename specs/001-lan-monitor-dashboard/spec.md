# Feature Specification: LAN Monitor Dashboard

**Feature Branch**: `[001-lan-monitor-dashboard]`  
**Created**: 2026-02-09  
**Status**: Draft  
**Input**: User description: "Build a dashboard for monitoring the state of systems on the LAN using SSH to query the system time, free space on their storage drives, and for some check the status of servers running on the system. Each system should have its own box on the dashboard with the status of the items checked. Systems are Windows hosts (including legacy). Roughly 5 systems. Include push button refresh. Password auth now, SSH keys later. Custom commands with stdout rules. Legacy-friendly remote command fallbacks. WMIC available."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See current status at a glance (Priority: P1)

As an operator, I want a single dashboard page that shows one status box per monitored system and the status of each configured check, so I can quickly identify which systems need attention.

**Why this priority**: This is the core value: fast situational awareness across all monitored systems.

**Independent Test**: Configure at least two systems with at least one check each; open the dashboard and verify each system has its own box showing overall status plus per-check statuses.

**Acceptance Scenarios**:

1. **Given** at least 2 monitored systems are configured, **When** the operator opens the dashboard, **Then** the dashboard displays one status box per system with the system’s name and address.
2. **Given** a system has a mix of passing and failing checks, **When** the operator views that system’s status box, **Then** the overall status reflects the worst check state and the failing check(s) are clearly indicated.
3. **Given** a system is unreachable or cannot be accessed, **When** the dashboard updates, **Then** that system’s status box shows an unavailable state and a non-sensitive reason category (for example: unreachable, authentication failed, or timeout).

---

### User Story 2 - Refresh now to confirm recovery (Priority: P2)

As an operator, I want a “Refresh All” action to immediately re-check all monitored systems, so I can confirm whether a system has recovered without waiting for the scheduled update.

**Why this priority**: During troubleshooting, operators need immediate confirmation to reduce downtime and uncertainty.

**Independent Test**: Cause a check to change state on a monitored system; trigger Refresh All; verify the “last checked” time and visible statuses update.

**Acceptance Scenarios**:

1. **Given** the dashboard is open, **When** the operator triggers “Refresh All”, **Then** the system initiates an immediate update for all monitored systems and displays updated “last checked” timestamps.

---

### User Story 3 - Configure checks per system (Priority: P3)

As an operator, I want to configure which checks run per system (time, disk free by drive letter, custom command checks with output-based rules, and HTTP GET requests for server health), so the dashboard reflects each system’s role and constraints.

**Why this priority**: Different systems require different validation; the solution must support per-system customization, including legacy compatibility.

**Independent Test**: Configure System A with a disk check and System B with a custom command check and an HTTP GET check; verify each system’s status box only shows its configured checks and evaluates status correctly.

**Acceptance Scenarios**:

1. **Given** two systems have different configured checks, **When** the dashboard shows their status boxes, **Then** each system displays only the checks configured for it.
2. **Given** a custom command check has a rule that evaluates based on command output content, **When** the command output matches (or does not match) the rule, **Then** the check status is set to passing (or failing) accordingly.

---

### Edge Cases

- A system can be accessed, but a specific check cannot run due to system differences (older Windows environment, missing utilities, or incompatible command behavior).
- A custom command produces very large output; the dashboard must remain usable and not become slow or unreadable.
- Only some checks succeed for a system; the dashboard must show partial results clearly and compute an accurate overall status.
- Results become stale because updates have not completed successfully within the configured staleness window.

## Requirements *(mandatory)*

### Assumptions

- The operator monitors approximately 5 systems on a local network.
- Monitored systems are Windows-based, including older/legacy variants; check execution must be compatible with a range of system capabilities.
- Remote access uses secure remote command execution over the network and supports password-based access initially, with the ability to add key-based access later.

### Functional Requirements

- **FR-001**: System MUST allow the operator to define a list of monitored systems, each with a display name and network address.
- **FR-002**: System MUST display a dashboard view that shows one distinct status box per monitored system.
- **FR-003**: Each system’s status box MUST display an overall status derived from its check results using a consistent roll-up rule (worst check state determines overall state).
- **FR-004**: System MUST record and display the most recent “last checked” time for each monitored system.
- **FR-005**: System MUST support a time check that retrieves the monitored system’s current time and reports success/failure with a clear summary.
- **FR-006**: System MUST support disk free checks for operator-specified drive letters and report free space in a human-readable way.
- **FR-007**: Disk free checks MUST evaluate against operator-configured warning and critical thresholds and report a corresponding status.
- **FR-008**: System MUST support custom command checks per system.
- **FR-009**: Custom command checks MUST support pass/fail evaluation based on both (a) command success/failure outcome and (b) rule-based evaluation of command output content.
- **FR-010**: System MUST support scheduled updates at a configurable interval.
- **FR-011**: System MUST provide a manual “Refresh All” action that triggers an immediate update outside the normal schedule.
- **FR-012**: System MUST classify and display non-sensitive failure categories for access or execution problems (for example: unreachable, authentication failed, timeout, or check execution failed).
- **FR-013**: System MUST support password-based access for monitored systems without exposing passwords in the user interface or logs.
- **FR-014**: System MUST be designed so that adding key-based access in the future does not require rewriting the feature requirements or changing the dashboard user experience.
- **FR-015**: System MUST handle partial and stale results: if results are older than a configurable staleness window, the system MUST indicate that the displayed state may be out of date.
- **FR-016**: System MUST support HTTP GET checks to verify the status of software servers.
- **FR-017**: HTTP GET checks MUST evaluate success based on (a) successful connection/response and (b) optional status code or content-based rules.

### Key Entities *(include if feature involves data)*

- **Monitored System**: A LAN host being monitored (name, address, access configuration reference, enabled checks).
- **Check Definition**: A configured check for a system (type, parameters such as drive letter or command, evaluation rules).
- **Check Result**: The latest outcome of a check (status, summary, timestamp, optional details).
- **System Status Summary**: The rolled-up view of system state (overall status, last checked time, list of check results).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An operator can open the dashboard and see a status box for each configured system (up to 5) without additional setup steps beyond documented configuration.
- **SC-002**: When the operator triggers “Refresh All”, all systems display updated “last checked” timestamps within 60 seconds under normal LAN conditions.
- **SC-003**: In validation testing, disk free checks correctly classify at least three threshold situations (OK, warning, critical) across configured drives.
- **SC-004**: In failure-mode validation, the dashboard presents at least three distinct, non-sensitive failure categories (unreachable, authentication failed, timeout) in a way an operator can act on.
- **SC-005**: An operator can add a new monitored system with at least one check and see it appear on the dashboard within 10 minutes by following the documentation.