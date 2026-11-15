# Copilot Instructions

This repository follows Eric's Engineering Constitution.

## Context Files

Use these files as primary context:

- `constitution/CONSTITUTION.md`
- `constitution/AI_WORKFLOW.md`
- `constitution/TESTING.md`
- `constitution/DOCUMENTATION.md`
- `constitution/SECURITY.md`
- `constitution/ARCHITECTURE.md`
- `README.md`
- `TODO.md`
- `CHANGELOG.md`
- `docs/MEMORY.md`
- `docs/sessions/README.md` — the session-log index, newest rows; search the log for the task's topic and read matching summaries on demand

## Development Standards

- Prefer existing project conventions.
- Keep changes focused and maintainable.
- Check `docs/SESSION_PLAN.md` for a previous interrupted session; write your own plan before implementing.
- Add tests for new behavior.
- Add regression tests for bug fixes.
- Update documentation for changed behavior, setup, architecture, or operations.
- Update TODO.md with discovered follow-up work.
- Update CHANGELOG.md for user-facing changes.
- Avoid adding unnecessary dependencies.
- Consider security, observability, and release impact.
- Propose new codebase learnings, user preferences, or major decisions to the user and (upon approval) record them in `docs/MEMORY.md` before completing work.
- Keep the demo page current — when a change alters user-facing behavior and the repository has a `demo.html`, update it in the same change; a demo still showing the old behavior is an incomplete change (`constitution/DOCUMENTATION.md`, "Demo Page").
- Consult and extend the session log — before planning, read the newest rows of `docs/sessions/README.md` and search `docs/sessions/` for earlier sessions on the same topic (`bash constitution/scripts/find_sessions.sh <keyword>`), reading the ones that match; before completing non-trivial work, add this session's summary there (request, context, decisions, discoveries, outcome — a summary, never a transcript, and never a secret) and list it in the index (`constitution/AI_WORKFLOW.md`, "Session Summaries").
