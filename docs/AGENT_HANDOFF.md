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

## Last Session — 2026-07-19: Constitution Patch Bump

- **Branch**: `chore/constitution-1.39.1`.
- **Scope**: Submodule pointer and version references only.
- **Nothing to adopt.** The patch release refactors the constitution's own `bootstrap.sh` into `scripts/lib/` and fixes a `.gitignore` bug in that repository. It changes no templates, adds no checkers, and introduces no required or recommended files, so for an adopting repository it is a pure pointer bump. Verified by diffing every template against its local copy: only `SECURITY.md` differs, which is project-specific by design.
- **Third bump in roughly one hour** (two minors, then this patch). Because `BEHIND` is a hard version-gate failure, PR #25 was merged with a known-red gate whose failure was unrelated to its content — the same call made earlier for PR #23. Whether `BEHIND` should stay hard-failing is logged in `TODO.md` under Governance.
- **Verification**: 176 tests pass; compliance `--strict --product`, secrets, OTS, env-vars, and architecture all pass under `--strict`; version alignment 0 mismatches; freshness `CURRENT`.

## Earlier Session — 2026-07-19: Operator Guidance Salvage

- **Branch**: `docs/salvage-operator-guidance`.
- **Scope**: Documentation only. No code, workflow, or submodule changes.
- **What**: Recovered commit `fcfe4ec` from `codex-ops-roadmap-docs` — 335 lines of operator documentation written 2026-06-30 that never reached `main` and had no pull request tracking it. Ported as fresh edits, not a merge: the branch is 14 commits behind and predates this sequence of Constitution adoption work entirely.
- **Method worth reusing**: each file was compared in *both* directions before deciding. `main` was better for `TROUBLESHOOTING.md` and `COMMAND_REFERENCE.md`, so most of the branch's versions were dropped; the branch was better for `OPERATIONS.md` and `SECURITY.md`. Its install instructions (Python 3.10 floor, `pip install paramiko`) were rejected outright as stale — porting them would have regressed documentation corrected earlier in this sequence.
- **Two carried-over claims were verified, not trusted**: `paramiko_compat.py` really is a stub fallback, and `TestContracts` really does cover `sections.json` schema (CT-03) and command tokens.
- **The branch and worktree are intentionally still in place.** Its committed content is salvaged, but whether the worktree holds *uncommitted* work beyond `fcfe4ec` is unknown — it is owned by the `KITT/CodexSandboxOffline` account and needs a `safe.directory` exception to read. The branch has no remote, so deleting it discards the commit outright. Tracked in `TODO.md` under Documentation.
- **Verification**: 176 tests pass; compliance `--strict --product`, secrets, OTS, env-vars, and architecture all pass under `--strict`; version alignment 0 mismatches; traceability 12/12; all internal document links resolve.

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
- **Unmerged operator documentation** sat on `codex-ops-roadmap-docs` with no remote branch. Its
  committed content is now salvaged onto `main`, but whether that worktree holds *uncommitted* work
  is still unknown, and the branch still has no remote. See the resolve item in `TODO.md` under
  Documentation before removing any worktree.

**Two checker traps, both still live.** Both were hit while adopting the architecture checker and
are logged in `TODO.md` under Governance for reporting upstream:

- **`check_architecture.sh` does not respect HTML comment boundaries.** It parses the
  `Layer Boundaries` pipe table by text, so a draft table sketched inside a comment is read as a
  live declaration. When its paths do not resolve, the checker emits per-layer `WARN`s but still
  summarizes "all dependencies point inward" — enforcement that appears active while verifying
  nothing. Never sketch a draft table in `docs/ARCHITECTURE.md`; the candidate layering there is
  deliberately written as prose.
- **`check_compliance.sh` treats any HTML comment marker as placeholder content**, failing that
  file under `--strict`. The upstream `docs/ARCHITECTURE.md` template ships eight of them, so
  following it verbatim breaks strict compliance. Avoid HTML comments in governance documents;
  use ordinary Markdown prose instead.

**`check_version_alignment.sh` cannot distinguish history from staleness.** It flags any semantic
version on a Constitution-related line, so deliberately historical references — "we upgraded from
X to Y" — read as stale claims. Describe history in prose or by commit SHA. This is why this file
carries one current session plus this section, rather than an accumulating per-session log.

## Handoff Note Template

When handing off work, include:

- Branch/worktree path.
- Files changed.
- Tests and Constitution checks run, with exact results.
- Any checks skipped and why.
- Security-sensitive decisions or remaining risks.
- Follow-up TODO entries created or completed.
