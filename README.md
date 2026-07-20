# SSH Device Manager

<!-- CONSTITUTION_START -->
[![Eric's Engineering Constitution](https://img.shields.io/badge/Eric's%20Engineering%20Constitution-Adopted-blue)](https://github.com/esanacore/engineering-constitution)
<!-- CONSTITUTION_END -->


A Python Tkinter GUI application for managing SSH connections and executing commands on remote devices. Uses `paramiko` for SSH/SFTP. This project provides a configurable, themeable SSH command console with a separate GUI customizer and automatic configuration reload.

## Project Structure

```
ssh_device_manager/          # Main package
    __init__.py              # Re-exports public API
    models.py                # ActionButton, ButtonSection, ToolTip
    ssh_manager.py           # SSHManager (Paramiko wrapper)
    themes.py                # THEMES dictionary (18 built-in themes)
    config.py                # App config / profile persistence
    constants.py             # Shared app constants (limits, file paths)
    paramiko_compat.py       # Clean import when paramiko is absent
    sections_loader.py       # JSON section loading + handler resolution
    validation.py            # Input validation helpers
    output.py                # OutputManager (log queue, append, clear, copy, save, JSON export)
    app.py                   # SSHGuiApp (Tkinter orchestrator)
    controllers/             # Focused controllers
        connection.py        # Connection lifecycle
        actions.py           # SSH actions and file uploads
        profiles.py          # Profile CRUD
        sections.py          # Section loading, rendering, file watching

SSH_DeviceManager.py         # Thin launcher / backward-compat shim (49 lines)
test_SSH_DeviceManager.py    # 158 unit + integration tests
customizer.py                # Standalone sections.json editor
docs/                        # Test matrix, Gherkin specs, reading guide
```

## Highlights / What it can do now

- Connect to remote hosts via SSH (username/password).
- Execute predefined commands via configurable action buttons.
- Run custom commands through a prompt.
- Upload files via SFTP (template upload and user-specified remote path).
- Save and load connection profiles to/from a JSON config file.
- Per-field connection validation with specific error messages.
- Configurable host key policy (strict, warning, auto).
- Modular UI driven by `sections.json` (JSON): sections, buttons, labels, enabled state, and commands.
- `customizer.py`: visual editor to create/edit `sections.json` with a live preview.
- Auto-reload: main app watches the active `sections.json` and reloads the Actions panel when the file changes.
- 18 built-in themes (Default, Solarized Dark/Light, Dark Mode, Retro Terminal, Cyberpunk, Nord, Dracula, Gruvbox Dark/Light, Monokai Pro, One Dark, Tokyo Night, High Contrast, Catppuccin Mocha, Amber Terminal, NY Mets, NY Rangers) and easy theme additions.
- Thread-safe logging shown in the Terminal Output pane, plus copy/save/clear and structured JSON export options.
- Host history combobox with `<Clear History>` option (last 10 connections).

## Quick start

1. Clone the repository:

   ```bash
   git clone https://github.com/esanacore/SSH_DeviceManager
   cd SSH_DeviceManager
   ```

2. Create and activate a virtual environment (recommended).

3. Install dependencies from the manifest:

   ```bash
   pip install -e .
   ```

   Add contributor tooling (Pylint, flake8, pre-commit, build) with `pip install -e ".[dev]"`.

4. Launch the main app:

   ```bash
   python SSH_DeviceManager.py
   ```

   Installing also provides an `ssh-device-manager` command that launches the same GUI.

5. (Optional) Launch the customizer to edit the UI config visually:

   ```bash
   python customizer.py
   ```

6. After saving changes in `customizer.py`, the main app will automatically reload the configuration (or use Config ? Reload Sections).

## `sections.json` (configuration)

`sections.json` defines the UI layout and actions. Example:

```json
{
  "sections": [
    {
      "title": "Status",
      "max_buttons": 6,
      "actions": [
        { "label": "Show Version", "enabled": true, "command": "run:show version", "tooltip": "Runs: show version" }
      ]
    }
  ]
}
```

Supported command tokens:
- `run:...` - execute the right-hand string as an SSH command.
- `__upload_template__` - open file picker and upload via `upload_config_template()`.
- `__send_file__` - open SCP-style dialog and upload via `send_file_scp()`.
- `__custom_command__` - open the Run Custom Command dialog.

Rules:
- `enabled` controls visibility of buttons.
- `max_buttons` limits visible buttons; extras are truncated with a warning.
- Keep secrets out of `sections.json` - it is intended for UI metadata only.

## Themes

Change theme via the `Theme` menu. Add new themes by editing the `THEMES` dictionary in `ssh_device_manager/themes.py`, then select via the Theme menu (auto-updates).

Built-in themes: Default, Solarized Dark, Solarized Light, Dark Mode, Retro Terminal, Cyberpunk, Nord, Dracula, Gruvbox Dark, Gruvbox Light, Monokai Pro, One Dark, Tokyo Night, High Contrast, Catppuccin Mocha, Amber Terminal, NY Mets, NY Rangers.

## Security notes

- Default host key policy uses `paramiko.WarningPolicy()` (warns on unknown host keys). Configurable to strict (reject), warning (default), or auto (accept silently).
- Do not store credentials in `sections.json`.
- The "Clear credentials on disconnect" checkbox clears the password field on disconnect.
- Consider OS keyring integration for secure credential storage.

## Troubleshooting

- If no window appears or the app exits at startup, check `ssh_device_manager_startup_error.log` for a traceback.
- Verify `tkinter` and `paramiko` are installed and working.

## Tests

Run all unit and integration tests (mocks `tkinter`, `paramiko`):

```bash
python -m unittest test_SSH_DeviceManager.py -v
```

## Linting

Run repository lint checks with the same command used in CI:

```bash
pylint $(git ls-files '*.py')
```

Pylint behavior is configured via `.pylintrc` to keep checks practical for
this Tkinter-heavy application and the current test architecture.

Test documentation:
- `docs/TEST_MATRIX.md` - Test IDs, descriptions, and requirements traceability matrix
- `docs/TEST_GHERKIN.md` - Gherkin behavioral specifications (Given/When/Then)
- `docs/READING_GUIDE.md` - How to navigate the test documentation
- `docs/TEST_PLAN.md` - Constitution-aligned test strategy, coverage targets, and gap log
- `docs/PRODUCT_REQUIREMENTS.md` - Stable product requirement IDs and acceptance criteria
- `docs/REQUIREMENTS_TRACEABILITY.md` - Requirement-to-test verification matrix

## Constitution workflow

This repository adopts Eric's Engineering Constitution through the pinned `constitution/` submodule. The current branch pins the submodule to Constitution `1.39.0` on `main` and includes local guardrails for Constitution version checks, compliance checks, declared-test runs, documentation-freshness checks, secrets sweeps, OTS inventory cross-checks, environment-contract checks, architecture checks, Dependabot submodule updates, pre-commit, Aider, Continue, Goose, Solon, and devcontainers.

Start with:

- `AGENTS.md` for agent work rules
- `docs/ARCHITECTURE.md` for system boundaries and components
- `docs/SETUP.md` for local workstation setup
- `docs/COMMAND_REFERENCE.md` for validation commands
- `docs/OPERATIONS.md` for release and incident-response guidance
- `docs/SESSION_PLAN.md` for the current session's planned work (crash recovery)
- `docs/MEMORY.md` for durable project memory, learnings, and user preferences
- `docs/OTS_SOFTWARE.md` for the third-party dependency register
- `docs/ENV_VARS.md` for the environment and configuration contract
- `TODO.md` for the living roadmap

## Contributing & Workflow

- Create a branch for your changes and open a pull request for review.
- Keep `sections.json` free of credentials.
- See `CHANGELOG.md` for recent changes.

---

For more details, see the `docs/` directory and `.github/copilot-instructions.md`.
