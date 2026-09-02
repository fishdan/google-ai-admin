# Implementation Plan: Installer Hardening and Per-Command Authorization

**Spec**: `spec.md`
**Branch**: `005-installer-hardening`

## Approach

Two independent layers change: the shell installer (User Stories 1-2) and the Python authorization model (User Stories 4-5). README edits (User Stories 2, 3, 6) follow both.

### Installer

Preflight grows one check: `"$PYTHON" -c 'import ensurepip'`. It belongs with the existing interpreter version check so that failure happens before `mkdir .secrets` or any clone-side effect in an existing checkout.

Virtual environment creation becomes conditional and self-cleaning. `.venv` is treated as unusable unless `.venv/bin/python` is executable, which is exactly the state Debian's stub interpreter leaves behind. Removal is scoped to `${PROJECT_DIR}/.venv` after a successful `cd`, never to a path derived from user input.

The closing block prints `Installed to: ${PROJECT_DIR}` on both the ready and not-ready paths.

### Authorization model

`TOKEN_PATH` becomes `token_path(profile)`. The default profile keeps `.secrets/token.json` so existing installs are unaffected; a named profile uses `.secrets/token-<name>.json`.

`client_secret_path()` currently excludes only the literal `token.json`, which would let `token-work.json` be mistaken for a second OAuth client and trip the "more than one client" error. A single `_is_token_file()` predicate replaces the name comparison and is shared by client discovery and the readiness check.

`COMMAND_SCOPES` maps each command to its required scopes. `authorize(scopes, profile)` reuses a token whose granted scopes are a superset of what the command needs. When consent is required, it requests `granted | required`, so authorizing a Gmail command on a directory-authorized token does not silently drop the directory grant.

`main()` currently builds the Admin Directory service even for the Gmail command. Service construction moves under each command branch.

### Readiness check

`check_setup()` gains a per-command scope report. It passes when the local files are valid and at least one command's scopes are granted, and lists any command that needs reauthorization along with the specific missing scope. This supersedes spec 004's FR-005 all-scopes rule, which would now fail every correctly authorized single-purpose install.

## Files

- `install.sh` — preflight check, venv cleanup, install-location output.
- `google_workspace_admin.py` — profile-aware token paths, per-command scopes, argument parsing, readiness reporting, service construction.
- `README.md` — quick start `GOOGLE_AI_ADMIN_DIR`, anchored credential snippet, restricted-scope explanation, profile and scope documentation.
- `tests/test_setup.py` — profile paths, name validation, token/client discrimination, per-command readiness, scope-union behavior.
- `specs/004-user-friendly-bootstrap/spec.md` — note that FR-005 is superseded.

## Validation

- `python3 -m unittest discover -s tests -v`
- `bash -n install.sh` and `shellcheck install.sh` if available
- `python3 -m py_compile google_workspace_admin.py`
- CLI `--help` and `check-setup` against the live local install
- Simulated failure runs for the missing-`ensurepip` and partial-`.venv` paths

## Risks

- The readiness pass criterion loosens from "all scopes" to "at least one command". Mitigated by explicit per-command output so a partially authorized install is never reported as fully capable.
- Scope union means a token can accumulate grants across commands. That matches Google's incremental consent behavior and is visible in the readiness output.
