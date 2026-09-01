# Tasks: Google Workspace Admin CLI Foundation

**Input**: `spec.md`

All tasks below are complete in the implementation currently under review.

## Setup and security

- [x] T001 Add `.secrets` ignore rules for OAuth clients, tokens, and service-account keys.
- [x] T002 Document anonymized Cloud Console and local setup in `README.md`.
- [x] T003 Add a local Python virtual-environment setup using `requirements.txt`.

## OAuth and API access

- [x] T004 Implement installed-app OAuth credential discovery in `google_workspace_admin.py`.
- [x] T005 Store generated tokens under `.secrets` with restrictive file permissions.
- [x] T006 Detect missing requested scopes and force reauthorization.
- [x] T007 Document and handle disabled APIs, insufficient scopes, and callback failures.

## Directory inspection

- [x] T008 Implement paginated user listing.
- [x] T009 Implement paginated group listing.

## Gmail routing inspection

- [x] T010 Implement read-only Gmail filter inspection.
- [x] T011 Implement forwarding-address verification-state inspection.
- [x] T012 Ensure message bodies are never requested or displayed.

## Validation and handoff

- [x] T013 Validate syntax, CLI help, secret exclusion, and local token permissions.
- [x] T014 Validate users and groups against a production Workspace.
- [x] T015 Validate Gmail settings against a production filter configuration.
