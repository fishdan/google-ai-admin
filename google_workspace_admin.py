#!/usr/bin/env python3
"""Read-only Google Workspace Directory CLI."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import re
import socket
import stat
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


ROOT = Path(__file__).resolve().parent
SECRETS_DIR = ROOT / ".secrets"
DEFAULT_PROFILE = "default"
PROFILE_PATTERN = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._-]{0,31}\Z")

USER_SCOPE = "https://www.googleapis.com/auth/admin.directory.user.readonly"
GROUP_SCOPE = "https://www.googleapis.com/auth/admin.directory.group.readonly"
GMAIL_SETTINGS_SCOPE = "https://www.googleapis.com/auth/gmail.settings.basic"

# Each command requests only what it uses, so an account holding just one of
# these permissions is not blocked by consent for the others.
COMMAND_SCOPES = {
    "list-users": [USER_SCOPE],
    "list-groups": [GROUP_SCOPE],
    "inspect-gmail-routing": [GMAIL_SETTINGS_SCOPE],
}
SCOPES = sorted({scope for scopes in COMMAND_SCOPES.values() for scope in scopes})

DEPENDENCIES = {
    "google-api-python-client": "googleapiclient",
    "google-auth-oauthlib": "google_auth_oauthlib",
}


def validate_profile(profile: str) -> str:
    """Return a profile name that is safe to use in a filename."""
    if not PROFILE_PATTERN.match(profile):
        raise ValueError(
            f"Invalid profile name: {profile!r}. Use letters, digits, dots, "
            "dashes, or underscores, starting with a letter or digit."
        )
    return profile


def token_path(profile: str = DEFAULT_PROFILE, secrets_dir: Path = SECRETS_DIR) -> Path:
    """Return the token file for a profile, keeping the original default path."""
    if profile == DEFAULT_PROFILE:
        return secrets_dir / "token.json"
    return secrets_dir / f"token-{validate_profile(profile)}.json"


def _is_token_file(path: Path) -> bool:
    """Return whether a .secrets JSON file is a generated token, not a client."""
    return path.name == "token.json" or path.name.startswith("token-")


def client_secret_path() -> Path:
    candidates = sorted(
        path
        for path in SECRETS_DIR.glob("*.json")
        if not _is_token_file(path)
    )
    if not candidates:
        raise FileNotFoundError(
            "No OAuth client JSON found in .secrets. "
            "Place the downloaded Desktop client file there."
        )
    if len(candidates) > 1:
        raise RuntimeError(
            "Multiple OAuth client JSON files found in .secrets; "
            "keep only the intended Desktop client file."
        )
    return candidates[0]


def _private_file(path: Path) -> bool:
    """Return whether a file has no group or other permissions."""
    return not (stat.S_IMODE(path.stat().st_mode) & 0o077)


def _setup_error(errors: list[str], message: str) -> None:
    errors.append(f"✗ {message}")


def _report_command_readiness(granted: set[str], output) -> list[str]:
    """Print per-command readiness and return the commands that cannot run."""
    unavailable = []
    for command, required in sorted(COMMAND_SCOPES.items()):
        missing = [scope for scope in required if scope not in granted]
        if missing:
            unavailable.append(command)
            output(f"  - {command}: not authorized")
            for scope in missing:
                output(f"      missing scope: {scope}")
        else:
            output(f"  - {command}: ready")
    return unavailable


def check_setup(
    secrets_dir: Path = SECRETS_DIR,
    token_file: Path | None = None,
    output=print,
) -> int:
    """Check local prerequisites without authorizing or contacting Google."""
    if token_file is None:
        token_file = token_path(secrets_dir=secrets_dir)
    errors: list[str] = []
    output("Google AI Admin readiness check")
    output("(This check never prints credential contents or contacts Google.)")

    for distribution, module in DEPENDENCIES.items():
        try:
            importlib.metadata.version(distribution)
            __import__(module)
            output(f"✓ Python dependency: {distribution}")
        except (importlib.metadata.PackageNotFoundError, ImportError):
            _setup_error(errors, f"Python dependency missing: {distribution}")

    if not secrets_dir.is_dir():
        _setup_error(errors, "Private secrets folder is missing: .secrets")
        output("\nNext steps:")
        output("  Create .secrets and place one downloaded Desktop OAuth client JSON inside it.")
        return 2
    if stat.S_IMODE(secrets_dir.stat().st_mode) & 0o077:
        _setup_error(errors, ".secrets is accessible to group/other users; run: chmod 700 .secrets")
    else:
        output("✓ Private secrets folder: .secrets")

    client_files = sorted(
        path for path in secrets_dir.glob("*.json") if not _is_token_file(path)
    )
    if len(client_files) == 0:
        _setup_error(errors, "Desktop OAuth client JSON is missing from .secrets")
    elif len(client_files) > 1:
        _setup_error(errors, "More than one OAuth client JSON is in .secrets; keep only the intended one")
    else:
        client_path = client_files[0]
        try:
            client = json.loads(client_path.read_text(encoding="utf-8"))
            installed = client.get("installed")
            required_keys = {"client_id", "client_secret", "auth_uri", "token_uri"}
            if not isinstance(installed, dict) or not required_keys.issubset(installed):
                _setup_error(errors, "OAuth client JSON is not a valid downloaded Desktop client file")
            elif not _private_file(client_path):
                _setup_error(errors, f"OAuth client file is not private; run: chmod 600 {client_path}")
            else:
                output("✓ Desktop OAuth client: present and private")
        except (OSError, json.JSONDecodeError):
            _setup_error(errors, "OAuth client JSON cannot be read as a valid file")

    if not token_file.is_file():
        _setup_error(errors, "Google authorization is not complete; run a Workspace command to sign in")
    else:
        try:
            token = json.loads(token_file.read_text(encoding="utf-8"))
            granted = set(token.get("scopes", []))
            if not _private_file(token_file):
                _setup_error(errors, f"Authorization token is not private; run: chmod 600 {token_file}")
            else:
                output(f"✓ Google authorization: token present and private ({token_file.name})")
            output("\nCommand authorization:")
            unavailable = _report_command_readiness(granted, output)
            if len(unavailable) == len(COMMAND_SCOPES):
                _setup_error(
                    errors,
                    "Google authorization grants no supported command; run a Workspace command to sign in again",
                )
            elif unavailable:
                output(
                    "\nEach command requests only the scopes it needs. Run an unauthorized "
                    "command to add its permission; existing permissions are kept."
                )
        except (OSError, json.JSONDecodeError, AttributeError):
            _setup_error(errors, "Authorization token is not a valid generated OAuth token")

    if errors:
        output("\nNot ready yet:")
        for error in errors:
            output(error)
        output("\nRun the setup instructions in README.md, then run this check again.")
        return 2
    output("\nReady: local tools and Google authorization are configured.")
    return 0


def requested_scopes(required: list[str], granted: set[str]) -> list[str]:
    """Union required scopes with granted ones so consent never drops access."""
    return sorted(set(required) | granted)


def authorize(required: list[str], profile: str = DEFAULT_PROFILE) -> Credentials:
    SECRETS_DIR.mkdir(mode=0o700, exist_ok=True)
    token_file = token_path(profile)
    credentials = None
    granted: set[str] = set()
    if token_file.exists():
        credentials = Credentials.from_authorized_user_file(str(token_file))
        granted = set(credentials.scopes or ())
        if not set(required).issubset(granted):
            credentials = None

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(client_secret_path()), requested_scopes(required, granted)
            )
            oauth_host = os.environ.get("GOOGLE_OAUTH_HOST", "localhost")
            credentials = flow.run_local_server(
                host=oauth_host,
                bind_addr=oauth_host,
                port=0,
                timeout_seconds=300,
                device_id=socket.gethostname(),
                device_name="google-ai-admin-local",
            )
        token_file.write_text(credentials.to_json(), encoding="utf-8")
        token_file.chmod(0o600)
    return credentials


def list_users(service) -> int:
    request = service.users().list(customer="my_customer", orderBy="email")
    count = 0
    while request is not None:
        response = request.execute()
        for user in response.get("users", []):
            name = user.get("name", {}).get("fullName", "")
            print(f"{user.get('primaryEmail', '')}\t{name}")
            count += 1
        request = service.users().list_next(request, response)
    if count == 0:
        print("No users found.")
    return count


def list_groups(service) -> int:
    request = service.groups().list(customer="my_customer", orderBy="email")
    count = 0
    while request is not None:
        response = request.execute()
        for group in response.get("groups", []):
            print(f"{group.get('email', '')}\t{group.get('name', '')}")
            count += 1
        request = service.groups().list_next(request, response)
    if count == 0:
        print("No groups found.")
    return count


def inspect_gmail_routing(service) -> int:
    """Print Gmail filters and forwarding settings, never message contents."""
    filters = service.users().settings().filters().list(userId="me").execute()
    print("Filters:")
    for item in filters.get("filter", []):
        criteria = item.get("criteria", {})
        action = item.get("action", {})
        print(f"  id={item.get('id', '')}")
        print(f"    criteria={json.dumps(criteria, sort_keys=True)}")
        print(f"    action={json.dumps(action, sort_keys=True)}")

    forwarding = service.users().settings().forwardingAddresses().list(userId="me").execute()
    print("Forwarding addresses:")
    addresses = forwarding.get("forwardingAddresses", [])
    if not addresses:
        print("  None configured")
    else:
        for address in addresses:
            print(
                f"  {address.get('forwardingEmail', '')} "
                f"(verification={address.get('verificationStatus', 'unknown')})"
            )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("check-setup", *sorted(COMMAND_SCOPES)),
        help="Read-only Workspace operation",
    )
    parser.add_argument(
        "--profile",
        default=DEFAULT_PROFILE,
        help=(
            "Named Workspace profile. Each profile keeps its own authorization "
            "in .secrets/token-<profile>.json, so managing several tenants does "
            "not overwrite an existing sign-in. Default: %(default)s"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        profile = validate_profile(args.profile)
        if args.command == "check-setup":
            return check_setup(token_file=token_path(profile))
        credentials = authorize(COMMAND_SCOPES[args.command], profile)
        if args.command == "list-users":
            list_users(build("admin", "directory_v1", credentials=credentials))
        elif args.command == "list-groups":
            list_groups(build("admin", "directory_v1", credentials=credentials))
        else:
            inspect_gmail_routing(build("gmail", "v1", credentials=credentials))
        return 0
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        print(f"Setup error: {error}", file=sys.stderr)
        return 2
    except HttpError as error:
        print(
            "Google API error. Confirm the Directory API is enabled and "
            "that the authorized account is a Workspace administrator.",
            file=sys.stderr,
        )
        print(f"Details: {error.reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
