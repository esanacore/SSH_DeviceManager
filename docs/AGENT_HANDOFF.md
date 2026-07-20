# Agent Handoff

Use this file to leave concise context for the next human or AI agent working on SSH Device Manager.

## Current Project Shape

- Local Python/Tkinter desktop app for SSH command execution and SFTP uploads.
- Main launcher: `SSH_DeviceManager.py`.
- Package code: `ssh_device_manager/`.
- Primary tests: `test_SSH_DeviceManager.py` and `test_customizer.py`.
- Constitution submodule: `constitution/`.

## Before Changing Code

1. Read `AGENTS.md`.
2. Read the required Constitution files listed there.
3. Review `README.md`, `TODO.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, and `docs/TEST_PLAN.md`.
4. Check `docs/SESSION_PLAN.md` for an interrupted session, and read `docs/MEMORY.md` for project memory.
5. Run or understand the current baseline command:

   ```bash
   python -m unittest test_SSH_DeviceManager test_customizer -v
   ```

## Last Session — 2026-07-19: Constitution 1.37.0 Alignment

- **Branch**: `chore/constitution-1.37.0-alignment`.
- **Scope**: Governance only. No runtime behavior in `ssh_device_manager/` was touched.
- **Submodule**: advanced `v1.30.0` → Constitution `1.37.0` (`f1cd362` on `main`).
- **Added**: `docs/OTS_SOFTWARE.md`, `docs/SESSION_PLAN.md`, `docs/MEMORY.md`, four CI gates
  (`constitution-tests`, `-doc-freshness`, `-secrets`, `-ots`), `.claude/settings.json` SessionStart hook,
  a machine-readable `## How to Run Tests` section in `docs/TEST_PLAN.md`, and secrets coverage in `.gitignore`.
- **Refreshed**: all agent instruction files against 1.37.0 templates. Project-specific architecture content in
  `.github/copilot-instructions.md` was preserved, not overwritten.
- **Verification**: 176 tests pass via the declared command; pylint 10.00/10;
  `check_compliance.sh --strict --product`, `check_version_alignment.sh`, `check_traceability.sh` (12/12),
  and `check_secrets.sh --strict` all pass.
- **Known non-clean status**: `check_constitution_freshness.sh` reports `AHEAD/DIVERGED (pinned v1.37.0, latest tag v1.34.0)`.
  This is expected and non-blocking. The upstream constitution repo declares 1.37.0 in `VERSION`/`CHANGELOG.md` but
  its newest Git tag is `v1.34.0`; releases 1.35–1.37 were never tagged. Tagging them upstream is logged in
  `TODO.md` under Governance and will clear this to `CURRENT`. Do **not** "fix" it by pinning back to `v1.34.0` —
  that tag predates `check_ots_inventory.sh` and the `docs/MEMORY.md` template, and would break the OTS gate.
- **Deliberately out of scope**: adding a `requirements.txt`/`pyproject.toml` manifest. It is an existing
  `TODO.md` Technical Debt item, and this session was scoped to constitution alignment only. Until it exists,
  `check_ots_inventory.sh` has no manifest to cross-check, so the `paramiko` row in `docs/OTS_SOFTWARE.md`
  is named to bind to it automatically once one lands.

## Handoff Note Template

When handing off work, include:

- Branch/worktree path.
- Files changed.
- Tests and Constitution checks run, with exact results.
- Any checks skipped and why.
- Security-sensitive decisions or remaining risks.
- Follow-up TODO entries created or completed.
