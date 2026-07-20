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

## Last Session — 2026-07-19: Constitution 1.38.0 Update

- **Branch**: `chore/constitution-1.38.0`.
- **Scope**: Governance only. No runtime behavior in `ssh_device_manager/` was touched.
- **Submodule**: moved forward one release; `check_constitution_freshness.sh` now reports `CURRENT`.
- **Added**: `docs/ENV_VARS.md` (the new Environment & Configuration Contract) and the matching
  `.github/workflows/constitution-env.yml` gate. This project reads **no** environment variables —
  verified by scanning for `os.environ`/`os.getenv`/`environ[...]` across the package and root
  modules — so the document records that fact explicitly and describes the file-based configuration
  (`ssh_device_manager_config.json`, `sections.json`) used instead.
- **Refreshed**: `CONTRIBUTING.md` and `HELP.md` from the new templates. `SECURITY.md` was
  deliberately **not** refreshed: its section structure matches the template exactly but its content
  is real project-specific security guidance, where the template ships placeholders.
- **Verification**: 176 tests pass; pylint 10.00/10; compliance `--strict --product`, secrets
  `--strict`, OTS `--strict`, env-vars `--strict`, traceability (12/12), and version alignment all pass.

### Carried-Forward Context

- The upstream tagging gap that produced `AHEAD/DIVERGED` in the previous session is **resolved** —
  releases through 1.38.0 are now tagged upstream, and the pin resolves to a real tag.
- **Optional cleanup not taken.** 1.38.0 relocates constitution-owned docs out of the repository root
  (`SECURITY.md`/`CONTRIBUTING.md` to `.github/`, `HELP.md`/`SYSTEM_PROMPT.md` to `docs/`) and makes
  the 13 vendor instruction files opt-in rather than default. Its Compatibility note states existing
  repositories need not move anything, and `check_compliance.sh` accepts either location. Both are
  logged in `TODO.md` under Governance as deliberate, separate decisions rather than silent changes.
- Paramiko constraints from the manifest session still apply: see `docs/OTS_SOFTWARE.md` OTS-001 and
  OTS-107. In particular, do not raise the setuptools floor above 75.3.x while Python 3.8 is supported.

## Handoff Note Template

When handing off work, include:

- Branch/worktree path.
- Files changed.
- Tests and Constitution checks run, with exact results.
- Any checks skipped and why.
- Security-sensitive decisions or remaining risks.
- Follow-up TODO entries created or completed.
