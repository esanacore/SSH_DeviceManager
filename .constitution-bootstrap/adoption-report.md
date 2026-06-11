# Engineering Constitution Adoption Report

Project: SSH Device Manager

Project path: `/mnt/c/Projects/SSH_DeviceManager`

Constitution source: `/mnt/c/Projects/engineering-constitution`

## What Happened

The bootstrap script installed the Engineering Constitution in a non-destructive mode.

Existing project files were not overwritten. When a target file already existed, the matching constitution template was copied into `.constitution-bootstrap/templates/` so maintainers can compare and merge manually.

## Current Governance Files

- [x] README.md exists
- [x] AGENTS.md exists
- [x] CLAUDE.md exists
- [x] .agent-instructions.md exists
- [x] .cursorrules exists
- [x] .antigravity/instructions.md exists
- [x] .openhands_instructions exists
- [x] .project-rules.md exists
- [x] SYSTEM_PROMPT.md exists
- [x] CONTRIBUTING.md exists
- [x] HELP.md exists
- [x] SECURITY.md exists
- [x] .github/copilot-instructions.md exists
- [x] .cursor/rules/project.mdc exists
- [x] TODO.md exists
- [x] CHANGELOG.md exists
- [x] VERSION exists
- [x] docs/adr exists
- [x] docs/SETUP.md exists
- [x] docs/COMMAND_REFERENCE.md exists
- [x] docs/TROUBLESHOOTING.md exists
- [x] docs/AGENT_PROMPTS.md exists
- [x] docs/AGENT_HANDOFF.md exists
- [x] docs/OPERATIONS.md exists
- [x] docs/ARCHITECTURE.md exists

## Files Written

- ` AGENTS.md`
- `CLAUDE.md`
- `.agent-instructions.md`
- `.cursorrules`
- `.antigravity/instructions.md`
- `.openhands_instructions`
- `.project-rules.md`
- `SYSTEM_PROMPT.md`
- `CONTRIBUTING.md`
- `HELP.md`
- `SECURITY.md`
- `.cursor/rules/project.mdc`
- `TODO.md`
- `VERSION`
- `docs/adr/0001-record-architecture-decisions.md`
- `docs/SETUP.md`
- `docs/COMMAND_REFERENCE.md`
- `docs/TROUBLESHOOTING.md`
- `docs/AGENT_PROMPTS.md`
- `docs/AGENT_HANDOFF.md`
- `docs/OPERATIONS.md`
- `docs/ARCHITECTURE.md`

## Existing Files Preserved

- ` .github/copilot-instructions.md`
- `CHANGELOG.md`
- `README.md`

## Detected Project Signals

- GitHub Actions workflows: `.github/workflows`

## Recommended Merge Steps

1. Compare existing files with templates in `.constitution-bootstrap/templates/`.
2. Merge relevant Engineering Constitution sections into existing project files.
3. Customize generated placeholders in TODO.md, CHANGELOG.md, README.md, and ADRs.
4. Commit `.gitmodules`, the `constitution` submodule reference, generated files, and any merged documentation changes.
5. Keep or remove `.constitution-bootstrap/` depending on whether the adoption report is useful to the project.

## Suggested Agent Context

Add or verify these instructions in AGENTS.md:

- Read `constitution/CONSTITUTION.md` before making changes.
- Read `README.md`, `TODO.md`, and `CHANGELOG.md` for project context.
- Update tests, docs, TODO.md, and CHANGELOG.md when relevant.
- Record major design decisions in `docs/adr/`.
- See `constitution/INTEGRATION.md` for override patterns and update instructions.
