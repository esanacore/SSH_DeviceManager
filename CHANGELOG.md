# Changelog

All notable changes to the SSH_DeviceManager project will be documented in this file.

## [Unreleased]

### Added
- **Operator Guidance (salvaged from unmerged work)**:
    - Recovered documentation from commit `fcfe4ec` on `codex-ops-roadmap-docs`, which was written 2026-06-30 and never merged. Ported as fresh edits rather than a merge, since the branch predates the Constitution 1.37.0–1.39.0 work and conflicts with it.
    - `docs/OPERATIONS.md`: added **Environments** and **Safe Operations** sections, plus configuration-drift diagnostics, a profile-reset restore path, host-key trust rollback, and a link to `docs/release-process.md`.
    - `SECURITY.md`: documented host-key mode guidance (`auto` reserved for trusted labs), warned that `sections.json` defines **executable** SSH actions rather than just labels, and reworked the checklist to distinguish properties the code already holds from open work.
    - `docs/TROUBLESHOOTING.md`: added recovery for corrupted saved profiles and for `sections.json` edits that make buttons disappear.
    - `docs/ARCHITECTURE.md`: added **Key Design Constraints**.
    - `docs/SETUP.md`: added the writable-working-directory prerequisite and a post-setup validation section.

- **Engineering Constitution 1.39.0**:
    - Advanced the pinned `constitution/` submodule to Constitution `1.39.0`; `check_constitution_freshness.sh` reports `CURRENT`.
    - Added `.github/workflows/constitution-architecture.yml`, which runs the new `check_architecture.sh` — the first constitution checker that inspects code structure rather than file presence.
    - Added a `Layer Boundaries` section to `docs/ARCHITECTURE.md` recording a candidate layering for this project. Dependency Rule enforcement is opt-in and deliberately left **off**: only `controllers` is currently a directory, and the checker attributes imports by path component, so the other three candidate layers would need to become packages first. The checker reports `SKIP` with 0 violations. Advisory structural signals flag `app.py` (671 lines) and `test_SSH_DeviceManager.py` (2765 lines); these never fail the build by design.

- **Engineering Constitution 1.38.0**:
    - Advanced the pinned `constitution/` submodule to Constitution `1.38.0`; `check_constitution_freshness.sh` reports `CURRENT`.
    - Added `docs/ENV_VARS.md`, the Environment & Configuration Contract, and the `constitution-env.yml` CI gate that cross-checks it. This project reads no environment variables, so the document records that explicitly and describes the file-based configuration (`ssh_device_manager_config.json`, `sections.json`) used instead.
    - Refreshed `CONTRIBUTING.md` and `HELP.md` from the 1.38.0 templates. `SECURITY.md` was intentionally left in place — its structure matches the template but its content is real project-specific security guidance where the template ships placeholders.
- **Dependency Manifest (`pyproject.toml`)**:
    - Added PEP 621 packaging metadata as the single source of truth for dependencies, closing the long-standing "add a dependency manifest" roadmap item.
    - Runtime dependency is `paramiko>=3.4`; contributor tooling (Pylint, flake8, pre-commit, build) lives in a `dev` optional extra installed with `pip install -e ".[dev]"`.
    - Version is read dynamically from the existing `VERSION` file rather than duplicated, so there is no second copy to drift.
    - Declares `requires-python = ">=3.8"`, honoring the 3.8 typing compatibility deliberately restored in commit `e103746`.
    - Installing now provides an `ssh-device-manager` GUI entry point.
- **Reproducible CI dependency setup**: `ci.yml` and `pylint.yml` now install from the manifest (`pip install -e .` / `.[dev]`) instead of naming packages inline, so CI exercises the same resolution a user gets.

