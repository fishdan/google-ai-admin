# Google AI Admin

Google AI Admin is a framework for helping a Google Workspace administrator use an AI assistant to do approved work in their Workspace. It gives the assistant local, explicit Google tools and permissions, while keeping credentials on the user's computer and using the narrowest scopes needed by each workflow.

This repository currently provides read-only tools for:

- Listing Workspace users
- Listing Workspace groups
- Inspecting Gmail filters and forwarding addresses

The first milestone is read-only Workspace inspection. Changes to Workspace data require a separate workflow and confirmation. Never commit credentials or paste them into an AI chat.

## Quick start

On macOS, Linux, WSL, or another Unix-like terminal with Git and Python 3.10+, run:

```bash
curl -fsSL https://raw.githubusercontent.com/fishdan/google-ai-admin/main/install.sh | bash
```

The installer creates an isolated environment, installs the tools, and runs a readiness check. It does not create Google permissions or upload credentials.

Where it installs:

- By default, a fresh install goes to `~/.google-ai-admin`.
- If you run the command from the root of a checkout you already cloned, setup uses that checkout instead.
- To choose the location yourself, set `GOOGLE_AI_ADMIN_DIR`:

  ```bash
  curl -fsSL https://raw.githubusercontent.com/fishdan/google-ai-admin/main/install.sh \
    | GOOGLE_AI_ADMIN_DIR=~/projects/google-ai-admin bash
  ```

Note that running the installer from an empty directory does **not** install into it; that directory is not a checkout, so the default location is used. The installer prints `Installed to: <path>` when it finishes — use that path for every command below.

On Debian and Ubuntu, Python ships without the `venv` module. If the installer stops and asks for it, run `sudo apt install python3-venv` and run the installer again.

After the Google Cloud steps below, verify setup with:

```bash
cd ~/.google-ai-admin   # or the path the installer printed
.venv/bin/python google_workspace_admin.py check-setup
```

When the check says `Ready`, your AI assistant can use the documented Workspace commands.

## Prerequisites

- A Google Workspace domain
- A Workspace administrator account
- A Google Cloud project associated with that Workspace
- Python 3.10 or newer

## 1. Create or select a Google Cloud project

