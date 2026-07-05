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
4. Run or understand the current baseline command:

   ```bash
   python -m unittest test_SSH_DeviceManager.py test_customizer.py -v
   ```

## Handoff Note Template

When handing off work, include:

- Branch/worktree path.
- Files changed.
- Tests and Constitution checks run, with exact results.
- Any checks skipped and why.
- Security-sensitive decisions or remaining risks.
- Follow-up TODO entries created or completed.