- **Engineering Constitution 1.37.0 Alignment**:
    - Advanced the pinned `constitution/` submodule from `v1.30.0` to Constitution `1.37.0` on `main`.
    - Added `docs/OTS_SOFTWARE.md`, the off-the-shelf software inventory, with real entries for Paramiko (assessed High risk as the credential-handling and host-key trust boundary), CPython, Tk/Tcl, and Pylint.
    - Added `docs/SESSION_PLAN.md` for crash-recovery session planning and `docs/MEMORY.md` as the durable project-memory scaffold.
    - Added four CI gates: `constitution-tests.yml` (runs the suite declared in `docs/TEST_PLAN.md`, wired to Python 3.12 + Paramiko), `constitution-doc-freshness.yml`, `constitution-secrets.yml`, and `constitution-ots.yml`.
    - Added `.claude/settings.json` with the `SessionStart` hook that reports constitution staleness at the start of every Claude Code session.
    - Added a machine-readable `## How to Run Tests` section to `docs/TEST_PLAN.md` so the declared-test CI gate can find the full-suite command.
    - Refreshed every agent instruction file against the 1.37.0 templates, picking up `CODE_STYLE.md`, session planning, and project memory. Project-specific architecture guidance in `.github/copilot-instructions.md` was preserved and given an explicit constitution section.

- **Engineering Constitution Completion**:
    - Updated the pinned `constitution/` submodule from `v1.20.0` to Constitution `1.29.0` on `main`.
    - Added Constitution adoption guardrails for version checks, compliance checks, Dependabot submodule updates, pre-commit, Aider, Continue, Goose, Solon, and devcontainers.
    - Added project-specific product requirements, requirements traceability, and test plan documentation.
    - Replaced template setup, command reference, troubleshooting, architecture, operations, and roadmap content with SSH Device Manager-specific guidance.
- **Structured Output Export**:
    - Added an `Export JSON` control for terminal output.
    - Exported payloads include a format ID, UTC timestamp, line count, line list, and raw output text for downstream troubleshooting or audit workflows.
- **Controller Layer Refactor**:
    - Added `ssh_device_manager/controllers/` with focused controllers for connection lifecycle, SSH actions/uploads, profile CRUD, and sections loading/rendering/watching.
    - Added `constants.py` to centralize shared app constants.
    - Added `paramiko_compat.py` so the app and tests can import cleanly even when `paramiko` is not installed in the active interpreter.
- **Modular Package Architecture**:
    - Refactored 1,763-line monolith into `ssh_device_manager/` package with 8 focused modules.
    - `models.py`: ActionButton, ButtonSection, ToolTip data models.
    - `ssh_manager.py`: Paramiko wrapper (connect, disconnect, run_command, upload_file).
    - `themes.py`: THEMES dictionary with 18 built-in themes.
    - `config.py`: App config / profile persistence (load_app_config, save_app_config).
    - `sections_loader.py`: JSON section loading with handler token resolution.
    - `validation.py`: Connection form validation (get_connection_inputs, parse_int_input, get_host_key_mode).
    - `output.py`: OutputManager for thread-safe logging, append, clear, copy, save.
    - `app.py`: SSHGuiApp Tkinter orchestrator (slim, wires modules together).
    - `__init__.py`: Re-exports public API for backward compatibility.
    - `SSH_DeviceManager.py` is now a thin 49-line launcher/shim.
- **Connection Profiles**:
    - Save, load, and delete connection profiles (host, port, username, timeout, host key mode).
    - Profiles persist to `ssh_device_manager_config.json`.
- **Per-Field Validation**:
    - Each missing or invalid connection field is reported with a specific error message.
    - Validates host, username, password, port (1-65535), and timeout (1-300).
    - Catches TclError for blank IntVar fields (port, timeout).
- **Specific Error Handling**:
    - AuthenticationException, SSHException, and OSError each produce distinct, actionable error messages in both on_connect and test_connection.
- **Host Key Policy**:
    - Configurable host key policy: strict (RejectPolicy), warning (WarningPolicy, default), auto (AutoAddPolicy).
- **Integration Tests** (16 new):
    - Full connect ? run ? disconnect lifecycle.
    - Auth failure recovery (wrong password ? fix ? retry succeeds).
    - Validation blocks connect then succeeds after fixing fields.
    - Profile save ? load ? connect workflow.
    - Sections JSON loading (valid, missing, invalid, empty).
    - Command history ordering, deduplication, and limit enforcement.
    - Command failure handling (error logged, disconnect still works).
    - Config file round-trip (save to disk ? reload ? data intact).
    - Host history capped at 10 entries.
    - Disconnect credential clearing (enabled/disabled).
