# Feature Specification: Per-Profile OAuth Clients

**Feature Branch**: `006-per-profile-oauth-clients`
**Created**: 2026-09-02
**Status**: Implemented
**Input**: Dogfooding `005`'s `--profile` flag against a second Workspace organization.

## Purpose

`005-installer-hardening` gave each Workspace profile its own token, but `.secrets` still accepts exactly one OAuth client. That is sufficient only when every profile authorizes against the same client.

It does not hold for the case profiles exist to serve. A Desktop client with Audience **Internal** — the configuration `005` documents as the correct one, because it avoids the seven-day restricted-scope expiry and the Google security assessment — only accepts consent from users inside its own organization. A second Workspace organization therefore requires a second Cloud project and a second Desktop client, and the readiness gate currently rejects that with "More than one OAuth client JSON is in `.secrets`".

Managing two Workspace organizations is impossible today without downgrading to an External client and accepting weekly reauthorization. This feature removes that constraint.

## User Scenarios & Testing

### User Story 1 - A second organization brings its own client (Priority: P1)

As an administrator of two Workspace organizations, I want each profile to use its own Desktop OAuth client so that each organization can keep an Internal client in its own Cloud project.

**Acceptance Scenarios**

1. Given `.secrets/client_secret-<profile>.json`, when a command runs with `--profile <profile>`, then authorization uses that client and writes `.secrets/token-<profile>.json`.
2. Given a named profile whose client file is absent, when a command runs, then it fails naming the exact expected path, before any browser flow starts.
3. Given both a default client and one or more profile clients in `.secrets`, when the default profile runs, then the profile clients are not counted as additional default clients.

### User Story 2 - Existing installs are unaffected (Priority: P1)

As an existing single-Workspace user, I want my current setup to keep working untouched.

**Acceptance Scenarios**

1. Given a single OAuth client under any filename and no profile clients, when any command runs without `--profile`, then behavior is identical to `005`.
2. Given two non-profile client files, when the readiness check runs, then it still reports the ambiguity rather than guessing.

### User Story 3 - Readiness reporting per profile (Priority: P2)

As a user, I want `check-setup --profile <name>` to validate that profile's own client and token.

**Acceptance Scenarios**

1. Given `--profile <name>`, when the readiness check runs, then it validates `client_secret-<name>.json` and `token-<name>.json`, and names the profile in its output.
2. Given a profile client that is present but not a Desktop client, or not private, when the check runs, then it reports that specific problem without printing the file's contents.

## Functional Requirements

- **FR-001**: A named profile MUST resolve its OAuth client to `.secrets/client_secret-<profile>.json`.
- **FR-002**: A missing profile client MUST fail with the exact expected path, before any authorization flow begins.
- **FR-003**: Default-profile client discovery MUST exclude profile client files as well as token files.
- **FR-004**: The default profile MUST retain `005` behavior: exactly one non-token, non-profile client JSON under any filename.
- **FR-005**: The readiness check MUST accept a profile and validate that profile's client and token, naming the profile in its output.
- **FR-006**: Profile names MUST be validated before being used to build any client path, as they already are for tokens.
- **FR-007**: No diagnostic may print credential contents.

## Non-goals

- Copying, generating, or downloading OAuth clients on the user's behalf.
- Cross-organization delegation, service accounts, or domain-wide delegation.
- Automatic discovery of which profile belongs to which domain.
- Migrating an existing default client into a named profile.