Open the [Google Cloud Console](https://console.cloud.google.com/), select an existing project, or create a new one. Record the project ID; you will use it when enabling APIs.

## 2. Configure the OAuth consent screen

In the Cloud Console:

1. Open **Google Auth Platform**.
2. Under **Branding**, click **Get started** if the platform is not configured.
3. Enter an application name, support email, and developer contact email.
4. Under **Audience**, select **Internal** when the tool is only for users in your Workspace organization.
5. Finish and save the configuration.

### Why the audience choice matters

The `admin.directory.*` scopes this tool uses are **restricted scopes**, and Google treats them differently depending on the audience:

- **Internal** — available when the Cloud project belongs to the same Workspace organization as the account you will authorize. Consent applies only to users in that organization, refresh tokens do not expire on a fixed schedule, and no Google review is required. This is the recommended path for an administrator.
- **External** — left in **Testing** status, refresh tokens for restricted scopes expire after **seven days**, so you must reauthorize every week. Moving an External client to **Production** requires passing a Google security assessment, which is a lengthy process and is not worth it for a local admin tool.

If **Internal** is not offered, the Cloud project is not in the target Workspace organization. Create the project inside the Workspace whose data you intend to inspect, then create the Desktop client there. That single choice avoids both the seven-day expiry and the security assessment.

## 3. Create the Desktop OAuth client

1. Open **Google Auth Platform → Clients** (or **APIs & Services → Credentials** in the older console layout).
2. Click **Create Client** or **Create credentials → OAuth client ID**.
3. Select application type **Desktop app**.
4. Name it something recognizable, such as `Workspace Admin CLI`.
5. Download the JSON file.

Place the downloaded file in the installed checkout's `.secrets` directory. Renaming it is recommended. The tool only reads `.secrets` next to `google_workspace_admin.py`, so change into the install directory first:

```bash
cd ~/.google-ai-admin   # or the path the installer printed
mkdir -p .secrets && chmod 700 .secrets
mv ~/Downloads/client_secret_*.json .secrets/client_secret.json
chmod 600 .secrets/client_secret.json
```

The CLI accepts one OAuth client JSON file with any filename, but it must be the only non-token `.json` file in `.secrets`.

## 4. Enable the required APIs

For user and group listings, enable **Admin SDK API**. For Gmail filter and forwarding inspection, also enable **Gmail API**.

You can find both under **APIs & Services → Library**. Direct links, after replacing `<PROJECT_ID>`, are:

```text
https://console.cloud.google.com/apis/library/admin.googleapis.com?project=<PROJECT_ID>
https://console.cloud.google.com/apis/library/gmail.googleapis.com?project=<PROJECT_ID>
```

If the CLI reports that an API has not been used or is disabled, open the corresponding link, click **Enable**, wait briefly for propagation, and retry.

## 5. Install the local Python environment

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

If `python3 -m venv` fails on Debian or Ubuntu, install `python3-venv` (`sudo apt install python3-venv`), delete any partial `.venv` directory, and run the commands again.

The virtual environment and all secret files are excluded from Git.

The readiness gate checks that `.secrets` is private, exactly one valid Desktop OAuth client is present, the generated token exists and is private, and which commands the token's scopes authorize. It does not print credential values or contact Google.

A partially authorized install looks like this — the check passes, and names exactly what each unauthorized command is waiting for:

```text
✓ Python dependency: google-api-python-client
✓ Python dependency: google-auth-oauthlib
✓ Private secrets folder: .secrets
✓ Desktop OAuth client: present and private
✓ Google authorization: token present and private (token.json)

Command authorization:
  - inspect-gmail-routing: ready
  - list-groups: not authorized
      missing scope: https://www.googleapis.com/auth/admin.directory.group.readonly
  - list-users: not authorized
      missing scope: https://www.googleapis.com/auth/admin.directory.user.readonly

Ready: local tools and Google authorization are configured.
```

`check-setup` exits `0` when at least one command is authorized and `2` when required setup is missing, so it is safe to use as a gate in a script.

## 6. Authorize the administrator account

Run one of the CLI commands below. On first use, the CLI prints a Google authorization URL. Copy that URL into a browser, sign in as `<ADMIN_EMAIL>`, and approve the requested read-only permissions.

```bash
.venv/bin/python google_workspace_admin.py list-users
```

The resulting OAuth token is stored locally as `.secrets/token.json` with restrictive permissions. Later runs reuse that token.

### Each command requests only the scopes it uses

| Command | Scope requested |
| --- | --- |
| `list-users` | `admin.directory.user.readonly` |
| `list-groups` | `admin.directory.group.readonly` |
| `inspect-gmail-routing` | `gmail.settings.basic` |

Consent asks for the scopes of the command you ran, plus any scope your token already holds, so authorizing a new command never revokes an earlier one. An account with Gmail access but no directory role can therefore use `inspect-gmail-routing` without being blocked by admin scopes it will never be granted.

`check-setup` reports readiness per command, so a token that covers some commands and not others is reported accurately rather than as a blanket failure.

### Managing more than one Workspace

Use `--profile` to keep each tenant's authorization separate:

```bash
.venv/bin/python google_workspace_admin.py list-users --profile clientA
.venv/bin/python google_workspace_admin.py list-users --profile clientB
.venv/bin/python google_workspace_admin.py check-setup --profile clientA
```

Each named profile stores its own token at `.secrets/token-<profile>.json`, so signing into one tenant does not overwrite another. Omitting `--profile` uses the default `.secrets/token.json`. Profile names accept letters, digits, dots, dashes, and underscores.

#### Adding a second Workspace organization

A profile in a **different** Workspace organization also needs its own OAuth client. An Internal client only accepts consent from users inside its own organization, so the second organization cannot reuse the first one's client — and downgrading to External would reintroduce the seven-day expiry described above.

Give the profile its own client by saving that organization's downloaded Desktop client as `client_secret-<profile>.json`:

1. In the **second organization's** Google Cloud Console, create or select a project that belongs to that Workspace.
2. Configure the consent screen there with Audience → **Internal**, for the reasons in [Why the audience choice matters](#why-the-audience-choice-matters).
3. Enable the **Admin SDK API**, and the **Gmail API** if you will inspect Gmail routing.
4. Create a **Desktop app** OAuth client and download its JSON.
5. Save it into the existing install, named for the profile:

   ```bash
   cd ~/.google-ai-admin   # or the path the installer printed
   mv ~/Downloads/client_secret_*.json .secrets/client_secret-clientB.json
   chmod 600 .secrets/client_secret-clientB.json
   .venv/bin/python google_workspace_admin.py check-setup --profile clientB
   ```

6. Authorize from your own terminal, signing in as an administrator of that organization:

   ```bash
   .venv/bin/python google_workspace_admin.py list-users --profile clientB
   ```

The default profile keeps using its single unnamed client file, so an existing single-Workspace install is unaffected. Only files named `client_secret-<profile>.json` are treated as profile clients; Google's downloaded name uses an underscore (`client_secret_<id>...json`) and is never mistaken for one.

## 7. List Workspace users and groups

```bash
.venv/bin/python google_workspace_admin.py list-users
.venv/bin/python google_workspace_admin.py list-groups
```

The output contains directory email addresses and display names. The commands follow pagination and list all results.

## 8. Inspect Gmail filters and forwarding

```bash
.venv/bin/python google_workspace_admin.py inspect-gmail-routing
```

This displays Gmail filter criteria/actions and configured forwarding addresses. It does not read email messages.

For a Google Voice forwarding workflow, verify that:

1. A filter matches the expected Google Voice sender or search query.
2. The filter action forwards to the intended group address, such as `<GROUP_ADDRESS>`.
3. The forwarding address is marked `accepted` or otherwise verified.
4. Group membership and member delivery settings allow the message to reach the intended recipients.

This confirms the configuration, but only an actual test message confirms end-to-end delivery.

## OAuth and localhost troubleshooting

- Do not paste an OAuth callback URL or authorization code into chat. Callback URLs contain temporary authorization material.
- The authorization URL is not the same thing as the `gmail.settings.basic` scope identifier; do not browse directly to the scope identifier.
- Use the newest authorization URL printed by the currently running command. Older URLs expire or belong to a different local callback session.
- The supported Desktop OAuth callback is a loopback `localhost` URL. Do not replace it with an arbitrary private network IP; Google may reject that request as invalid.
- If the browser and CLI run in different environments (for example, a Windows browser and a remote Linux/WSL shell), run the command from the same local environment that owns the repository, or use a local terminal/browser arrangement where the printed `localhost:<PORT>` callback can reach the running CLI.
- If a previous attempt timed out, rerun the command to generate a fresh authorization URL.
- If authorization stops working roughly every seven days, the OAuth client is **External** and still in **Testing**. Refresh tokens for restricted scopes expire on that schedule; see [Why the audience choice matters](#why-the-audience-choice-matters).
- If a command reports a missing scope, just run that command. It requests the scope it needs and keeps the permissions the token already holds; there is no need to delete the token first.
- If `check-setup` reports that authorization is not complete on an install that was working, confirm the `--profile` value. Each profile has its own token, and omitting `--profile` uses the default one.

## Security notes

- Keep `.secrets/client_secret.json` and every `.secrets/token*.json` file private.
- Do not commit, upload, or paste secret files or OAuth callback URLs.
- Use read-only scopes whenever possible.
- Revoke the app's access from the administrator's Google Account security settings if a token or credential may have been exposed.
- Service-account keys and domain-wide delegation are intentionally not part of this initial setup. Add them only when unattended automation is explicitly required.

## Development

The project follows the repository's SpecKit workflow. Every change starts from a specification in `specs/`:

| Specification | Subject |
| --- | --- |
| `specs/001-list-users-groups/` | Read-only Directory listing CLI |
| `specs/002-workspace-admin-foundation/` | Initial Workspace admin milestone |
| `specs/003-chrome-devtools-mcp/` | Chrome DevTools MCP integration |
| `specs/004-user-friendly-bootstrap/` | One-command installer and readiness gate |
| `specs/005-installer-hardening/` | Installer preflight, profiles, per-command scopes |

Run the tests, a syntax check, and command help with:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m py_compile google_workspace_admin.py
.venv/bin/python google_workspace_admin.py --help
bash -n install.sh
```

The test suite uses fixture directories and never contacts Google or reads real credentials.

## Chrome DevTools MCP

The project specification for this integration is in `specs/003-chrome-devtools-mcp/`. The official Chrome DevTools MCP server requires Node.js LTS, npm, and current Chrome. The package can be run through `npx`, so no repository dependency is needed.

### Recommended: ask your AI assistant

The exact configuration location differs by operating system and AI client. From the repository root, tell your AI assistant:

> Set up the official Chrome DevTools MCP server for this project. Detect my operating system and AI client, use the current official Chrome DevTools MCP documentation, prefer an isolated browser profile for the first smoke test, configure the MCP server without hard-coded user paths or secrets, restart or reload the client if needed, and verify the connection by opening `https://example.com` and reporting only its title and URL. Explain each OS- and client-specific step, and warn me before connecting to an existing authenticated browser profile.

The assistant should verify Node.js, npm, Chrome, the MCP package, the client configuration, and the smoke test. It should not ask you to paste credentials, cookies, authorization codes, or browser callback URLs into chat.

The recommended initial configuration uses an isolated Chrome profile. This allows the server to launch a clean browser for smoke tests without exposing an existing signed-in browser profile:

```toml
[mcp_servers.chrome-devtools]
command = "npx"
args = ["-y", "chrome-devtools-mcp@latest", "--isolated", "--no-usage-statistics"]
```

For clients that use a TOML configuration, use the equivalent entry above. For clients that use JSON, use the corresponding `mcpServers` structure. The official server command is:

```bash
npx -y chrome-devtools-mcp@latest --isolated --no-usage-statistics
```

Use the AI client's documented MCP configuration method to register that command, then restart or reload the AI client. The server starts the isolated browser when a browser tool is first used. A safe smoke test is to ask the AI to open `https://example.com` and report only the page title and URL.

To connect to an existing Chrome session instead, Chrome must expose a local DevTools endpoint and the MCP configuration must use `--browser-url=http://127.0.0.1:<PORT>`. Keep that endpoint local and protected. If Chrome and the AI client run in different environments such as Windows and WSL, a host gateway address may be required; use the narrowest reachable address and firewall it from the LAN. The repository's optional `chrome-debug.bat` starts an isolated Windows profile on port `9222` and binds to all interfaces, so close that Chrome profile when finished and restrict the Windows Firewall rule if this is used beyond a temporary local test.

Useful checks:

```bash
node --version
npm --version
npx -y chrome-devtools-mcp@latest --version
npx -y chrome-devtools-mcp@latest --help
```

The official project documents additional AI-client configurations and options in its [ChromeDevTools/chrome-devtools-mcp repository](https://github.com/ChromeDevTools/chrome-devtools-mcp), and Chrome provides the [DevTools for agents setup guide](https://developer.chrome.com/docs/devtools/agents/get-started).
