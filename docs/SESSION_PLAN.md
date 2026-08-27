# Session Plan

This document records the current session's planned work before implementation begins. If this session is interrupted or crashes, the next agent or human can read this file to understand what was in progress and resume cleanly.

## Session

- **Date/Time**: 2026-08-27 19:07 UTC
- **Agent**: Antigravity
- **Previous Session**: Cleared; 2026-07-19 session completed.

## Goal

Ensure SSH_DeviceManager is fully working, compliant with Eric's Engineering Constitution 1.44.1, and implement OS Keyring Integration (FR-009) for secure credential storage.

## Approach

1. **Fix Declared Test Execution Command**: Update `docs/TEST_PLAN.md` line to use `python3 -m unittest test_SSH_DeviceManager test_customizer -v` so `run_declared_tests.sh` succeeds in Linux environments where `python` is not aliased.
2. **Update Constitution Version References**: Update references in `README.md`, `docs/AGENT_HANDOFF.md`, and `CHANGELOG.md` from `1.39.1` to `1.44.1` so `check_version_alignment.sh` passes.
3. **Align Release Tag**: Create and push tag `v0.3.0` matching `VERSION` (0.3.0) so `check_release_tag_alignment.sh` passes.
4. **Implement OS Keyring Integration (FR-009)**:
   - Create `ssh_device_manager/keyring_helper.py` with `is_keyring_available()`, `get_keyring_password()`, `set_keyring_password()`, and `delete_keyring_password()`.
   - Update `pyproject.toml` dependencies to include `keyring`.
   - Add UI control ("Save Password to Keyring" checkbox) to `SSHGuiApp` / `ProfileController` connection form.
   - Load password from keyring automatically when loading a profile/host if stored.
   - Delete/clear keyring entries when profiles are deleted or credentials cleared.
5. **Update Product Requirements & Traceability**:
   - Add `FR-009` to `docs/PRODUCT_REQUIREMENTS.md`.
   - Update `docs/REQUIREMENTS_TRACEABILITY.md` to map `FR-009` to new tests in `test_SSH_DeviceManager.py`.
   - Add `OTS-002` (`keyring`) to `docs/OTS_SOFTWARE.md`.
6. **Update Documentation & Roadmap**:
   - Update `CHANGELOG.md` under `## [Unreleased]` for Constitution 1.44.1 and OS Keyring Integration.
   - Check off keyring item in `TODO.md`.
7. **Verification**: Run `pytest` / unit tests (including new keyring tests) and all Constitution check scripts (`check_compliance.sh`, `check_version_alignment.sh`, `check_release_tag_alignment.sh`, `run_declared_tests.sh`, `check_architecture.sh`, `check_secrets.sh`, `check_ots_inventory.sh`, `check_env_vars.sh`, `check_wiki_links.sh`).

## Files Expected to Change

- `docs/SESSION_PLAN.md` — create/update session plan
- `docs/TEST_PLAN.md` — update declared test command to `python3`
- `README.md` — update constitution version reference to 1.44.1
- `docs/AGENT_HANDOFF.md` — update constitution version reference to 1.44.1
- `CHANGELOG.md` — update unreleased section
- `TODO.md` — mark keyring feature complete
- `pyproject.toml` — add `keyring` dependency
- `docs/PRODUCT_REQUIREMENTS.md` — add FR-009
- `docs/REQUIREMENTS_TRACEABILITY.md` — trace FR-009
- `docs/OTS_SOFTWARE.md` — add OTS-002 (keyring)
- `ssh_device_manager/keyring_helper.py` — [NEW] keyring wrapper module
- `ssh_device_manager/app.py` — add keyring UI checkbox & load/save handlers
- `ssh_device_manager/controllers/profiles.py` — wire profile load/save/delete to keyring helper
- `test_SSH_DeviceManager.py` — add unit tests for keyring integration (FR-009)

## Risks and Dependencies

- If system keyring service is not present (headless CI), `keyring_helper` must degrade gracefully without throwing exceptions.

## Resumption Notes

- **Last completed step**: Session plan and implementation plan updated.
- **Uncommitted changes**: `docs/SESSION_PLAN.md`
- **Known issues**: None.
