# TODO

This file is the living roadmap for SSH Device Manager.

## Features

- [ ] Add OS keyring integration so users can opt into secure credential storage without writing passwords to repository or profile files.
- [ ] Add a real-device smoke-test checklist for SSH command execution and SFTP uploads against a disposable test host.

## Technical Debt

- [ ] Add a coverage tool and record the first measured line/branch coverage baseline in `docs/TEST_PLAN.md`.
- [x] Add a dependency manifest for runtime and contributor tooling so Paramiko and Pylint setup is reproducible. Added `pyproject.toml` (PEP 621) with `paramiko>=3.4` as the runtime dependency and a `dev` extra for Pylint, flake8, pre-commit, and build. Version is read dynamically from `VERSION` to avoid a second source of truth.
- [ ] Consider raising `requires-python` from `>=3.8` to `>=3.9`. Python 3.8 has been end-of-life since October 2024, and the 3.8 floor is the only reason `paramiko` is specified as `>=3.4` rather than `>=4` — a 3.8 install silently receives the older Paramiko 3.x line. Raising the floor would let the project require Paramiko 4.x uniformly and drop 3.8 from the CI matrices. Deferred because commit `e103746` deliberately added 3.8 compatibility.
- [ ] Add a `pip` ecosystem entry to `.github/dependabot.yml` now that a manifest exists, so Paramiko upgrades are proposed automatically rather than noticed by hand.

## Operations

- [ ] Protect the `main` branch with required status checks and required review. `constitution/INTEGRATION.md`'s "Repository Settings Checklist" expects this, and `gh api .../branches/main/protection` currently returns "Branch not protected", so nothing enforces the constitution gates before a merge.
- [ ] Enable "Automatically delete head branches" in the repository settings, per the same checklist.
- [ ] Clean up stale Codex worktrees. `git worktree list` shows three left over from earlier sessions:
  - `C:/Projects/_codex_worktrees/steward-2026-07-14/SSH_DeviceManager` → `codex/constitution-v133-readme-alignment`. Safe to remove: its remote branch is deleted, PR #18 is closed, and its one genuinely useful change (documenting `check_version_alignment.sh`) was salvaged into `docs/COMMAND_REFERENCE.md`. The local branch only survives because this worktree pins it.
  - `C:/Projects/_worktrees/SSH_DeviceManager/codex-constitution-hardening` → `codex/constitution-hardening` at `e103746`. Redundant: that commit is already on `main` via PR #15.
  - `C:/Projects/_worktrees/SSH_DeviceManager/codex-ops-roadmap-docs` → **do not remove yet.** See the salvage item under Documentation; it holds an unmerged commit with no remote branch, so removing it risks losing work.

  Note the last two are owned by the `KITT/CodexSandboxOffline` account, so a normal session cannot inspect them for uncommitted changes without a `git config --global --add safe.directory` exception.

## Refactoring

- [ ] Centralize Tk event-loop dispatch for UI state updates that can be requested from worker threads.
- [ ] Continue slimming `SSHGuiApp` by moving remaining direct UI workflow logic into focused controllers where tests can cover it independently.

## Testing

- [ ] Cover real Tk event-loop scheduling behavior for connection-state changes instead of relying only on mocks.
- [ ] Add a live-device smoke-test script or documented manual checklist for release candidates.
- [ ] Add measured coverage reporting and set an enforceable project floor after the first baseline.
- [ ] Close GAP-004: Paramiko is mocked everywhere, so neither resolved line is exercised against the real library. Since Python 3.8 resolves Paramiko 3.x and 3.9+ resolves 4.x, two distinct dependency lines ship with no unmocked coverage. A minimal smoke test against a local SSH server would cover both.

## Documentation

