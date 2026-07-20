# Session Plan

This document records the current session's planned work before implementation begins. If this session is interrupted or crashes, the next agent or human can read this file to understand what was in progress and resume cleanly.

**This file is overwritten at the start of each session.** Before overwriting, ensure the previous session's outcomes are captured in `AGENT_HANDOFF.md` or commit messages.

## Session

- **Date/Time**: 2026-07-19
- **Agent**: Claude (Claude Code)
- **Previous Session**: Constitution 1.39.0 update, merged as PR #24. Working tree clean, `main` current at `CURRENT (v1.39.0)`.

## Goal

Salvage the unmerged operator documentation from `codex-ops-roadmap-docs`, per the `TODO.md` item under Documentation. Commit `fcfe4ec` ("docs: harden operator guidance", 2026-06-30) adds 335 lines across 9 files and never reached `main`; there is no pull request tracking it.

## Approach

**This is content salvage, not a merge or cherry-pick.** The branch is 14 commits behind `main` and predates the 1.37.0–1.39.0 adoption work, so a merge would conflict across most of the files it touches. Branch content is read via `git show codex-ops-roadmap-docs:<file>` and ported as fresh edits onto current `main`.

Each file was compared in both directions before deciding. Where `main` is already better, the branch content is deliberately dropped rather than merged in.

### Per-file decisions

- **`docs/OPERATIONS.md`** — port the most. Branch has two whole sections `main` lacks: **Environments** (developer workstation, release-candidate checkout) and **Safe Operations** (keep secrets out of `sections.json`, host-key mode guidance, back up before risky edits, prefer `customizer.py`). Also port the "reset profiles" restore path, host-key rollback, configuration-drift diagnostics, and a link to `docs/release-process.md` — which exists but `main` never references. Keep `main`'s constitution checks, JSON-export evidence, and secrets-review step, which the branch predates.
- **`SECURITY.md`** — port the host-key verification paragraph (`auto` reserved for trusted labs), the warning that `sections.json` drives **executable** SSH actions so secrets must stay out of labels/tooltips/command text, and the scrubbed-test-host guidance for logs. Adopt the branch's convention of marking checklist items done vs open, which is more informative than `main`'s all-unchecked list. Keep `main`'s LAN-exposure and JSON-export items.
- **`docs/TROUBLESHOOTING.md`** — port only **"Saved profiles are missing or corrupted"**. Everything else on the branch is covered by `main` in equal or better form; `main` additionally has Paramiko-missing, failed-hosts-in-history, and Windows-bash entries the branch lacks.
- **`docs/ARCHITECTURE.md`** — port **Key Design Constraints** (four constraints, all still accurate).
- **`docs/SETUP.md`** — port the writable-working-directory prerequisite and a validation section. `main`'s Configuration Files section already covers all three persistent files.

### Deliberately dropped

- Branch `docs/COMMAND_REFERENCE.md` — restructures the file in a style `main` no longer uses, and `main`'s version (rewritten in PR #23) documents all eight constitution checkers, which the branch predates entirely. Its one unique contribution, the "Common Local Workflows" tips, is folded into `docs/TROUBLESHOOTING.md` and `docs/OPERATIONS.md` where it fits better.
- Branch `TODO.md`, `CHANGELOG.md`, `docs/AGENT_HANDOFF.md` — all substantially rewritten since; branch versions are stale.
- Branch `docs/SETUP.md` install instructions — say "Python 3.10 or newer" and `pip install paramiko pylint`. Both are now wrong: the declared floor is `>=3.8` and installation goes through `pip install -e .`.

## Files Expected to Change

- `docs/OPERATIONS.md`, `SECURITY.md`, `docs/TROUBLESHOOTING.md`, `docs/ARCHITECTURE.md`, `docs/SETUP.md` — modify
- `TODO.md`, `CHANGELOG.md`, `docs/SESSION_PLAN.md` — modify

## Risks and Dependencies

- **Do not delete the branch or its worktree as part of this session.** It has no remote, so the commit exists only there. Removal is a separate decision once the salvage is confirmed complete.
- Whether the worktree holds **uncommitted** changes beyond `fcfe4ec` is still unknown — it is owned by the `KITT/CodexSandboxOffline` account and cannot be read without a `git config --global --add safe.directory` exception. This salvage covers the committed content only.
- Some branch content is confidently stale (Python 3.10 floor, `pip install paramiko`). Porting it verbatim would regress documentation corrected earlier in this sequence — every ported passage is checked against current reality rather than copied.
- Avoid HTML comments in any edited governance document: `check_compliance.sh` treats a comment marker as placeholder content and fails the file under `--strict`.

## Resumption Notes

- **Last completed step**: Plan written; per-file decisions made; implementation starting.
- **Uncommitted changes**: None yet.
- **Known issues**: None yet.
