# Changelog

All notable changes to the SSH_DeviceManager project will be documented in this file.

## [Unreleased]

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
