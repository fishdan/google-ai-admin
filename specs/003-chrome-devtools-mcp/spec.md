# Feature Specification: Chrome DevTools MCP Integration

**Feature Branch**: `003-chrome-devtools-mcp`
**Created**: 2026-09-01
**Status**: Draft
**Input**: User request to make Chrome DevTools MCP available for this project with AI assistance.

## User Scenarios & Testing

### User Story 1 - Local browser inspection (Priority: P1)

As a developer, I want the AI assistant to connect to a locally running Chrome browser through Chrome DevTools MCP so that it can inspect pages and troubleshoot the browser-based Google Cloud and Workspace setup.

**Why this priority**: A working browser bridge will make OAuth, Cloud Console, and future administrative UI workflows easier to inspect and debug.

**Independent Test**: Start the configured MCP server and Chrome connection, then have the AI inspect a harmless local or public test page and report its title without changing the page.

**Acceptance Scenarios**:

1. **Given** Chrome is running with the supported DevTools connection enabled, **when** the MCP server starts, **then** the AI client can discover its browser inspection tools.
2. **Given** a test page is open, **when** the AI requests the page title and URL, **then** the values are returned without modifying browser state.
3. **Given** Chrome or the MCP server is unavailable, **when** a connection is attempted, **then** the setup reports an actionable error and recovery steps.

### User Story 2 - Safe troubleshooting (Priority: P1)

As a Workspace administrator, I want browser inspection to avoid exposing secrets so that OAuth tokens, credential JSON, and authorization codes remain private.

**Why this priority**: Browser inspection may involve sensitive Cloud Console and account pages, so security boundaries must be explicit before use.

**Independent Test**: Inspect a deliberately sanitized test page and verify that the documented workflow does not request, log, or commit browser cookies, tokens, passwords, or secret files.

**Acceptance Scenarios**:

1. **Given** a page contains a secret-like value, **when** the AI inspects the page, **then** the workflow does not copy that value into repository files or progress logs.
2. **Given** a user asks for a browser mutation, **when** the action could alter account, billing, or Workspace state, **then** the AI requests confirmation before performing it.

### User Story 3 - Reproducible project setup (Priority: P2)

As a contributor, I want the MCP configuration and troubleshooting steps documented in the repository so that another contributor can reproduce the connection with their own AI client.

**Why this priority**: The project supports AI-assisted work across environments, and setup knowledge should not depend on one machine or conversation.

**Independent Test**: A contributor following the documentation can identify prerequisites, configure the MCP server in their AI client, run the smoke test, and remove the configuration cleanly.

**Acceptance Scenarios**:

1. **Given** a fresh checkout, **when** a contributor follows the setup guide, **then** the guide identifies all required software and configuration locations.
2. **Given** a contributor no longer wants the integration, **when** they follow the removal steps, **then** the MCP configuration can be disabled without affecting the CLI or Google credentials.

## Edge Cases

- Chrome is installed but running without the required remote-debugging or DevTools connection mode.
- Another process is using the selected debugging port.
- The AI client supports MCP but does not support this server's transport or configuration format.
- Chrome is logged into a different Google account than the intended administrator.
- A page contains sensitive data, authorization codes, cookies, or credentials.
- The integration is attempted in a remote/containerized environment where the browser is not reachable.
- The MCP package or Chrome version changes its setup requirements.

## Requirements

### Functional Requirements

- **FR-001**: The project MUST document prerequisites and supported environment assumptions for Chrome DevTools MCP.
- **FR-002**: The project MUST provide a reproducible MCP client configuration example without embedding user-specific paths, account identifiers, tokens, or secrets.
- **FR-003**: The integration MUST expose a non-destructive smoke test for browser connectivity.
- **FR-004**: The integration MUST document how to start, stop, diagnose, and remove the MCP connection.
- **FR-005**: The integration MUST clearly distinguish read-only browser inspection from actions that change browser or account state.
- **FR-006**: The integration MUST warn contributors not to inspect or copy credential files, OAuth callback URLs, cookies, passwords, or access tokens.
- **FR-007**: The integration MUST keep MCP configuration portable across supported AI clients where their configuration formats differ.
- **FR-008**: The integration MUST not change Google Workspace data as part of its installation or smoke test.

## Key Entities

- **Chrome session**: The local browser instance made available for inspection.
- **DevTools connection**: The local browser debugging channel used by the MCP server.
- **MCP server**: The process that exposes Chrome inspection capabilities to an AI client.
- **MCP client configuration**: The local AI-client entry that starts or connects to the server.
- **Smoke-test page**: A harmless page used only to verify connectivity and basic inspection.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A contributor can complete setup and run the smoke test in under 10 minutes on a supported local environment.
- **SC-002**: The AI client discovers the MCP tools and retrieves a test page title and URL successfully.
- **SC-003**: The repository contains no user-specific browser paths, account identifiers, authorization URLs, or secrets in the MCP documentation/configuration.
- **SC-004**: A failed connection produces a documented diagnosis path covering Chrome, port, transport, and client configuration issues.
- **SC-005**: Installation and removal leave the existing Google Workspace CLI and `.secrets` contents unchanged.

## Assumptions

- Initial support targets local development, not a shared or unattended browser session.
- The first milestone is inspection and troubleshooting; browser mutations require separate approval and specifications.
- Contributors may use different AI clients, so the repository will document the server concept and client-specific configuration separately.
- Chrome DevTools MCP package and Chrome requirements must be verified against current official documentation during planning.
