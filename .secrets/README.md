# Local Google Workspace credentials

This directory is for local credential files only. Do not paste secret values into chat or commit them to GitHub.

## Preferred initial setup: OAuth desktop client

1. In Google Cloud Console, select or create a project.
2. Enable the Google Workspace Admin SDK APIs needed by the tool.
3. Configure the OAuth consent screen for the intended Workspace audience.
4. Create an OAuth client with application type **Desktop app**.
5. Download the JSON file and place it here as:

   `client_secret.json`

The tool will use this to obtain user-authorized access. The first sign-in will open a browser, and the resulting token should also remain local in this directory.

## Information needed from you

Please provide these non-secret settings in your next message:

- The Google Workspace administrator email address to authorize.
- The Workspace customer ID, if you know it (often starts with `C`).
- Whether access should be limited to a test/sandbox account or your production Workspace.
- Which initial admin task to support first (for example: list users, inspect groups, or audit Drive sharing).

## Alternative: service account

If this will run unattended or across many administrator accounts, we can instead use a service-account JSON key with domain-wide delegation. Do not create or add that key until we explicitly choose this model; service-account keys are high-risk credentials.

## Expected local files

The following are examples and are ignored by Git:

- `client_secret.json` — downloaded OAuth client configuration
- `token.json` — generated local OAuth token, if the tool uses file-based token storage
- `service-account.json` — only if we explicitly choose service-account authentication