- **Unit Test Expansion** (18 new):
    - SSHManager: stderr capture, host key policy per mode, upload-not-connected guard, SFTP session reuse.
    - SSHGuiApp: save-empty guard, save-write-error handling, clear output, double-click connect guard, run-command-not-connected, upload-not-connected, upload-cancelled, log timestamp format.
    - Profiles: load-missing-profile error, save-via-dropdown-name fallback.
    - Connection State Monitor: detect dropped connection, no false alarm when disconnected.
- **Test Documentation**:
    - `docs/TEST_MATRIX.md`: Test IDs, descriptions, requirements traceability matrix (40+ requirements).
    - `docs/TEST_GHERKIN.md`: 92 Gherkin behavioral specifications (Given/When/Then).
    - `docs/READING_GUIDE.md`: Guide to reading the test documentation.
- **Themes**:
    - Added "Cyberpunk" theme (Electric Blue, Bright Pink, Bright Yellow).
    - Reworked Solarized Dark to use canonical palette (base03 bg, base02 surfaces, blue selection, base01 borders).
    - Added btn_bg, border, label_fg keys to all themes for proper layering.
    - Added 12 new themes: Nord, Dracula, Gruvbox Dark, Gruvbox Light, Monokai Pro, One Dark, Tokyo Night, High Contrast, Catppuccin Mocha, Amber Terminal, NY Mets, NY Rangers.
    - Total built-in themes expanded from 6 to 18.
- **Startup Error Logging**:
    - The launcher (`SSH_DeviceManager.py`) now catches unexpected startup exceptions and writes a full traceback to `ssh_device_manager_startup_error.log`, so non-terminal users can diagnose startup failures.
- **Contract Tests** (7 new):
    - Theme color values are valid hex (`CT-01`), theme keys match `apply_theme()` usage (`CT-02`).
    - `sections.json` schema validation (`CT-03`) and command token validation (`CT-04`).
    - Profile config round-trip schema (`CT-05`).
    - `SSHManager` public interface contract (`CT-06`), controller interface contract (`CT-07`).

### Changed
- **App Composition**:
    - Reduced `SSHGuiApp` so it acts primarily as the Tkinter composition root and delegates major behaviors to controllers.
    - Kept the existing public `SSHGuiApp` methods and the top-level `SSH_DeviceManager.py` shim stable for backward compatibility and test compatibility.
- **Test Harness Compatibility**:
    - Updated imports so the launcher shim and package use the same `paramiko` compatibility path.
    - Relaxed a brittle `customizer` save test that incorrectly assumed app initialization performed no file reads.
- **Architecture**: Single-file monolith ? modular package with 8 modules.
- **Theme System**: Updated apply_theme to style buttons, borders, separators, checkbuttons, spinboxes.
- **Security Default**: Host key policy changed from AutoAddPolicy to WarningPolicy.
- **Test Count**: 19 → 158 tests (142 unit + 16 integration).

### Security
- **Secrets Coverage in `.gitignore`**:
    - Added ignore rules for environment files, SSH private keys (`id_rsa`, `id_ed25519`, `*_rsa`, and friends), service-account JSON, `.netrc`, and Terraform state. This project handles SSH passwords and private key material, and the constitution secrets sweep previously reported six coverage gaps; `check_secrets.sh --strict` now passes.

### Fixed
- **Dependency Manifest Fixes**:
    - **Release publishing was broken.** `python-publish.yml` runs `python -m build`, but the repository had no `pyproject.toml` or `setup.py` to build from — the workflow failed in 11 seconds the one time it ran, on release `v0.2.0`. The new manifest fixes that path; `python -m build` now produces a valid sdist and wheel.
    - **Python 3.8 support was claimed but never tested.** `ci.yml` ran the suite on 3.11/3.12 only while `pylint.yml` linted 3.8/3.9/3.10. Because both workflows named their job `build`, the check list rendered as `build (3.8)`..`build (3.12)` and looked like full coverage. The test matrix now spans 3.8–3.12, and the lint job is renamed `lint` so the two are distinguishable.
    - Corrected `docs/SETUP.md`, which required "Python 3.10 or newer" — inconsistent with both the lint matrix and the newly declared `>=3.8` floor.
    - **`ci.yml` never ran on stacked pull requests.** Its trigger was `pull_request: branches: [main]`, so a pull request based on any branch other than `main` skipped the test suite entirely. The branch filter is removed, matching every `constitution-*` workflow.
