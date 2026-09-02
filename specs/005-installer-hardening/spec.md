# Feature Specification: Installer Hardening and Per-Command Authorization

**Feature Branch**: `005-installer-hardening`
**Created**: 2026-09-02
**Status**: Implemented
**Input**: First-time Linux install report (Ubuntu, Python 3.13.7) covering three installer/README papercuts, two multi-tenant limitations, and a missing restricted-scope explanation.

## Purpose

The `004-user-friendly-bootstrap` installer was validated on a machine that already had a working checkout and a complete Python toolchain. A first-time install on a clean Ubuntu host exposed failures that the readiness gate cannot report, because the installer aborts before the gate runs. This feature makes a first install survivable, retryable, and discoverable, and removes two authorization limits that block administrators who manage more than one Workspace or who only hold Gmail permissions.

## User Scenarios & Testing

### User Story 1 - The installer survives a missing venv module (Priority: P1)

As a first-time user on Debian or Ubuntu, I want the installer to tell me what to install when `python3 -m venv` cannot work, so that I am not left with a raw Python traceback and a broken half-built environment.

**Acceptance Scenarios**

1. Given a Python interpreter without `ensurepip`, when the installer runs, then it stops during preflight with a plain-language message naming the package to install, and creates no virtual environment.
2. Given a previous run that left an unusable `.venv`, when the installer runs again, then it removes that incomplete environment and rebuilds it, so the retry succeeds.
3. Given virtual environment creation fails for any other reason, when the installer stops, then the partial `.venv` is removed so the next run is not poisoned.

### User Story 2 - The install location is always visible (Priority: P1)

As a user who ran the installer from a directory I created for the project, I want to know where the repository actually landed.

**Acceptance Scenarios**

1. Given any successful or partially successful run, when the installer finishes, then its final output states the absolute install directory.
2. Given a user who wants a specific location, when they read the README quick start, then `GOOGLE_AI_ADMIN_DIR` is documented with an example.

### User Story 3 - Credential placement lands in the right directory (Priority: P1)

As a user following README step 3 immediately after a `curl | bash` install, I want the commands to place the OAuth client where the tool reads it.

**Acceptance Scenarios**

1. Given the README credential snippet, when a user copies it verbatim in any working directory, then the file is written into the installed checkout's `.secrets`, not a stray directory.

### User Story 4 - More than one Workspace (Priority: P2)

As an administrator of several Workspace tenants, I want each tenant's authorization stored separately so that signing into one does not overwrite another.

**Acceptance Scenarios**

1. Given `--profile <name>`, when a command authorizes, then the token is written to `.secrets/token-<name>.json` and the default profile's `.secrets/token.json` is untouched.
2. Given a profile name containing a path separator or other unsafe character, when a command runs, then it is rejected before any file is written.
3. Given several profile tokens in `.secrets`, when the OAuth client file is located, then no token file is mistaken for a client file.

### User Story 5 - Only the scopes a command needs (Priority: P2)

As a user whose account only has Gmail permissions, I want `inspect-gmail-routing` to request Gmail settings access alone, so that consent is not blocked by directory scopes the command never uses.

**Acceptance Scenarios**

1. Given no token, when `inspect-gmail-routing` runs, then consent requests only `gmail.settings.basic`.
2. Given a token that already grants the directory scopes, when a Gmail command triggers a new consent, then the requested scope set is the union of the granted scopes and the newly required scope, so existing authorization is preserved.
3. Given a token that already grants a command's scopes, when that command runs, then no new consent flow starts.
4. Given a token granting only some commands' scopes, when the readiness check runs, then it reports per-command readiness and names the command that needs reauthorization.

### User Story 6 - Restricted scopes are explained (Priority: P2)

As a user configuring the OAuth consent screen, I want to know why the audience choice matters before I make it.

**Acceptance Scenarios**

1. Given README step 2, when a user reads it, then it explains that `admin.directory.*` are restricted scopes, that an External client left in Testing issues refresh tokens that expire after seven days, that moving External to Production requires a Google security assessment, and that creating the Desktop client inside the target Workspace's own Cloud project with Audience → Internal avoids both.

## Functional Requirements

- **FR-001**: The installer MUST verify that the selected interpreter can create a virtual environment (`ensurepip` importable) during preflight, before it modifies the project directory, and MUST name the remediation package on failure.
- **FR-002**: The installer MUST remove an incomplete `.venv` before creating one, and MUST remove a `.venv` it failed to create, so that any failed run is retryable.
- **FR-003**: The installer MUST print the absolute install directory as part of its closing output on every completed run.
- **FR-004**: The README quick start MUST document `GOOGLE_AI_ADMIN_DIR` and the default install location.
- **FR-005**: README credential placement instructions MUST be anchored to the installed checkout.
- **FR-006**: The CLI MUST accept `--profile <name>`, storing authorization at `.secrets/token-<name>.json`, with the default profile continuing to use `.secrets/token.json`.
- **FR-007**: Profile names MUST be validated against a conservative character set and rejected before any filesystem write.
- **FR-008**: OAuth client discovery MUST exclude every token file, including profile tokens.
- **FR-009**: Each command MUST declare the scopes it needs, and authorization MUST request only those scopes, unioned with scopes an existing token already grants.
- **FR-010**: The readiness check MUST report readiness per command, MUST pass when at least one command is authorized, and MUST name the missing scope and affected command otherwise.
- **FR-011**: The readiness check MUST continue to avoid printing credential contents and MUST NOT contact Google.
- **FR-012**: The README MUST explain the restricted-scope consequences of the OAuth audience choice.

## Non-goals

- Changing the Google APIs called, or adding any write scope.
- Automatic migration of an existing `.secrets/token.json` into a named profile.
- Installing system packages on the user's behalf.
- Windows-native (non-WSL) installer support.
- Service-account or domain-wide-delegation authorization.
