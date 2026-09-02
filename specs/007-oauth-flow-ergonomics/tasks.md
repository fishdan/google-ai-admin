# Tasks: Authorization Flow Ergonomics and Safety

**Input**: `spec.md`

- [x] T001 Make the callback timeout configurable via `GOOGLE_OAUTH_TIMEOUT` with a longer default (FR-001, FR-002).
- [x] T002 Register a Windows browser under WSL when `BROWSER` is unset (FR-003, FR-004).
- [x] T003 Print a do-not-share warning alongside the authorization URL (FR-005, FR-007).
- [x] T004 Explain the exposure and recovery when the flow times out (FR-006, FR-007).
- [x] T005 Add tests for timeout parsing, WSL detection, and browser precedence.
- [x] T006 Document the environment variables and the warning in the README.
- [x] T007 Run tests, syntax checks, and a live authorization attempt.
- [x] T009 Use a non-blocking browser class and default to a private window (FR-008, FR-009).
- [x] T008 Record implementation and validation in progress history and update handoff.
