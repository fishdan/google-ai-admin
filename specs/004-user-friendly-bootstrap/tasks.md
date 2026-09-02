# Tasks: User-Friendly Google Workspace Bootstrap

**Input**: `spec.md`

## Specification and guidance

- [x] T001 Create the feature specification and define installation, gate, and scope boundaries.
- [x] T002 Rewrite repository-facing guidance around AI-assisted Google Workspace work.

## Installer and readiness gate

- [x] T003 Add an idempotent `install.sh` supporting curl-pipe installation and existing checkouts.
- [x] T004 Add a `check-setup` CLI command with safe, actionable gate output and exit codes.
- [x] T005 Validate secret directory/file permissions and Desktop OAuth client structure without printing contents.
- [x] T006 Validate token presence and all required OAuth scopes.

## Validation and handoff

- [x] T007 Add tests for passing and failing readiness checks and installer shell validation.
- [x] T008 Run syntax, CLI, test, and secret-exclusion checks.
- [x] T009 Record implementation and validation in progress history and update handoff.
