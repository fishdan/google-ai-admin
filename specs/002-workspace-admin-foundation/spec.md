# Feature Specification: Google Workspace Admin CLI Foundation

**Feature Branch**: `002-workspace-admin-foundation`
**Created**: 2026-09-01
**Status**: Ready for review
**Input**: User request to create anonymized documentation and an initial CLI workflow for Workspace administration.

## User Scenarios & Testing

### User Story 1 - Secure local setup (Priority: P1)

As a Workspace administrator, I want clear, reusable setup instructions so that I can configure the tool without exposing credentials.

**Why this priority**: Every later administrative operation depends on a safe and repeatable setup.

**Independent Test**: A new administrator can follow the README using a fresh Cloud project and finish local setup without committing secret files.

**Acceptance Scenarios**:

1. **Given** a Google Cloud project, **when** the administrator follows the setup guide, **then** the required OAuth client and APIs are configured.
2. **Given** local credential files, **when** the administrator checks Git status, **then** credential files and generated tokens are ignored.

### User Story 2 - Inspect Workspace directory (Priority: P1)

As a Workspace administrator, I want to list users and groups from the CLI so that I can inspect directory state quickly.

**Why this priority**: User and group visibility is the base capability for future administrative tools.

**Independent Test**: After authorization, the administrator can run user and group commands and receive complete paginated listings.

**Acceptance Scenarios**:

1. **Given** valid administrator authorization, **when** the user-list command runs, **then** it displays user email addresses and names.
2. **Given** valid administrator authorization, **when** the group-list command runs, **then** it displays group email addresses and names.
3. **Given** an empty directory result, **when** a listing command runs, **then** it reports no results without failing.

### User Story 3 - Verify Gmail routing (Priority: P1)

As a Workspace administrator, I want to inspect Gmail filters and forwarding addresses without reading messages so that I can verify operational routing rules.

**Why this priority**: Routing verification is the first concrete administrative workflow and requires a narrower permission boundary than mail access.

**Independent Test**: After Gmail settings authorization, the administrator can inspect filter criteria, filter actions, and forwarding-address verification states.

**Acceptance Scenarios**:

1. **Given** a filter forwarding matching messages to a group, **when** the routing inspection runs, **then** the matching criteria and destination are displayed.
2. **Given** an unverified forwarding address, **when** the routing inspection runs, **then** its verification state is displayed.
3. **Given** no Gmail message access was granted, **when** the inspection runs, **then** no message content is read or displayed.

## Edge Cases

- An API is disabled or has not finished propagating after enablement.
- The saved token lacks a newly requested scope and requires reauthorization.
- The browser and CLI run in different environments and cannot reach the local OAuth callback.
- Multiple OAuth client JSON files are present in `.secrets`.
- A forwarding address exists but is still pending verification.
- A group has members whose delivery settings prevent receipt.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST document Cloud project, consent-screen, OAuth client, and API setup in anonymized terms.
- **FR-002**: The system MUST keep OAuth client files and generated tokens outside version control.
- **FR-003**: The system MUST authorize a Workspace administrator through an installed-app OAuth flow.
- **FR-004**: The system MUST request read-only directory access for users and groups.
- **FR-005**: The system MUST list all users and groups across paginated API responses.
- **FR-006**: The system MUST request Gmail settings access separately from message access.
- **FR-007**: The system MUST display Gmail filter criteria, actions, forwarding addresses, and verification states without reading message content.
- **FR-008**: The system MUST provide actionable errors for missing credentials, disabled APIs, insufficient scopes, and authorization timeouts.
- **FR-009**: The system MUST document that OAuth callback URLs and authorization codes must not be shared.
- **FR-010**: The system MUST document that group forwarding configuration does not by itself guarantee delivery to every member.

## Key Entities

- **Workspace administrator**: The authorized human account performing read-only administrative inspection.
- **OAuth client**: The local Desktop application credential used to begin authorization.
- **OAuth token**: The local, generated authorization state used for subsequent API calls.
- **Directory user**: A Workspace user record with an email address and display name.
- **Directory group**: A Workspace group with an address, name, and membership/delivery behavior.
- **Gmail filter**: A rule containing message criteria and actions such as forwarding or labeling.
- **Forwarding address**: A destination address with a verification state.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A new administrator can complete setup from the README without receiving or exposing any project-specific secret value.
- **SC-002**: Authorized users can list users and groups with one command each.
- **SC-003**: Listings include all pages returned by the service rather than an arbitrary first-page limit.
- **SC-004**: Gmail routing inspection completes without accessing email message bodies.
- **SC-005**: A reviewer can identify the required APIs, scopes, local files, commands, and recovery steps from the README alone.

## Assumptions

- The administrator has authority to authorize the Workspace and enable APIs in the selected Cloud project.
- Initial use is interactive and local; unattended service-account access is out of scope.
- The first milestone is read-only; mutation commands require separate specifications and explicit review.
- Google Cloud Console labels may change, so the README includes both current and fallback navigation labels where useful.
