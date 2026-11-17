# Antigravity Instructions

This repository follows [Eric's Engineering Constitution](constitution/CONSTITUTION.md).

## Agent Workflow

As an autonomous agent in this workspace, you MUST:
1. Initialize by reading `constitution/CONSTITUTION.md` and `constitution/AI_WORKFLOW.md`.
2. Adhere to the project-specific rules in `AGENTS.md`.
3. Maintain the `TODO.md` and `CHANGELOG.md` as living documents.
4. Follow the architectural standards in `docs/adr/`.
5. Keep the demo page current — when a change alters user-facing behavior and the repository has a `demo.html`, update it in the same change; a demo still showing the old behavior is an incomplete change (`constitution/DOCUMENTATION.md`, "Demo Page").
6. Consult and extend the session log — before planning, read the newest rows of `docs/sessions/README.md` and search `docs/sessions/` for earlier sessions on the same topic (`bash constitution/scripts/find_sessions.sh <keyword>`), reading the ones that match; before completing non-trivial work, add this session's summary there (request, context, decisions, discoveries, outcome — a summary, never a transcript, and never a secret) and list it in the index (`constitution/AI_WORKFLOW.md`, "Session Summaries").

## Command Execution

Refer to `docs/COMMAND_REFERENCE.md` for the exact commands required for building, testing, and linting. Always run tests before considering a task complete.
