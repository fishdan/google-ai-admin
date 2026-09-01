# Tasks: Chrome DevTools MCP Integration

**Input**: `spec.md`

## Discovery and design

- [x] T001 Verify the current official Chrome DevTools MCP package, transport, supported Chrome versions, and launch requirements.
- [x] T002 Identify the supported AI client configuration locations relevant to this repository.
- [x] T003 Define a localhost-only connection and a safe smoke-test page.

## Implementation

- [x] T004 Add anonymized MCP setup instructions to `README.md`.
- [x] T005 Add a portable example configuration with placeholder paths only.
- [x] T006 Document start, stop, diagnosis, and removal procedures.
- [x] T007 Document security boundaries for browser inspection and account-state mutations.

## Validation

- [x] T008 Start Chrome and the MCP server in a supported local environment.
- [ ] T009 Verify tool discovery from the intended AI client.
- [ ] T010 Run the non-destructive title/URL smoke test.
- [ ] T011 Verify no credentials or user-specific values are present in tracked files.
- [ ] T012 Verify the existing Workspace CLI and `.secrets` files remain unchanged.
