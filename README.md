# Google AI Admin

Google AI Admin is a framework for asking an AI assistant to do approved work in your Google Workspace. It gives the assistant local, explicit Google tools and permissions, while keeping credentials on your computer and using the narrowest scopes needed by each workflow.

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

The installer creates an isolated environment, installs the tools, and runs a readiness check. It does not create Google permissions or upload credentials. If you already cloned this repository, run the same command from its root and setup will use that checkout. The default fresh-install location is `~/.google-ai-admin`.

After the Google Cloud steps below, verify setup with:

```bash
cd ~/.google-ai-admin   # or your existing checkout
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

## 3. Create the Desktop OAuth client

1. Open **Google Auth Platform → Clients** (or **APIs & Services → Credentials** in the older console layout).
2. Click **Create Client** or **Create credentials → OAuth client ID**.
3. Select application type **Desktop app**.
4. Name it something recognizable, such as `Workspace Admin CLI`.
5. Download the JSON file.

Create the local secrets directory and place the downloaded file there. Renaming it is recommended:

```bash
mkdir -p .secrets
mv ~/Downloads/client_secret_*.json .secrets/client_secret.json
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

The virtual environment and all secret files are excluded from Git.

The readiness gate checks that `.secrets` is private, exactly one valid Desktop OAuth client is present, the generated token exists, and the token contains every scope used by the current tools. It does not print credential values or contact Google.

## 6. Authorize the administrator account

Run one of the CLI commands below. On first use, the CLI prints a Google authorization URL. Copy that URL into a browser, sign in as `<ADMIN_EMAIL>`, and approve the requested read-only permissions.

```bash
.venv/bin/python google_workspace_admin.py list-users
```

The resulting OAuth token is stored locally as `.secrets/token.json` with restrictive permissions. Later runs reuse that token.

The CLI requests only these scopes:

- `admin.directory.user.readonly`
- `admin.directory.group.readonly`
- `gmail.settings.basic` (only needed for Gmail settings inspection)

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

## Security notes

- Keep `.secrets/client_secret.json` and `.secrets/token.json private.
- Do not commit, upload, or paste secret files or OAuth callback URLs.
- Use read-only scopes whenever possible.
- Revoke the app's access from the administrator's Google Account security settings if a token or credential may have been exposed.
- Service-account keys and domain-wide delegation are intentionally not part of this initial setup. Add them only when unattended automation is explicitly required.

## Development

The project follows the repository's SpecKit workflow. The first feature specification is in `specs/001-list-users-groups/`.

Run a syntax check and view command help with:

```bash
.venv/bin/python -m py_compile google_workspace_admin.py
.venv/bin/python google_workspace_admin.py --help
```

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
