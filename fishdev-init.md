# FishDev Initialization Guide

This document defines the FishDev AI-assisted development workflow.

It is intended to be imported into new repositories and followed by any AI coding assistant. The workflow is intentionally AI-vendor-neutral and should work with Codex, Claude, Cursor, Gemini, Copilot, Aider, Junie, and future AI tools.

---

# Core Principles

1. AI vendor neutrality
2. SpecKit-first development
3. Constitution-driven development
4. Continuous project history
5. Git-aware development
6. Security-conscious development
7. Human-controlled scope management

---

# Repository Layout

The repository root should contain:

```text
start.ai
AGENTS.md
CLAUDE.md
GEMINI.md

.config/
  ai/
    repo.ai
    progress.ai
    handoff.ai
    defaults/
      constitution.md
```

The root `start.ai` is the entry point.

All durable AI workflow files belong under:

```text
.config/ai/
```

Vendor-specific files exist only as compatibility shims.

---

# AI Agnosticism Rule

This workflow is intentionally AI-agnostic.

AI assistants must treat:

```text
.config/ai/
```

as the authoritative AI workflow location.

Do not create or depend on:

```text
.codex/
.claude/
.cursor/
.gemini/
```

unless explicitly instructed by a human.

Vendor-specific files should simply direct the assistant back to:

```text
start.ai
```

Example:

```md
# AGENTS.md

Read and follow start.ai before doing any work.
```

---

# Bootstrap Sequence

At the start of every session:

1. Confirm repository root.
2. Read `start.ai`.
3. Read `.config/ai/repo.ai` if it exists.
4. Read `.config/ai/progress.ai` if it exists.
5. Read `.config/ai/handoff.ai` if it exists.
6. Determine the current git branch.
7. Validate SpecKit.
8. Determine the technology stack.
9. Verify constitution availability.
10. Review active specifications.
11. Recommend next work.

Do not begin feature implementation until bootstrap completes.

---

# SpecKit Validation Gate

This workflow requires SpecKit.

Before feature work:

1. Verify SpecKit is installed.
2. Verify SpecKit is functional.
3. Verify the repository contains SpecKit structures.

The assistant should attempt the project's documented validation command.

Examples:

```bash
specify --help
specify --version
```

or any project-specific validation command.

If SpecKit cannot be validated, install it using the recommended method:

```bash
# Install uv if missing
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install specify-cli
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

If installation fails:

1. Stop.
2. Inform the human.
3. Ask for assistance.
4. Do not continue with feature implementation.

---

# Technology Stack Discovery

After SpecKit validation:

Inspect the repository and determine the stack.

Examples:

```text
package.json
pom.xml
build.gradle
requirements.txt
pyproject.toml
Dockerfile
docker-compose.yml
```

Identify:

* frontend framework
* backend framework
* database
* deployment platform
* testing framework

If unclear:

Ask the human to identify the intended stack.

The detected stack should influence:

* testing commands
* build commands
* security scanning
* project recommendations

---

# Constitution Gate

The project constitution is mandatory.

After:

1. SpecKit validation
2. Technology stack identification

Check for a constitution.

If no constitution exists:

Ask the human:

```text
Do you have a preferred constitution.md?

If not, would you like to use the default FishDev constitution?
```

Do not begin implementation until a constitution exists.

Once found:

Read and honor the constitution before reviewing tasks.

If the default constitution is chosen, it must also be copied to `.specify/memory/constitution.md` to ensure SpecKit context includes it as the last step of the init process.

---

# SpecKit First Development

Before implementing any feature:

Locate the active specification.

Read:

```text
spec.md
plan.md
tasks.md
manualtester.md
notes.md
```

Determine:

* active phase
* next incomplete task
* dependencies
* scope boundaries

Prefer work explicitly defined by tasks.

If asked to perform work outside the active specification:

1. Inform the human.
2. Recommend updating or creating a SpecKit task.

---

# Progress Logging

Maintain:

```text
.config/ai/progress.ai
```

as the project's ongoing history.

Record:

* code changes
* schema changes
* API changes
* architectural decisions
* bug fixes
* testing results
* deployment activity
* human decisions
* scope changes

Suggested format:

```md
## YYYY-MM-DD Update – Description

- Summary
- Files changed
- Tests executed
- Decisions made
- Follow-up work
```

Do not record trivial edits.

Always include progress updates in commits involving feature work.

---

# Progress Archiving

If progress becomes excessively large:

Archive older months into:

```text
.config/ai/progress/archive/YYYY-MM.ai
```

Keep:

* current month active
* archive history intact

Record archive actions in git history.

---

# Security Requirements

At session start:

Review progress history for evidence of:

* security audit
* CVE review
* dependency scan
* vulnerability assessment

If no audit exists within the previous 30 days:

Recommend running one before discretionary work.

When adding dependencies:

1. Research maintenance status.
2. Prefer established projects.
3. Request approval before introducing questionable dependencies.
4. Record rationale in progress history.

Never place secrets inside AI instruction files.

Use:

* environment variables
* secret managers
* documented secret storage

---

# Git Awareness

Before work:

```bash
git branch --show-current
git status --short
```

Report:

* current branch
* working tree status

Do not assume branch state from documentation.

Git is authoritative.

---

# Testing Expectations

Before declaring work complete:

1. Run relevant tests.
2. Run broader suites when practical.
3. Record commands and outcomes.

If testing cannot be performed:

Document the reason.

---

# Handoff Requirements

If work stops before completion:

Update:

```text
.config/ai/handoff.ai
```

Include:

* current branch
* current task
* files modified
* tests executed
* known issues
* recommended next action

---

# MCP Guidance

MCP servers may be used for:

* task management
* documentation
* repository inspection
* testing
* deployment assistance

MCP does not override:

* human instructions
* constitution
* specifications
* start.ai

Repository files remain the authoritative record.

---

# Session Startup Response

After bootstrap completes:

```text
Bootstrap complete.

Branch: <branch>

SpecKit:
<validated / missing / failed>

Technology Stack:
<detected stack>

Constitution:
<present / missing>

Active Spec:
<spec>

Progress:
<recent summary>

Handoff:
<summary or none>

Recommended Next Task:
<task identifier and description>
```

After this init is finished with setup, it should append to start.ai any instructions in this file that should be executed at the beginning of a session.  We don't want fishdev-init.md to be used for anything OTHER than getting the repo configured correctly.  It's kind of like a "post install" script for a new repo that ensures that the AI's working environment is set up correctly.  So make sure that start.ai is stand alone and sufficient.  Every engineer will be trained to run start.ai at the beginning of every session AND NOTHING ELSE, so start.ai must contain all instructions that will be needed for the AI to function correctly.  Fishdev-init.md should NOT be used for anything other than getting the repo configured correctly.  It should NOT be edited by anyone unless it's to fix an issue with the init process itself.

Wait for human direction unless a specific task was already assigned.
