# Implementation Plan: Per-Profile OAuth Clients

**Spec**: `spec.md`
**Branch**: `006-per-profile-oauth-clients`

## Approach

`005` established the pattern: a profile owns a file whose name encodes the profile. Clients follow tokens.

- Tokens: `token.json` (default), `token-<profile>.json` (named).
- Clients: any single non-token JSON (default), `client_secret-<profile>.json` (named).

The dash prefix `client_secret-` is what marks a file as profile-owned. Google's downloaded clients are named `client_secret_<id>.apps.googleusercontent.com.json` with an underscore, so a real download is never mistaken for a profile client.

`005` fixed exactly this class of bug for tokens: a new per-profile file silently became a second "client" and tripped the ambiguity error. The same trap exists here in reverse, so `_is_profile_client()` joins `_is_token_file()` as an exclusion in default-profile discovery. Both predicates are shared by client discovery and the readiness check so the two can never disagree.

`client_secret_path()` gains a `profile` argument and, for named profiles, resolves deterministically and raises with the expected path rather than globbing. Failing before `InstalledAppFlow` is constructed keeps a missing file from opening a browser.

`check_setup()` gains a `profile` argument, replaces its inline client glob with a call to `client_secret_path()`, and names the profile in its header so output from two profiles is distinguishable.

## Files

- `google_workspace_admin.py` — profile-aware client resolution, exclusion predicate, readiness plumbing.
- `tests/test_setup.py` — profile client resolution, missing-client error, default-profile exclusion, unchanged single-client behavior.
- `README.md` — a second-organization walkthrough and the client naming convention.

## Validation

- `python3 -m unittest discover -s tests -v`
- `py_compile`, CLI `--help`, live `check-setup` for the default profile (must stay green)
- Fixture runs for a named profile with and without its client file

## Risks

- A user who named their only client `client_secret-something.json` would have it treated as a profile client, leaving the default profile with none. The readiness message names the expected default condition, and the README documents the convention.
