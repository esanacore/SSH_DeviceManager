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
  - `C:/Projects/_worktrees/SSH_DeviceManager/codex-ops-roadmap-docs` → **do not remove yet.** Its committed content is now salvaged, but the uncommitted question is still open — see the resolve item under Documentation. The branch has no remote, so removing it discards `fcfe4ec` outright.

  Note the last two are owned by the `KITT/CodexSandboxOffline` account, so a normal session cannot inspect them for uncommitted changes without a `git config --global --add safe.directory` exception.

## Architecture

- [ ] Decide whether to adopt Dependency Rule enforcement via `constitution/scripts/check_architecture.sh` (new in Constitution 1.39.0). Enforcement is opt-in and currently `SKIP`ped: it activates only when `docs/ARCHITECTURE.md` declares a `Layer Boundaries` table. A candidate layering is written there as prose — domain (models, constants, themes) → services (ssh_manager, config, validation, sections_loader, output, paramiko_compat) → controllers → ui (app.py).

  The blocker is structural, not clerical: the checker attributes imports by **path component**, and only `controllers` is currently a directory. The other three layers are individual modules and would need to become packages before they could be declared. That restructuring is the real decision here.

  **Gotcha worth knowing before anyone drafts a table**: `check_architecture.sh` parses the pipe table by text and does **not** respect HTML comment boundaries. A commented-out draft is still read as a live declaration, and one with unresolvable paths yields per-layer `WARN`s while still reporting "all dependencies point inward" — enforcement that appears active but verifies nothing. This was hit and reverted while adopting 1.39.0; the candidate layering is deliberately recorded as prose for that reason.

- [ ] Consider splitting `ssh_device_manager/app.py` (671 lines) and `test_SSH_DeviceManager.py` (2765 lines). Both exceed the architecture checker's advisory 600-line signal. These signals never fail the build by design — `constitution/ARCHITECTURE.md`'s SRP guardrail says not to split a module merely because it is long — so treat this as a prompt to look, not an instruction to split.

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
- [x] **Salvage the unmerged operator documentation on `codex-ops-roadmap-docs`** (committed content). Ported as fresh edits rather than merged: `docs/OPERATIONS.md` gained Environments and Safe Operations sections plus reset-profile, host-key-rollback, and configuration-drift guidance; `SECURITY.md` gained host-key verification detail, the warning that `sections.json` defines executable actions, and a done-vs-open checklist; `docs/TROUBLESHOOTING.md` gained corrupted-profile and broken-`sections.json` recovery; `docs/ARCHITECTURE.md` gained Key Design Constraints; `docs/SETUP.md` gained the writable-directory prerequisite and a validation section. Branch versions of `COMMAND_REFERENCE.md`, `TODO.md`, `CHANGELOG.md`, and `AGENT_HANDOFF.md` were deliberately dropped as superseded, as were its stale install instructions (Python 3.10 floor, `pip install paramiko`).
- [ ] **Resolve the `codex-ops-roadmap-docs` worktree before removing it.** The committed content is salvaged, but whether the worktree holds *uncommitted* changes beyond `fcfe4ec` is still unknown — it is owned by the `KITT/CodexSandboxOffline` account, so reading it requires `git config --global --add safe.directory C:/Projects/_worktrees/SSH_DeviceManager/codex-ops-roadmap-docs`. The branch has no remote, so deleting it discards `fcfe4ec` outright. Answer the uncommitted question first, then remove the worktree and branch.
## Governance

- [x] Tag Constitution releases `v1.35.0` through `v1.37.0` in `esanacore/engineering-constitution`. Resolved upstream on 2026-07-19; tags through `v1.38.0` now exist, and `check_constitution_freshness.sh` reports `CURRENT`.
- [ ] Decide whether to adopt Constitution 1.38.0's repository-root cleanup. It relocates constitution-owned documents out of the root — `SECURITY.md` and `CONTRIBUTING.md` to `.github/`, `HELP.md` and `SYSTEM_PROMPT.md` to `docs/` — and `check_compliance.sh` accepts either location, so this is optional. Note `SECURITY.md` carries real project-specific content and would need to move with its content intact, not be regenerated from the template.
- [ ] Decide which vendor AI instruction files to keep. As of 1.38.0 they are opt-in (`bootstrap.sh --agents=<list>`) rather than installed by default, on the reasoning that adopting a framework should not double a project's root file listing. This repository still carries all 13 — `.cursorrules`, `.goosehints`, `.openhands_instructions`, `.agent-instructions.md`, `.project-rules.md`, `SYSTEM_PROMPT.md`, `COPILOT_INSTRUCTIONS.md`, `.antigravity/`, `.continue/`, `.aider.conf.yml`, and others — including for tools that may never be used here. Deleting the unused ones is a judgment call about which agents this project actually supports.
- [ ] Once the OTS inventory is confirmed complete, switch `.github/workflows/constitution-ots.yml` to `--strict` so an undocumented dependency fails the build.
- [ ] Consider switching `.github/workflows/constitution-tests.yml` and `constitution-doc-freshness.yml` to `--strict` after a period of warn-only observation.
- [ ] Report two upstream inconsistencies to `esanacore/engineering-constitution`, both found while adopting 1.39.0:
  - `check_compliance.sh`'s placeholder detector matches any HTML comment marker, but `templates/docs/ARCHITECTURE.md` ships eight of them. An adopter who follows the template verbatim fails the `--strict` placeholder check on that file. Worked around here by writing the section as ordinary prose.
  - `check_architecture.sh` parses the `Layer Boundaries` pipe table by text without respecting HTML comment boundaries, so a commented-out draft table is read as a live declaration. When its paths do not resolve, the checker emits per-layer `WARN`s yet still summarizes "all dependencies point inward" — a false green. The two behaviors interact badly: the template tells adopters to keep the example table commented, which is exactly the state that produces the misleading result.
- [ ] Consider whether `BEHIND` should stay a hard version-gate failure. Upstream tagged two releases thirty minutes apart on 2026-07-19, and because `BEHIND` fails the build, every open pull request went red the moment the second landed — regardless of content. PR #23 had to be merged with a known-red `version-gate` whose failure was unrelated to the change. If the upstream release cadence stays this high, this converts routine work into constant submodule chasing.
- [ ] Wire `constitution/scripts/check_version_alignment.sh` into `.github/workflows/constitution-compliance.yml`. That workflow currently runs only `check_compliance.sh` and `check_traceability.sh`, so stale Constitution version references in governance docs are caught only when someone runs the checker by hand.
- [ ] Switch `.github/workflows/constitution-ots.yml` to `--strict` — the inventory is now complete and the checker passes in strict mode, so this is ready whenever you want it enforcing.

## Nice-to-Have

- [ ] Add import/export for reusable `sections.json` profiles.
