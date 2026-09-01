# Feature Specification: List Workspace Users and Groups

**Feature Branch**: `main`
**Created**: 2026-09-01
**Status**: Implemented

## User Scenarios & Testing

### User Story 1 - List users (Priority: P1)

As a Workspace administrator, I want to list the users in my production Workspace so that I can inspect the directory from the CLI.

**Acceptance Scenarios**:

1. Given valid local OAuth credentials, when the administrator runs the user-list command, then the CLI authorizes the account if needed and displays each user’s primary email and full name.
2. Given a valid token with insufficient permission, when the command runs, then the CLI reports an actionable authorization error without printing credential contents.

### User Story 2 - List groups (Priority: P1)

As a Workspace administrator, I want to list the groups in my production Workspace so that I can inspect group membership containers from the CLI.

**Acceptance Scenarios**:

1. Given valid local OAuth credentials, when the administrator runs the group-list command, then the CLI displays each group’s email and name.
2. Given no groups are available, when the command runs, then the CLI reports that no groups were found.

## Functional Requirements

- FR-001: The CLI MUST use OAuth user authorization with the local Desktop client configuration.
- FR-002: The CLI MUST request read-only user and group directory permissions only.
- FR-003: The CLI MUST store the resulting refresh token only under the local `.secrets` directory.
- FR-004: The CLI MUST paginate through all available users and groups.
- FR-005: The CLI MUST provide separate commands for users and groups.
- FR-006: The CLI MUST avoid printing client secrets, access tokens, or refresh tokens.

## Assumptions

- The administrator has enabled the Admin SDK Directory API in the Google Cloud project.
- The OAuth consent screen is configured for the production Workspace organization.
- The local credential JSON is an installed/desktop OAuth client file in `.secrets`.

## Success Criteria

- SC-001: An administrator can complete first-time authorization and obtain a directory listing in one CLI invocation.
- SC-002: Subsequent invocations reuse the local token without requiring repeated authorization while it remains valid.
- SC-003: User and group listings contain all pages returned by the Directory API.
