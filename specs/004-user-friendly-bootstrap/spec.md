# Feature Specification: User-Friendly Google Workspace Bootstrap

**Feature Branch**: `004-user-friendly-bootstrap`
**Created**: 2026-09-02
**Status**: Implemented
**Input**: Request for a one-command FishDev-style setup and a readiness gate for AI-driven Google Workspace work.

## Purpose

This repository provides a framework in which a user can ask their AI assistant to perform approved work in Google Workspace, with the tools and Google authorization required for that work. The first-run experience must make that purpose understandable to a nontechnical user while keeping credentials local and least-privileged.

## User Scenarios & Testing

### User Story 1 - One-command installation (Priority: P1)

As a nontechnical Workspace user, I want one documented command that installs the framework and its dependencies so that I can get started without knowing Python or Git setup.

**Acceptance Scenarios**

1. Given a supported Unix-like machine with `curl`, `git`, and Python 3, when the user runs the published installer command, then the repository is available in a predictable local directory, dependencies are installed in an isolated virtual environment, and the installer explains the next action.
2. Given an existing checkout, when the user runs the installer from its root, then setup uses that checkout and does not overwrite secret files.
3. Given a missing prerequisite or a failed download, when installation runs, then it stops safely with a plain-language remediation message.

### User Story 2 - Readiness gate (Priority: P1)

As a user, I want a readiness check to tell me exactly what is missing before I ask the AI to use Workspace tools.

**Acceptance Scenarios**

1. Given a fresh install, when the readiness check runs, then it reports missing OAuth client credentials, missing authorization, required scopes, and required dependency state without exposing secret contents.
2. Given a valid Desktop OAuth client and authorized token, when the check runs, then it confirms the local secret files, token scopes, and dependency imports and exits successfully.
3. Given a token missing one required scope, when the check runs, then it identifies the missing scope and explains that reauthorization is required.

### User Story 3 - Purpose-specific guidance (Priority: P1)

As a user or AI assistant, I want the constitution, startup guide, and README to describe this repository's Google Workspace assistant purpose so that future work stays within the correct tool, permission, and safety boundaries.

**Acceptance Scenarios**

1. Given a new AI session, when startup guidance is read, then it identifies Google Workspace assistance, local secrets, least privilege, and user confirmation for state-changing actions as the governing context.
2. Given a contributor proposes unrelated generic FishDev work, when the repository guidance is consulted, then the scope boundary is clear.

## Functional Requirements

- **FR-001**: The repository MUST provide a root `install.sh` suitable for a `curl -fsSL URL | bash` invocation.
- **FR-002**: The installer MUST support an existing checkout and a fresh install destination, MUST be idempotent for non-secret files, and MUST never print or overwrite secret contents.
- **FR-003**: The installer MUST verify required local prerequisites before making setup changes.
- **FR-004**: The CLI MUST provide a noninteractive readiness command with a nonzero exit status when required setup is incomplete.
- **FR-005**: The readiness command MUST validate Python dependencies, `.secrets` directory permissions, exactly one Desktop OAuth client JSON, token presence, and all scopes declared in the tool. *(Superseded by `005-installer-hardening` FR-010: scopes are now validated per command, because commands request only the scopes they use.)*
- **FR-006**: Diagnostics MUST identify the failed gate and remediation without displaying credential JSON, OAuth tokens, authorization codes, or secret values.
- **FR-007**: The README MUST lead with the repository purpose and one-command install path, then explain the human steps for Google Cloud APIs, consent, OAuth, and AI use.
- **FR-008**: Repository guidance MUST preserve read-only defaults, least privilege, and explicit confirmation before mutations.
- **FR-009**: The installer and readiness check MUST be usable without network access after dependencies and repository files are present, except for the user's explicit Google authorization/API actions.

## Non-goals

- Automatically creating Google Cloud projects, enabling APIs, configuring OAuth consent, or granting Workspace permissions.
- Storing credentials in the repository, shell history beyond the command itself, or an AI conversation.
- Unattended service-account/domain-wide-delegation setup.
- Granting broader Google scopes than the current read-only workflows require.

## Success Criteria

- **SC-001**: A nontechnical user can install the local framework with one copyable command and receive a clear next step.
- **SC-002**: A readiness check distinguishes installation readiness from Google authorization readiness in under one screen of output for the common case.
- **SC-003**: A reviewer can identify every required local secret file and Google scope from the README and readiness output.
- **SC-004**: Automated tests cover success and representative missing/invalid secret states without using real credentials.
