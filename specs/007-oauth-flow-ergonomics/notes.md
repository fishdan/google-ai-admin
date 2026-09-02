# Field Notes: Onboarding a Second Workspace Organization

**Date**: 2026-09-02
**Context**: Dogfooding the `--profile` flag from `005` by adding a real second Workspace organization (`people4liberty.org`) alongside the existing one. Eleven distinct problems surfaced. They are recorded here because most were invisible from the code and only appeared during a real first-run.

## Blocking defects

### N1 — Profiles separated tokens but not OAuth clients

`005` gave each profile its own token, but `.secrets` still accepted exactly one OAuth client. A Desktop client with Audience **Internal** only accepts consent from users inside its own organization, so a second organization could not authorize at all. The only workaround was an External client with a seven-day refresh-token expiry — the configuration `005` documents as the one to avoid.

**Resolved by**: `006-per-profile-oauth-clients`.

### N2 — A profile client under Google's download name broke the default profile

The second organization's client was saved with Google's own filename (`client_secret_<id>.apps.googleusercontent.com.json`). That is not recognized as profile-owned, so it counted as a *second default* client and the previously working default profile began failing with "More than one OAuth client JSON is in .secrets". A working single-tenant setup was broken by adding a second tenant's file.

**Resolved by**: the `client_secret-<profile>.json` convention and `_is_profile_client()` in `006`, plus explicit README instructions to rename on arrival.

### N3 — Downloaded credentials arrive world-readable

A file copied from the Windows filesystem landed as mode `644`. The readiness gate correctly rejects that, but nothing in the flow sets the mode, so every user must know to run `chmod 600`.

**Partially resolved**: the README snippet now includes `chmod 600`. Setting the mode automatically on first use remains open.

### N4 — `xdg-open` fails under WSL

WSL has no Linux browser, so the CLI printed fourteen "not found" lines and left the user to copy a long URL by hand.

**Resolved by**: `register_host_browser()` in `007`, which registers the Windows browser when running under WSL and `BROWSER` is unset.

### N5 — Copying the authorization URL by hand truncated it

The URL wrapped across terminal lines; the copy captured only part of it. Google returned `Error 400: invalid_scope` with the invalid scope shown as the truncated string `https://www.googleapi`. The error names a scope problem, which is misleading — the scopes were correct.

**Resolved by**: N4's fix removing the manual copy entirely.

### N6 — The five-minute timeout was too short and not adjustable

`timeout_seconds=300` was hardcoded. A real sign-in — password, second factor, reading the consent screen, and any diagnosis in between — exceeded it three times in a row.

**Resolved by**: `GOOGLE_OAUTH_TIMEOUT` with a 15-minute default in `007`.

### N7 — A timeout escaped as a raw traceback

`run_local_server` raises `WSGITimeoutError` on timeout. That class subclasses `AttributeError`, which `main()` does not catch, so the user saw an unhandled traceback rather than an explanation. This was found by reading the library after a user challenged the diagnosis — the first fix written for N6 guarded on `credentials is None`, which the library never returns and which would never have fired.

**Resolved by**: catching `WSGITimeoutError` and converting it to a `RuntimeError` with recovery instructions.

## Safety defects

### N8 — A dead callback exposed an authorization code with no warning

When the callback server has exited, the browser shows a bare `http://localhost:<port>/?...&code=...` page. Nothing on screen indicates that string is credential material. During this session the user pasted a live authorization code into the AI conversation — exactly what Constitution §XVI and the README forbid.

The code was never redeemed: no token existed, the CLI had exited, and nothing was listening on the port. It was single-use, expired within roughly ten minutes, and could not be exchanged without the client secret, which never left the machine. No rotation was performed.

**Resolved by**: `007` printing a do-not-share warning with the authorization URL, and a timeout message that names the leftover URL as an authorization code and says to close the tab.

### N9 — Readiness output briefly printed the client filename

While implementing `006`, the readiness line was changed to print the resolved client filename. Under Google's default naming that filename embeds the OAuth client ID. Caught in self-review before commit; the profile name in the header already disambiguates.

**Resolved by**: removing the filename, with a test asserting it stays out of the output.

## Process defects

### N10 — A false "still running" diagnosis, twice

`pgrep -f 'google_workspace_admin.py'` matched the diagnostic shell command itself, so the assistant twice reported the CLI as alive when no such process existed. This sent the user to a browser page that could not possibly work. Process checks must exclude the checking command — `ps -eo args | grep -E '[.]venv/bin/python google_workspace_admin'` was used afterward.

### N11 — Documentation referenced a file that is not in the repository

The README's Chrome DevTools MCP section describes `chrome-debug.bat` as "the repository's optional `chrome-debug.bat`". No such file is tracked. Separately, the DevTools MCP is configured only in `~/.codex/config.toml`, so it is unavailable to other AI clients working in this repository despite the README presenting it as a project capability.

**Open**: neither is addressed by `007`.

## Outcome

Authorization for the second organization completed at 14:38 with exactly one scope granted (`admin.directory.user.readonly`), a refresh token present, and the token at mode `600`. The default profile was unaffected throughout.
