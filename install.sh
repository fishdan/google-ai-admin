#!/usr/bin/env bash
set -euo pipefail

# One-command bootstrap for local AI-assisted Google Workspace tooling.
# Safe to run from an existing checkout or through curl | bash.

REPO_URL="${GOOGLE_AI_ADMIN_REPO_URL:-https://github.com/fishdan/google-ai-admin.git}"
INSTALL_DIR="${GOOGLE_AI_ADMIN_DIR:-${HOME}/.google-ai-admin}"

say() { printf '%s\n' "$*"; }
fail() { say "Installation stopped: $*" >&2; exit 1; }

command -v git >/dev/null 2>&1 || fail "Git is required. Install Git, then run this command again."
PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
  for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then PYTHON="$candidate"; break; fi
  done
fi
[[ -n "$PYTHON" ]] || fail "Python 3 is required. Install Python 3, then run this command again."
"$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' \
  || fail "Python 3.10 or newer is required."

if [[ -f "google_workspace_admin.py" && -d ".git" ]]; then
  PROJECT_DIR="$(pwd -P)"
  say "Using existing checkout: ${PROJECT_DIR}"
else
  PROJECT_DIR="$INSTALL_DIR"
  if [[ -e "$PROJECT_DIR" && ! -d "$PROJECT_DIR/.git" ]]; then
    fail "Install destination exists but is not a Google AI Admin checkout: ${PROJECT_DIR}"
  fi
  if [[ ! -d "$PROJECT_DIR/.git" ]]; then
    say "Downloading Google AI Admin to ${PROJECT_DIR}"
    git clone "$REPO_URL" "$PROJECT_DIR"
  else
    say "Using existing installation: ${PROJECT_DIR}"
  fi
fi

cd "$PROJECT_DIR"
mkdir -p .secrets
chmod 700 .secrets
"$PYTHON" -m venv .venv
".venv/bin/python" -m pip install --disable-pip-version-check -r requirements.txt

say "Installation complete. Checking readiness..."
set +e
".venv/bin/python" google_workspace_admin.py check-setup
CHECK_STATUS=$?
set -e

if [[ "$CHECK_STATUS" -ne 0 ]]; then
  say "The local framework is installed, but Google authorization still needs attention."
  say "Follow the short setup steps in ${PROJECT_DIR}/README.md, then run:"
  say "  cd ${PROJECT_DIR} && .venv/bin/python google_workspace_admin.py check-setup"
else
  say "You are ready to ask your AI assistant to use the Workspace tools."
fi
