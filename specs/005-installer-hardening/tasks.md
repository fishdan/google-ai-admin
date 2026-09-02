# Tasks: Installer Hardening and Per-Command Authorization

**Input**: `spec.md`, `plan.md`

## Installer

- [x] T001 Add an `ensurepip` preflight check with Debian/Ubuntu remediation text (FR-001).
- [x] T002 Remove incomplete or failed `.venv` directories so retries succeed (FR-002).
- [x] T003 Print the absolute install directory in the closing output (FR-003).

## Authorization model

- [x] T004 Add profile-aware token paths and profile name validation (FR-006, FR-007).
- [x] T005 Exclude every token file from OAuth client discovery (FR-008).
- [x] T006 Declare per-command scopes and request only those, unioned with granted scopes (FR-009).
- [x] T007 Build only the API service each command uses.

## Readiness gate

- [x] T008 Report per-command readiness and name missing scopes (FR-010, FR-011).

## Documentation

- [x] T009 Document `GOOGLE_AI_ADMIN_DIR` and the default install location in the quick start (FR-004).
- [x] T010 Anchor the credential placement snippet to the installed checkout (FR-005).
- [x] T011 Explain restricted scopes and the OAuth audience choice (FR-012).
- [x] T012 Document `--profile` and per-command scopes.
- [x] T013 Note in spec 004 that its FR-005 is superseded.

## Validation

- [x] T014 Extend tests for profiles, token/client discrimination, and per-command readiness.
- [x] T015 Run tests, shell and Python syntax checks, CLI help, and installer failure-path simulations.
- [x] T016 Record implementation and validation in progress history and update handoff.
