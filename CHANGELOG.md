# Changelog

All notable changes to the SSH_DeviceManager project will be documented in this file.

## [Unreleased]

### Added
- **Modular Package Architecture**:
    - Refactored 1,763-line monolith into `ssh_device_manager/` package with 8 focused modules.
    - `models.py`: ActionButton, ButtonSection, ToolTip data models.
    - `ssh_manager.py`: Paramiko wrapper (connect, disconnect, run_command, upload_file).
    - `themes.py`: THEMES dictionary with 6 built-in themes.
    - `config.py`: App config / profile persistence (load_app_config, save_app_config).
    - `sections_loader.py`: JSON section loading with handler token resolution.
    - `validation.py`: Connection form validation (get_connection_inputs, parse_int_input, get_host_key_mode).
    - `output.py`: OutputManager for thread-safe logging, append, clear, copy, save.
    - `app.py`: SSHGuiApp Tkinter orchestrator (slim, wires modules together).
    - `__init__.py`: Re-exports public API for backward compatibility.
    - `SSH_DeviceManager.py` is now a thin 26-line launcher/shim.
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
- **Test Documentation**:
    - `docs/TEST_MATRIX.md`: Test IDs, descriptions, requirements traceability matrix (40+ requirements).
    - `docs/TEST_GHERKIN.md`: 74 Gherkin behavioral specifications (Given/When/Then).
    - `docs/READING_GUIDE.md`: Guide to reading the test documentation.
- **Themes**:
    - Added "Cyberpunk" theme (Electric Blue, Bright Pink, Bright Yellow).
    - Reworked Solarized Dark to use canonical palette (base03 bg, base02 surfaces, blue selection, base01 borders).
    - Added btn_bg, border, label_fg keys to all themes for proper layering.

### Changed
- **Architecture**: Single-file monolith ? modular package with 8 modules.
- **Theme System**: Updated apply_theme to style buttons, borders, separators, checkbuttons, spinboxes.
- **Security Default**: Host key policy changed from AutoAddPolicy to WarningPolicy.
- **Test Count**: 19 ? 74 tests (58 unit + 16 integration).

### Fixed
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
