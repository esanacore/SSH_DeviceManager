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

## Last Session — 2026-07-19: Constitution 1.39.0 Update

- **Branch**: `chore/constitution-1.39.0`.
- **Scope**: Governance only. No runtime behavior changed.
- **Why so soon after the previous bump**: upstream tagged two releases thirty minutes apart on the same evening (20:16 and 20:46). Because `check_constitution_freshness.sh` reports `BEHIND` as a **hard** version-gate failure — unlike `AHEAD`, which only warns — every open pull request in this repository goes red the moment upstream tags, regardless of what that pull request changes. PR #23 was merged with a known-red `version-gate` for exactly this reason: its other 20 checks passed and its content never touched the submodule. Expect this to recur while upstream is releasing rapidly.
- **Added**: `.github/workflows/constitution-architecture.yml` and the `Layer Boundaries` section in `docs/ARCHITECTURE.md`, left **undeclared** so enforcement stays opt-in and `SKIP`ped.
- **Trap hit and reverted, worth knowing**: `check_architecture.sh` parses the `Layer Boundaries` pipe table by text and does **not** respect HTML comment boundaries. A draft table sketched inside an HTML comment was still read as a live declaration; because its paths did not resolve, the checker emitted per-layer `WARN`s but still summarized "all dependencies point inward" — enforcement that appears active while verifying nothing. The candidate layering is therefore recorded as prose, not a table. Do not sketch a draft table in that file.
- **Second, related trap**: `check_compliance.sh` treats *any* HTML comment marker as placeholder content, so a file carrying one fails the `--strict` placeholder check. The 1.39.0 `docs/ARCHITECTURE.md` template ships eight of them, meaning following the template as written breaks strict compliance. This repository's `docs/ARCHITECTURE.md` therefore uses ordinary Markdown prose where the template used comments. Avoid reintroducing HTML comments into governance documents.
- **Verification**: 176 tests pass; pylint 10.00/10; compliance `--strict --product`, secrets, OTS, env-vars, architecture (`SKIP`, 0 violations), traceability (12/12), version alignment, and freshness (`CURRENT (v1.39.0)`) all pass.

### Carried-Forward Context

Earlier sessions in this sequence are recorded in `CHANGELOG.md` and the commit history; only
context still worth acting on is repeated here.

- **The `AHEAD/DIVERGED` tagging gap is resolved.** Upstream tags now exist for every release, so
  the pin always resolves to a real tag. Never "fix" a freshness complaint by pinning backward —
  older tags predate checkers this repository now depends on.
- **Optional cleanup not taken.** The current release line relocates constitution-owned documents
  out of the repository root (`SECURITY.md`/`CONTRIBUTING.md` to `.github/`, `HELP.md`/
  `SYSTEM_PROMPT.md` to `docs/`) and makes the 13 vendor instruction files opt-in rather than
  installed by default. `check_compliance.sh` accepts either location, so neither is required.
  Both are logged in `TODO.md` under Governance as deliberate decisions rather than silent omissions.
- **`SECURITY.md` must not be refreshed from its template.** Its section structure matches exactly,
  so a mechanical template sync looks correct — but its content is real project-specific security
  guidance where the template ships placeholders.
- **Paramiko and setuptools constraints still apply**: see `docs/OTS_SOFTWARE.md` OTS-001 and
  OTS-107. In particular, do not raise the setuptools floor above 75.3.x while Python 3.8 is
  supported — setuptools dropped 3.8 after that release, and a higher floor makes the project
  uninstallable on the very version `requires-python` claims to support.
- **Unmerged operator documentation** sits on `codex-ops-roadmap-docs` with no remote branch. See
  the salvage item in `TODO.md` under Documentation before removing any worktree.

## Handoff Note Template

When handing off work, include:

- Branch/worktree path.
- Files changed.
- Tests and Constitution checks run, with exact results.
- Any checks skipped and why.
- Security-sensitive decisions or remaining risks.
- Follow-up TODO entries created or completed.
