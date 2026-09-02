# Feature Specification: Authorization Flow Ergonomics and Safety

**Feature Branch**: `007-oauth-flow-ergonomics`
**Created**: 2026-09-02
**Status**: Implemented
**Input**: Three failures observed while authorizing a second Workspace organization on WSL.

## Purpose

Authorizing a profile failed three times in a row for reasons unrelated to scopes, clients, or Google configuration:

1. **The five-minute timeout expired** while the user was signing in and reading the consent screen. The hardcoded `timeout_seconds=300` is not adjustable, and each expiry silently kills the local callback server.
2. **`xdg-open` failed** because WSL has no Linux browser installed, so the CLI printed a wall of "not found" errors and left the user to copy a very long URL by hand. One such copy was truncated at a line wrap and produced `Error 400: invalid_scope`.
3. **A dead callback exposed credential material.** When the callback server is gone, the browser shows a bare `http://localhost:<port>/?...&code=...` URL. Nothing on screen says that string is an authorization code, and the user pasted it into a chat — precisely what the constitution forbids.

Each is a first-run defect in a tool whose stated purpose is to be usable by a nontechnical administrator.

## User Scenarios & Testing

### User Story 1 - Enough time to sign in (Priority: P1)

As a user signing into a Workspace account with a password and second factor, I want enough time to complete consent.

**Acceptance Scenarios**

1. Given no configuration, when authorization starts, then the callback server waits substantially longer than five minutes.
2. Given `GOOGLE_OAUTH_TIMEOUT` is set, when authorization starts, then that value is used.
3. Given a non-numeric or non-positive `GOOGLE_OAUTH_TIMEOUT`, when authorization starts, then the tool fails with a clear message rather than an unhandled error.

### User Story 2 - The browser opens itself under WSL (Priority: P1)

As a WSL user with no Linux browser, I want the CLI to open my Windows browser rather than fail through a list of missing ones.

**Acceptance Scenarios**

1. Given WSL and no `BROWSER` set, when authorization starts and a Windows browser is present, then that browser is used to open the authorization URL.
2. Given `BROWSER` is already set, when authorization starts, then the user's choice is respected.
3. Given a non-WSL system, when authorization starts, then browser selection is unchanged.
4. Given WSL and no Windows browser found, when authorization starts, then the URL is still printed and the flow still waits.

### User Story 3 - The user is told what not to share (Priority: P1)

As a user, I want to be warned that the authorization URL and anything the browser returns are credential material.

**Acceptance Scenarios**

1. Given authorization starts, when the URL is printed, then a warning states that neither the URL nor the resulting callback address may be pasted into chat, email, or a ticket.
2. Given the callback server times out, when the tool exits, then it explains that a URL left in the browser contains an authorization code, must not be shared, and that rerunning is the correct recovery.

## Functional Requirements

- **FR-001**: The callback timeout MUST default to a value substantially greater than five minutes and MUST be overridable by `GOOGLE_OAUTH_TIMEOUT`.
- **FR-002**: An invalid `GOOGLE_OAUTH_TIMEOUT` MUST produce a clear setup error.
- **FR-003**: Under WSL, when `BROWSER` is unset, the CLI MUST attempt to open a Windows browser, and MUST fall back silently to printing the URL.
- **FR-004**: An explicit `BROWSER` setting MUST always win, and non-WSL behavior MUST be unchanged.
- **FR-005**: The CLI MUST warn, at the point of printing the authorization URL, that the URL and callback are credential material that must never be shared.
- **FR-006**: A timeout MUST produce a message explaining the exposure and the recovery, not a bare stack trace or silent exit.
- **FR-007**: No warning or diagnostic may itself print an authorization code, token, or client secret.
- **FR-008**: The registered browser MUST NOT block the callback server. A browser opened with a class that waits for the process to exit prevents the local server from ever handling the redirect.
- **FR-009**: The browser SHOULD open a private window by default so that a machine with many browser profiles does not authorize through whichever profile was last used. `GOOGLE_OAUTH_BROWSER_ARGS` MUST override this, including an empty value to disable it.

## Non-goals

- Installing a browser or any system package.
- Device-code or service-account authorization.
- Changing scopes, profiles, or which APIs are called.
- Detecting or parsing anything the user pastes.
