# Session Plan

This document records the current session's planned work before implementation begins. If this session is interrupted or crashes, the next agent or human can read this file to understand what was in progress and resume cleanly.

**This file is overwritten at the start of each session.** Before overwriting, ensure the previous session's outcomes are captured in `AGENT_HANDOFF.md` or commit messages.

## Session

- **Date/Time**: 2026-07-19
- **Agent**: Claude (Claude Code)
- **Previous Session**: 2026-07-19 Constitution 1.37.0 alignment. Completed and merged into PR #20, all 15 CI checks green. This session is stacked on `chore/constitution-1.37.0-alignment` because it depends on `docs/OTS_SOFTWARE.md`, which only exists on that branch.

## Goal

Add a dependency manifest, closing the `TODO.md` Technical Debt item "Add a dependency manifest for runtime and contributor tooling so Paramiko and Pylint setup is reproducible."

This also activates the `constitution-ots.yml` CI gate, which currently reports "no declared third-party dependencies found in root-level manifests; nothing to verify" because there is no manifest to cross-check against the OTS inventory.

Decisions confirmed with the user before starting:

1. **Form**: `pyproject.toml` as the single source of truth (PEP 621), not `requirements.txt`.
2. **Python floor**: `>=3.8`, honoring commit `e103746`'s deliberate 3.8 typing-compatibility work and `pylint.yml`'s 3.8/3.9/3.10 matrix.
3. **Publishing**: fix `python-publish.yml` via the new packaging metadata rather than deleting the workflow.
4. **Paramiko constraint**: spec `paramiko>=3.4` rather than `>=4`. Paramiko 4.x declares `requires-python >=3.9`, so a `>=3.8` floor cannot use it. pip resolves paramiko 3.5.x on Python 3.8 and 4.x on 3.9+ automatically, with no environment markers needed.

## Findings That Shaped This Plan

- **`python-publish.yml` is already broken.** It ran once, on release `v0.2.0`, and failed in 11 seconds: `python -m build` has no `pyproject.toml` or `setup.py` to build from. Adding the manifest fixes a real, previously-failing release path.
- **The 3.8 support claim is only lint-verified, never test-verified.** Both `ci.yml` and `pylint.yml` name their job `build`, so the PR check list shows `build (3.8)` through `build (3.12)` and looks like full coverage. It is not: `pylint.yml` runs 3.8/3.9/3.10 but only invokes `pylint`, while `ci.yml` runs the actual unittest suite on 3.11/3.12 only. Nothing has ever run the test suite on 3.8. Declaring `requires-python = ">=3.8"` without fixing that would be an unverified claim.
- **The application code is genuinely 3.8-clean.** Scans found no PEP 585 builtin generics in annotations, no PEP 604 `X | Y` unions, no `match` statements, and no walrus operators in `ssh_device_manager/` or the root modules.

## Approach

1. Add `pyproject.toml` with PEP 621 metadata: `requires-python = ">=3.8"`, runtime dependency `paramiko>=3.4`, and a `dev` optional-dependency extra for `pylint`, `flake8`, `pre-commit`, and `build`.
2. Extend `ci.yml`'s matrix to 3.8/3.9/3.10 so the test suite actually runs on every version the manifest claims to support.
3. Update `docs/OTS_SOFTWARE.md`: Paramiko becomes genuinely manifest-declared, so its Version and Update Policy cells change, and the "Dependency Manifest Status" section describing the absent manifest must be rewritten.
4. Update `docs/SETUP.md` and `README.md` install instructions to use the manifest.
5. Update `TODO.md` (tick the Technical Debt item) and `CHANGELOG.md`.
6. Verify: `check_ots_inventory.sh` now cross-checks rather than skipping, full suite passes, `python -m build` succeeds locally, pylint stays at 10.00/10.

## Files Expected to Change

- `pyproject.toml` — create
- `.github/workflows/ci.yml` — modify (matrix)
- `docs/OTS_SOFTWARE.md` — modify
- `docs/SETUP.md`, `README.md` — modify
- `TODO.md`, `CHANGELOG.md` — modify
- `docs/SESSION_PLAN.md` — this file

## Risks and Dependencies

- **Stacked branch.** Depends on `chore/constitution-1.37.0-alignment` (PR #20) for `docs/OTS_SOFTWARE.md`. If #20 merges first this rebases trivially; if #20 changes substantially, revisit.
- **Python 3.8 is EOL** (October 2024), and a 3.8 user silently receives the older paramiko 3.x line rather than 4.x. Both facts must be recorded honestly in `docs/OTS_SOFTWARE.md` rather than glossed.
- **Packaging identity is a new decision surface.** Package name, entry points, and included packages did not previously exist anywhere in the repo; `SSH_DeviceManager.pyproj` is a Visual Studio project file, not Python packaging metadata.
- Adding 3.8/3.9/3.10 to the test matrix may surface genuine incompatibilities that the lint-only matrix never caught. If so, that is a real finding to report, not something to paper over by narrowing the matrix again.

## Resumption Notes

- **Last completed step**: All steps complete and verified.
- **Uncommitted changes**: None pending beyond the reviewed change set.
- **Outcome**: `pyproject.toml` added; `python -m build` verified producing a valid `ssh_device_manager-0.3.0` sdist and wheel with correct metadata (previously this path failed). CI test matrix widened to 3.8–3.12; `pylint.yml`'s job renamed `build` → `lint` to end the name collision that made 3.8 look test-covered. OTS gate now cross-checks rather than skipping, and passes `--strict`.
- **Known issues**: None blocking. GAP-004 logged in `docs/TEST_PLAN.md` — Paramiko is mocked everywhere, so neither the 3.x nor 4.x resolution path has unmocked coverage.
