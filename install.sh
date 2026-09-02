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
PYTHON_TAG="$("$PYTHON" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
"$PYTHON" -c 'import ensurepip' >/dev/null 2>&1 || fail \
  "Python's virtual environment support is missing, so an isolated environment cannot be created.
  On Debian or Ubuntu, install it with one of:
    sudo apt install python3-venv
    sudo apt install python${PYTHON_TAG}-venv
  Then run this command again."

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

# A failed `python -m venv` can leave a directory with no working interpreter,
# which would poison every later run. Treat that state as absent and rebuild.
if [[ -d ".venv" && ! -x ".venv/bin/python" ]]; then
  say "Removing an incomplete virtual environment: ${PROJECT_DIR}/.venv"
  rm -rf ".venv"
fi
if [[ ! -x ".venv/bin/python" ]]; then
  "$PYTHON" -m venv .venv || {
    rm -rf ".venv"
    fail "Could not create the virtual environment in ${PROJECT_DIR}. The partial environment was removed, so this command is safe to run again."
  }
fi
".venv/bin/python" -m pip install --disable-pip-version-check -r requirements.txt

say "Installation complete. Checking readiness..."
set +e
".venv/bin/python" google_workspace_admin.py check-setup
CHECK_STATUS=$?
set -e

say ""
say "Installed to: ${PROJECT_DIR}"

if [[ "$CHECK_STATUS" -ne 0 ]]; then
  say "The local framework is installed, but Google authorization still needs attention."
  say "Follow the short setup steps in ${PROJECT_DIR}/README.md, then run:"
  say "  cd ${PROJECT_DIR} && .venv/bin/python google_workspace_admin.py check-setup"
else
  say "You are ready to ask your AI assistant to use the Workspace tools."
  say "  cd ${PROJECT_DIR}"
fi
