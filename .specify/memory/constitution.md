# FishDev Default Constitution

Version: 1.0

This constitution defines the engineering principles governing all repositories set up with the FishDev CLI tool.

This constitution is authoritative once adopted by a repository.

All humans and AI assistants working within the repository must follow these principles.

---

# I. Constitution Supremacy

This constitution governs all engineering activity within the repository.

Specifications, plans, tasks, implementations, reviews, commits, and AI behavior must comply with this constitution.

If a conflict exists between this constitution and an implementation decision, the constitution prevails.

---

# II. Spec-Driven Development

All work must originate from a specification.

No code change is too small to require specification.

This includes:

* Features
* Bug fixes
* Refactors
* Documentation updates
* Dependency upgrades
* Configuration changes
* Typographical corrections

Every meaningful change must be traceable to:

1. A specification
2. A task
3. A progress log entry

If no specification exists, create one before implementing work.

If no task exists, create one before implementing work.

Implementation without specification is prohibited.

---

# III. Repository State Is Authoritative

The repository is the source of truth.

Authoritative project knowledge exists only in:

* Constitution files
* Specifications
* Tasks
* Progress logs
* Handoff files
* Source code
* Tests
* Version control history

Human memory is not authoritative.

AI memory is not authoritative.

Prior conversations are not authoritative.

When uncertainty exists, consult the repository.

---

# IV. Clean Code

Code should follow the principles described by Robert C. Martin and Martin Fowler.

Code should be:

* Readable
* Maintainable
* Testable
* Refactorable
* Understandable by a new engineer

Prefer:

* Small functions
* Clear naming
* Single responsibility
* Explicit behavior
* Low coupling
* High cohesion

Code should be written for future maintainers, not merely for current execution.

---

# V. Refactoring Is Continuous

Refactoring is encouraged when it improves maintainability.

However:

Refactoring must remain within the scope of the current specification and task.

Large architectural changes require explicit specification.

Unrelated refactoring should not be mixed into feature work.

---

# VI. Narrow Task Scope

Work should remain narrowly focused on the active task.

Avoid unrelated changes.

Avoid opportunistic improvements outside the specification.

Avoid expanding scope without explicit approval.

The goal is predictable, reviewable progress.

---

# VII. Testing First

Testing is a first-class deliverable.

Preferred order:

1. Test-first development
2. Test development concurrent with implementation
3. Test-after-development (discouraged)

Code without validation is incomplete.

Every feature should have a corresponding validation strategy.

---

# VIII. Local and CI Validation

Tests should be executable:

1. Locally by developers
2. Automatically within CI/CD pipelines

Prefer test frameworks that support both environments.

Examples include:

* JUnit
* Jest
* Vitest
* PyTest
* Playwright
* Cypress
* Schemathesis

Avoid testing approaches that only work in a single environment when practical alternatives exist.

---

# IX. Version Controlled Databases

Database schema changes must be version controlled.

Flyway is the preferred migration framework.

Alternative migration frameworks are acceptable only if they provide equivalent:

* Version tracking
* Repeatability
* Reproducibility
* Auditability

Manual schema changes are prohibited except during emergencies and must be reconciled into version control immediately afterward.

---

# X. Git History Preservation

Version control history is valuable.

Never:

* Rewrite history unnecessarily
* Destroy work without authorization
* Reset or clean repositories without approval

Human work must never be discarded without explicit permission.

When uncertainty exists, stop and ask.

---

# XI. Progress Over Conversation

Project knowledge should be recorded in repository artifacts.

Important decisions belong in:

* Specifications
* Progress logs
* Handoff files
* Documentation

Do not rely on chat history to preserve project state.

A future engineer should be able to understand the project without access to prior conversations.

---

# XII. Human Reviewability

Every change should be understandable during review.

A reviewer should be able to determine:

* What changed
* Why it changed
* Which task it satisfies
* How it was tested

without reading AI conversations.

Repository artifacts should contain sufficient context.

---

# XIII. Reproducibility

Any engineer should be able to:

* Clone the repository
* Install dependencies
* Run tests
* Build the project

using documented procedures.

Avoid tribal knowledge.

Avoid undocumented setup steps.

Prefer automation over manual processes.

---

# XIV. Explicit Dependencies

Dependencies introduce long-term maintenance obligations.

Before introducing a dependency:

1. Evaluate maturity
2. Evaluate maintenance status
3. Evaluate community adoption
4. Evaluate security posture

Dependency selection should be deliberate.

When practical, document the rationale for introducing significant dependencies.

---

# XV. Technology Neutrality

Technology choices should be based on suitability, maintainability, and operational value.

Avoid adopting technologies primarily because they are fashionable.

Prefer:

* Stability
* Maintainability
* Simplicity
* Long-term support

over novelty.

---

# XVI. Security by Default

Security is a continuous responsibility.

Repositories should:

* Track dependency vulnerabilities
* Review security issues regularly
* Protect secrets appropriately
* Follow least-privilege principles

Secrets must never be committed to source control.

Security audits should be performed regularly and recorded in project history.

---

# XVII. AI Transparency

AI assistance is permitted and encouraged.

Work should be judged by:

* Correctness
* Maintainability
* Testability
* Documentation quality
* Security

not by whether it was produced by a human or an AI.

AI-generated code is subject to the same standards as human-generated code.

---

# XVIII. Specification Structure

Specifications are organized by release and feature.

Required structure:

```text
specs/
  <release-number>/
    <release>.<feature-number>-<feature-name>/
```

Examples:

```text
specs/
  0/
    0.001-user-authentication/
    0.002-registration/
    0.003-profile-management/

  1/
    1.001-reporting/
    1.002-admin-tools/
```

Rules:

* Release numbers start at 0
* Feature numbers increment sequentially within a release
* Feature names should be descriptive
* Specification directories are permanent project history

Specifications should contain, when applicable:

* spec.md
* plan.md
* tasks.md
* manualtester.md
* notes.md

---

# XIX. Progress Logging

Repositories must maintain an ongoing project history.

Progress logs should record:

* Decisions
* Implementations
* Test results
* Architectural changes
* Deployment events
* Significant discussions

The progress log is the project's operational memory.

---

# XX. Completion Criteria

Work is not complete until:

* Specification exists
* Task exists
* Implementation exists
* Testing exists
* Progress log updated
* Constitution remains satisfied

Implementation alone does not constitute completion.

---

# Guiding Principle

Build systems that a competent engineer can understand, verify, test, maintain, and extend years later.

Favor clarity over cleverness.
Favor discipline over convenience.
Favor documented knowledge over remembered knowledge.
Favor specifications over assumptions.
Favor maintainability over novelty.