- **Constitution 1.37.0 Alignment Fixes**:
    - Corrected stale test counts in `.github/copilot-instructions.md`, which claimed 100 tests against an actual suite of 176.
    - Corrected the stale Constitution version reference in `README.md`, which claimed `1.29.0`.
    - Removed duplicated top-level headings in `docs/READING_GUIDE.md`, `docs/TEST_GHERKIN.md`, `docs/TEST_MATRIX.md`, and `.github/copilot-instructions.md`.
- **Host History Accuracy**:
    - Host history now records only successful SSH connections, preventing failed or mistyped hosts from polluting the dropdown.
- **Pylint CI Stability**:
    - Fixed `E0602` in `ssh_device_manager/app.py` by importing `queue` where `queue.Queue()` is used.
    - Updated `SSH_DeviceManager.py` launcher lint issues (split imports, added `main()` docstring, and exception chaining with `raise SystemExit(1) from exc`).
    - Replaced direct protected-call usage in `app.py` output helper with a public `OutputManager.append()` wrapper.
    - Added repository `.pylintrc` so `pylint $(git ls-files '*.py')` passes in CI without broad architectural refactors.
- **Refactor Safety**:
    - Verified the full local suite after the controller extraction and compatibility changes: 105 tests passing (`test_SSH_DeviceManager.py` and `test_customizer.py`).
- **Command History Dedup Bug**: `run_ssh_command` could insert duplicate entries when re-running a command already deeper in the history list. Fixed to remove-then-insert.
- Restored missing `import json` and `from tkinter import filedialog, messagebox, ttk` imports that were accidentally dropped.
- Fixed Dark Mode text_fg key typo (textFg ? text_fg).

---

## [Previous]

### Added
- **Themes**:
    - Added "Cyberpunk" theme (Electric Blue, Bright Pink, Bright Yellow).
- **Help Menu**: Added a "Help" menu with an "About / Usage" dialog providing a quick guide to features and usage.
- **File Transfer**:
    - Added "Send File via SCP" button to the Maintenance section.
    - Implemented a dialog to specify the remote destination path for uploads.
- **Theme Support**: Introduced a theming system with a "Theme" menu.
    - Added "Default" (Light) theme.
    - Added "Solarized Dark" and "Solarized Light" themes.
    - Added "Dark Mode" (Universal dark theme).
    - Added "Retro Terminal" (Black & Green high-contrast theme).
- **Host History**:
    - Replaced the "Host / IP" entry field with a `Combobox`.
    - Implemented history tracking for successful connections (last 10 hosts).
    - Added a `<Clear History>` option to the dropdown to reset the list.
- **Window Management**:
    - Increased default window size to 1400x900.
    - Added logic to auto-maximize the window on startup (supports Windows and Linux/X11).
- **Unit Tests**:
    - Created a comprehensive test suite in `test_SSH_DeviceManager.py`.
    - Covered Data Models, SSHManager, and SSHGuiApp functionality.
    - Added documentation for running tests in `README.md`.

### Changed
- **UI Layout**:
    - Improved button section layout using `grid` with uniform column weights for even distribution.
    - Added visual spacing between "Help" and "Theme" menus.
    - Swapped `ttk.Entry` for `ttk.Combobox` for host input.
    - Updated `README.md` with detailed features, requirements, installation, and usage instructions.
- **Code Structure**:
    - Refactored `SSHGuiApp` to support dynamic theme application via `ttk.Style`.
    - Added `THEMES` dictionary to centralize color definitions.

### Fixed
- Addressed various code analysis warnings (e.g., broad exception handling, unused variables).
