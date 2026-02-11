# Dashboard Server App Constitution

## Core Principles

### I. Ship a Working Dashboard (Minimum Scope)
The app MUST provide, at minimum:
- A running HTTP server with a **health endpoint** (e.g., `/health`) returning success when the process is ready.
- At least one **dashboard route** (HTML and/or JSON) that renders/returns meaningful status data.
- A clear **startup command** and a single, documented **configuration method** (environment variables preferred).

### II. Secure by Default
The app MUST:
- Bind to a safe interface by default (e.g., `127.0.0.1`) unless explicitly configured otherwise.
- Never log secrets. Any sensitive values MUST be redacted or omitted.
- Validate and sanitize all external inputs (query params, headers, body).
- Use authentication/authorization if exposed beyond localhost; if not implemented, it MUST be explicitly documented as “local-only”.

### III. Reliability & Correctness Over Cleverness
The app MUST:
- Fail fast on invalid configuration with actionable error messages.
- Provide deterministic behavior (no reliance on timing hacks).
- Handle expected failures gracefully (timeouts, upstream errors, empty datasets) with clear user-facing messages and proper HTTP status codes.

### IV. Observability Is Non‑Optional
The app MUST include:
- Structured logging (at least: timestamp, level, message, request path, status code, latency).
- A minimal request log for every HTTP request (success and error).
- An error path that captures stack traces in logs (server-side only), while returning safe error responses to clients.

### V. Compatibility, Simplicity, and Explicit Contracts
The app MUST:
- Pin to a supported Python runtime (Python 3.11.x).
- Keep dependencies minimal and justified.
- Define explicit response contracts for any JSON endpoints (fields, types, and error format documented).
- Prefer simple, maintainable design (YAGNI). No abstractions without clear payoff.

## Minimum Operational Requirements
- **Configuration**: via environment variables; defaults must be safe.
- **Ports**: configurable; collisions must produce a clear startup failure.
- **Health/Readiness**: `/health` (liveness) and, if the app depends on upstreams, a `/ready` (readiness) endpoint.
- **Timeouts**: outbound calls MUST have timeouts; no unbounded waits.
- **Static assets** (if any): must be served correctly or bundled/managed explicitly (no “works on my machine” paths).

## Development Workflow & Quality Gates
- Every change MUST include one of:
  - a unit test, or
  - an integration test, or
  - a written justification for why testing is not applicable.
- CI/local runs MUST be documented and reproducible.
- Before merging:
  - lint/format checks pass (or the project documents why not used),
  - tests pass,
  - `/health` behavior is unchanged unless explicitly intended and documented.

## Governance
- This constitution is the source of truth for minimum requirements.
- Any exception MUST be documented in the PR/commit message and revisited.
- Amendments require:
  - a short rationale,
  - migration notes (if behavior changes),
  - version bump.

**Version**: 1.0.0 | **Ratified**: 2026-02-09 | **Last Amended**: 2026-02-09
