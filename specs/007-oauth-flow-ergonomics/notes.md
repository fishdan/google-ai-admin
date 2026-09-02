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

### N12 — The fix for N4 introduced a worse failure

`register_host_browser()` was first written with `webbrowser.GenericBrowser`, whose `open()` calls `p.wait()`. Chrome does not exit while a window is open, so the CLI blocked inside the browser launch: the authorization URL was never printed and `handle_request()` was never reached, meaning the callback server would not have answered a redirect even if consent had been completed. The user reported it as "Chrome did not open, or I missed it"; the process was in `do_wait` on the browser.

`webbrowser.BackgroundBrowser` returns as soon as the process starts. A test now asserts the registered instance is the non-blocking class.

**Resolved**, with the lesson that a fix for an ergonomics defect can silently disable the mechanism it was meant to help.

### N13 — The browser opened the wrong profile

On a machine with many Chrome profiles, the browser opened whichever profile was last used, and the consent screen was easy to miss among open windows. Authorization now requests a private window (`--incognito`, or `--inprivate` for Edge), which both removes the profile ambiguity and forces an explicit account choice. `GOOGLE_OAUTH_BROWSER_ARGS` overrides it.

### N14 — "Ready" overpromises

`check-setup` reported `Ready` for two profiles whose commands were guaranteed to fail, because the Admin SDK API was not enabled in their Cloud projects. The gate deliberately never contacts Google, which is correct for an offline check, but the word "Ready" implies more than local validity.

**Open**: the wording should distinguish local setup from Google-side configuration, and the per-profile API enable step should be named. No network call should be added.

### N15 — Enabling an API is a cross-organization permission, not a tool capability

Asked whether the stored token removed the need for a browser, the answer is only partly yes: the token authorizes read calls without a browser, but enabling an API is a write to a Cloud project requiring `serviceusage.services.enable` and the `cloud-platform` scope — which would itself need a fresh browser consent and would grant this read-only tool write access to the whole project. `gcloud` is the correct instrument. In practice one org's admin (`dan@people4liberty.org`) could enable its own project but got `PERMISSION_DENIED` on the third organization's project, confirming this is an IAM boundary rather than anything the tool can resolve.

Separately, `gcloud auth login` failed through the identical `xdg-open` browser list under WSL. The defect N4 describes is not unique to this project.

## Outcome

Three organizations are authorized side by side, each with its own Internal OAuth client and its own token at mode `600`, each holding exactly the one read-only scope its command required: the original Workspace (11 users), `people4liberty.org` (4 users), and `home4liberty.org` (1 user). The default profile was unaffected throughout.
