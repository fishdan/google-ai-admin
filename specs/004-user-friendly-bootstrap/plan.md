# Implementation Plan: User-Friendly Google Workspace Bootstrap

1. Centralize setup checks in the Python CLI so the installer and AI/user workflow share one source of truth.
2. Keep the shell installer small: detect context, verify prerequisites, create/update the local environment, and invoke the readiness gate.
3. Make diagnostics safe by reporting paths, filenames, scopes, and remediation only; never values from secret files.
4. Update README, constitution, and startup guidance to establish this repository as an AI-to-Google-Workspace framework with read-only and confirmation boundaries.
5. Validate using temporary fixture directories and shell syntax checks; do not require live Google credentials.
