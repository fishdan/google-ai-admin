#!/usr/bin/env python3
"""Read-only Google Workspace Directory CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


ROOT = Path(__file__).resolve().parent
SECRETS_DIR = ROOT / ".secrets"
TOKEN_PATH = SECRETS_DIR / "token.json"
SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
    "https://www.googleapis.com/auth/admin.directory.group.readonly",
]


def client_secret_path() -> Path:
    candidates = sorted(
        path
        for path in SECRETS_DIR.glob("*.json")
        if path.name != TOKEN_PATH.name
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


def authorize() -> Credentials:
    SECRETS_DIR.mkdir(mode=0o700, exist_ok=True)
    credentials = None
    if TOKEN_PATH.exists():
        credentials = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(client_secret_path()), SCOPES
            )
            credentials = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(credentials.to_json(), encoding="utf-8")
        TOKEN_PATH.chmod(0o600)
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("list-users", "list-groups"), help="Directory operation"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        credentials = authorize()
        service = build("admin", "directory_v1", credentials=credentials)
        if args.command == "list-users":
            list_users(service)
        else:
            list_groups(service)
        return 0
    except (FileNotFoundError, RuntimeError, json.JSONDecodeError) as error:
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