- [ ] Add screenshots or a short walkthrough for the main app and `customizer.py`.
- [ ] Document a recommended trusted-host onboarding workflow for strict host-key mode.
- [ ] Reconcile `docs/TEST_MATRIX.md` and `docs/READING_GUIDE.md` with the current suite. Both still declare 158 tests (142 unit + 16 integration) and were last updated 2026-06-06; the suite is now 176 (163 in `test_SSH_DeviceManager.py`, 13 in `test_customizer.py`). The counts were deliberately left unchanged rather than edited in isolation, because the matrix enumerates individual cases and needs the ~18 missing rows added, not just a new total.
- [x] Populate `docs/MEMORY.md` with the initial approved entries (Paramiko trust boundary, constitution pin rationale, Tk-mocked-at-import test behavior). Further entries remain user-discretionary and must be approved before being recorded.
- [ ] **Salvage the unmerged operator documentation on `codex-ops-roadmap-docs`.** Commit `fcfe4ec` ("docs: harden operator guidance", 2026-06-30) adds 335 lines across 9 files and never reached `main`. There is no pull request for it, so nothing else is tracking it.

  Every file on that branch is larger than its `main` counterpart: `docs/OPERATIONS.md` 52 → 82 lines (gaining whole "Environments" and "Safe Operations" sections `main` lacks), `docs/SETUP.md` 55 → 72, `docs/TROUBLESHOOTING.md` 47 → 56, `SECURITY.md` 16 → 33, `docs/ARCHITECTURE.md` 52 → 56. It also carries operational knowledge documented nowhere on `main` — checking `ssh_device_manager_startup_error.log` after a failed launch, deleting `ssh_device_manager_config.json` to reset saved profiles, and using `Config → Reload Sections` when not relying on the file watcher.

  **Treat this as content salvage, not a merge or cherry-pick.** The branch is 14 commits behind `main` and predates the 1.37.0/1.38.0 adoption work, so it conflicts across `COMMAND_REFERENCE.md` (which it restructures differently), `SECURITY.md`, `TODO.md`, `CHANGELOG.md`, and `docs/AGENT_HANDOFF.md` — all substantially rewritten since. The approach is to read its versions of `OPERATIONS.md`, `SETUP.md`, `TROUBLESHOOTING.md`, and `SECURITY.md`, then port what is still accurate onto current `main` as fresh edits.

  Its worktree at `C:/Projects/_worktrees/SSH_DeviceManager/codex-ops-roadmap-docs` is owned by the `KITT/CodexSandboxOffline` account, so git refuses to read it from a normal session. **Whether it holds uncommitted changes beyond `fcfe4ec` is unknown** — answering that needs a `git config --global --add safe.directory` exception first. Do not remove the worktree or delete the branch until this is resolved; the branch has no remote, so deleting it would lose the commit outright.

## Governance

- [x] Tag Constitution releases `v1.35.0` through `v1.37.0` in `esanacore/engineering-constitution`. Resolved upstream on 2026-07-19; tags through `v1.38.0` now exist, and `check_constitution_freshness.sh` reports `CURRENT`.
- [ ] Decide whether to adopt Constitution 1.38.0's repository-root cleanup. It relocates constitution-owned documents out of the root — `SECURITY.md` and `CONTRIBUTING.md` to `.github/`, `HELP.md` and `SYSTEM_PROMPT.md` to `docs/` — and `check_compliance.sh` accepts either location, so this is optional. Note `SECURITY.md` carries real project-specific content and would need to move with its content intact, not be regenerated from the template.
- [ ] Decide which vendor AI instruction files to keep. As of 1.38.0 they are opt-in (`bootstrap.sh --agents=<list>`) rather than installed by default, on the reasoning that adopting a framework should not double a project's root file listing. This repository still carries all 13 — `.cursorrules`, `.goosehints`, `.openhands_instructions`, `.agent-instructions.md`, `.project-rules.md`, `SYSTEM_PROMPT.md`, `COPILOT_INSTRUCTIONS.md`, `.antigravity/`, `.continue/`, `.aider.conf.yml`, and others — including for tools that may never be used here. Deleting the unused ones is a judgment call about which agents this project actually supports.
- [ ] Once the OTS inventory is confirmed complete, switch `.github/workflows/constitution-ots.yml` to `--strict` so an undocumented dependency fails the build.
- [ ] Consider switching `.github/workflows/constitution-tests.yml` and `constitution-doc-freshness.yml` to `--strict` after a period of warn-only observation.
- [ ] Wire `constitution/scripts/check_version_alignment.sh` into `.github/workflows/constitution-compliance.yml`. That workflow currently runs only `check_compliance.sh` and `check_traceability.sh`, so stale Constitution version references in governance docs are caught only when someone runs the checker by hand.
- [ ] Switch `.github/workflows/constitution-ots.yml` to `--strict` — the inventory is now complete and the checker passes in strict mode, so this is ready whenever you want it enforcing.

## Nice-to-Have

- [ ] Add import/export for reusable `sections.json` profiles.
