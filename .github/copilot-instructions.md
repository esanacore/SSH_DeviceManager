# SSH Device Manager - AI Coding Instructions

## Architecture Overview

SSH_DeviceManager is a **Tkinter GUI application** for remote device management via SSH/SFTP. The architecture consists of four distinct layers:

1. **Data Models** (`ActionButton`, `ButtonSection`): Dataclasses that define UI button structure and behavior
2. **SSH Manager** (`SSHManager`): Wraps Paramiko for SSH connections, command execution, and file transfers
3. **GUI App** (`SSHGuiApp`): Tkinter-based UI orchestrating connections, displaying output, managing theming
4. **Threading Layer**: Background worker threads ensure UI responsiveness during network operations

## Critical Architecture Patterns

### Thread-Safe Logging with Queue
All network operations run in daemon threads that communicate with the main UI thread via `self.log_queue` (a `queue.Queue`). The `log()` method safely timestamps and queues messages; `_start_log_poller()` runs on the main thread every 80ms to dequeue and display output.

**Example:** `SSHGuiApp.run_ssh_command()` spawns a thread, logs via `self.log()`, not direct output writes.

### Modular Button Sections
Buttons are organized into `ButtonSection` objects defined in `_define_sections()`. Each section has:
- `title`, `max_buttons` (hard limit), and a list of `ActionButton` objects
- Each button has `label`, `enabled` (visibility), `handler` (callable), and `tooltip`
- **Pattern:** Disabled buttons are excluded from rendering; enable them in `_define_sections()` when ready

### Theme System
`THEMES` dictionary maps theme names to color dictionaries. `apply_theme()` modifies `ttk.Style` and raw Tk widgets (the `Text` output widget). Themes are applied dynamically via menu selection; UI rebuilds happen only for non-ttk widgets.

### Host History (Combobox)
The host field uses `ttk.Combobox` with a special `<Clear History>` option. History persists only during runtime; it's not saved to disk.

## Key Developer Workflows

### Running Tests
```powershell
python -m unittest test_SSH_DeviceManager.py
```
Tests use `unittest.mock` to mock `paramiko`, `tkinter`, and file dialogs. Tkinter is mocked at import time in the test file (see line 4-7 in test file).

### Adding a New Button
1. In `_define_sections()`, add an `ActionButton` to the appropriate `ButtonSection`
2. Set `enabled=True` and provide a handler function (e.g., lambda calling `self.run_ssh_command()`)
3. Buttons with `enabled=False` are hidden until enabled
4. If max_buttons is exceeded, excess buttons are truncated with a warning logged

### Extending SSH Commands
Commands can be either predefined or custom (via dialog). All execute via `SSHManager.run_command()` which uses `client.exec_command()` (non-interactive). For interactive shells (network device paging), override with `client.invoke_shell()`.

### File Transfer
Two methods exist:
- `upload_config_template()`: Fixed remote path (/tmp/uploaded_config.txt)
- `send_file_scp()`: User-specified remote path via dialog
Both use SFTP under the hood (`SSHManager.upload_file()`).

## Project-Specific Conventions

### Connection Management
- `SSHManager.connect()` uses `paramiko.AutoAddPolicy()` for host key acceptance (production security warning in code)
- Timeout defaults: 10s for connection, 30s for commands
- `disconnect()` uses `contextlib.suppress()` to silently handle cleanup errors
- The `clear_creds_var` checkbox optionally clears password on disconnect (best practice)

### Output Handling
- Terminal output is read-only by default (disabled state)
- Editing only occurs in `_append_output()` method
- Output can be cleared, copied to clipboard, or saved to file via buttons
- All timestamps are added by `log()` in HH:MM:SS format

### Error Handling
- Connection errors are logged, not raised (background threads suppress exceptions)
- Disconnection is graceful (uses `suppress()` for both SFTP and SSH cleanup)
- Invalid UTF-8 bytes in output are replaced with U+FFFD (see `run_command()` decode with `errors="replace"`)

### Testing Pattern
Tests mock external dependencies (Paramiko, Tkinter, file dialogs) to avoid side effects. The test file mocks tkinter before importing the main module to prevent GUI initialization. All UI state is mocked; threading is mocked to run synchronously.

## References

### Key Files
- `SSH_DeviceManager.py` (949 lines): Main application; see `_define_sections()` for button layout, `apply_theme()` for theming, `_start_log_poller()` for queue handling
- `test_SSH_DeviceManager.py` (293 lines): Comprehensive unit tests covering data models, SSH manager, and GUI app
- `README.md`: Features, installation, usage, and test instructions

### Constants
- `COMMAND_HISTORY_LIMIT = 50`: Max recent commands cached
- Host history max: 10 entries (hardcoded in `on_host_selected()`)
- Default theme: "Default" (light colors)
- Queue poll interval: 80ms (see `_start_log_poller()`)

## Common Tasks

**Add a status check button:** Create an ActionButton in "Status" section with `handler=lambda: self.run_ssh_command("show status")`

**Add a new theme:** Add entry to `THEMES` dict, then select via Theme menu (auto-updates)

**Test a connection without connecting:** Use "Test Connection" button which spawns a temporary SSHManager, connects, and disconnects

**Access output programmatically:** Use `self.output_text.get("1.0", "end-1c")` to read all content as string
