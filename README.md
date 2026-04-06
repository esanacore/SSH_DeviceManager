# SSH Device Manager

A Python Tkinter GUI application for managing SSH connections and executing commands on remote devices. Uses `paramiko` for SSH/SFTP. This project provides a configurable, themeable SSH command console with a separate GUI customizer and automatic configuration reload.

## Project Structure

```
ssh_device_manager/          # Main package
    __init__.py              # Re-exports public API
    models.py                # ActionButton, ButtonSection, ToolTip
    ssh_manager.py           # SSHManager (Paramiko wrapper)
    themes.py                # THEMES dictionary
    config.py                # App config / profile persistence
    sections_loader.py       # JSON section loading + handler resolution
    validation.py            # Input validation helpers
    output.py                # OutputManager (log queue, append, clear, copy, save)
    app.py                   # SSHGuiApp (Tkinter orchestrator)

SSH_DeviceManager.py         # Thin launcher / backward-compat shim
test_SSH_DeviceManager.py    # 92 unit + integration tests
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
- Multiple built-in themes (Default, Solarized Dark/Light, Dark Mode, Retro Terminal, Cyberpunk) and easy theme additions.
- Thread-safe logging shown in the Terminal Output pane, plus copy/save/clear options.
- Host history combobox with `<Clear History>` option (last 10 connections).

## Quick start

1. Clone the repository:

   ```bash
   git clone https://github.com/esanacore/SSH_DeviceManager
   cd SSH_DeviceManager
   ```

2. Create and activate a virtual environment (recommended).

3. Install dependencies:

   ```bash
   pip install paramiko
   ```

4. Launch the main app:

   ```bash
   python SSH_DeviceManager.py
   ```

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
- `run:...` � execute the right-hand string as an SSH command.
- `__upload_template__` � open file picker and upload via `upload_config_template()`.
- `__send_file__` � open SCP-style dialog and upload via `send_file_scp()`.
- `__custom_command__` � open the Run Custom Command dialog.

Rules:
- `enabled` controls visibility of buttons.
- `max_buttons` limits visible buttons; extras are truncated with a warning.
- Keep secrets out of `sections.json` � it's intended for UI metadata only.

## Themes

Change theme via the `Theme` menu. Add new themes by editing the `THEMES` dictionary in `ssh_device_manager/themes.py`, then select via the Theme menu (auto-updates).

Built-in themes: Default, Solarized Dark, Solarized Light, Dark Mode, Retro Terminal, Cyberpunk.

## Security notes

- Default host key policy uses `paramiko.WarningPolicy()` (warns on unknown host keys). Configurable to strict (reject), warning (default), or auto (accept silently).
- Do not store credentials in `sections.json`.
- The "Clear credentials on disconnect" checkbox clears the password field on disconnect.
- Consider OS keyring integration for secure credential storage.

## Troubleshooting

- If no window appears or the app exits at startup, check `ssh_device_manager_startup_error.log` for a traceback.
- Verify `tkinter` and `paramiko` are installed and working.

## Tests

Run all 92 unit and integration tests (mocks `tkinter`, `paramiko`):

```bash
python -m unittest test_SSH_DeviceManager.py -v
```

Test documentation:
- `docs/TEST_MATRIX.md` � Test IDs, descriptions, and requirements traceability matrix
- `docs/TEST_GHERKIN.md` � Gherkin behavioral specifications (Given/When/Then)
- `docs/READING_GUIDE.md` � How to navigate the test documentation

## Contributing & Workflow

- Create a branch for your changes and open a pull request for review.
- Keep `sections.json` free of credentials.
- See `CHANGELOG.md` for recent changes.

---

For more details, see the `docs/` directory and `.github/copilot-instructions.md`.
