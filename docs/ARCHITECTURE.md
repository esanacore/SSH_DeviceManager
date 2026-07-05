# Architecture

SSH Device Manager is a local desktop utility for operating SSH-capable devices from a Tkinter interface. It runs entirely on the user's workstation and talks directly to remote SSH/SFTP endpoints through Paramiko.

## System Boundaries

- **Local desktop process**: Tkinter UI, configuration loading, profile persistence, and log display.
- **Remote device boundary**: SSH command execution and SFTP file upload over the network.
- **Local filesystem boundary**: `sections.json`, `ssh_device_manager_config.json`, saved text/JSON output logs, and startup error logs.

The application does not run a backend service, expose an HTTP API, or collect telemetry.

## Components

- `SSH_DeviceManager.py`: thin launcher and backward-compatible public API shim.
- `ssh_device_manager/app.py`: Tkinter composition root that wires widgets, controllers, themes, and persistence.
- `ssh_device_manager/controllers/connection.py`: connection lifecycle, host history, connection testing, and state polling.
- `ssh_device_manager/controllers/actions.py`: command execution and SFTP upload workflows.
- `ssh_device_manager/controllers/profiles.py`: connection profile save/load/delete behavior.
- `ssh_device_manager/controllers/sections.py`: configurable action-section loading and reload watching.
- `ssh_device_manager/ssh_manager.py`: Paramiko wrapper for SSH, command execution, and SFTP sessions.
- `ssh_device_manager/sections_loader.py`: validates and resolves `sections.json` commands into handlers.
- `ssh_device_manager/output.py`: queue-backed output rendering plus output save/copy/clear and structured JSON export helpers.
- `customizer.py`: standalone visual editor for `sections.json`.

## Data Flow

1. The user enters connection fields and selects a host key policy.
2. `ConnectionController` validates inputs and starts network work on a background thread.
3. `SSHManager` opens a Paramiko `SSHClient`, loads system host keys, applies the selected missing-host-key policy, and connects.
4. Successful connection attempts update host history; failed attempts are logged without being remembered.
5. Action buttons resolve to controller handlers that execute SSH commands or SFTP uploads.
6. Worker threads enqueue log messages; the Tk event loop drains them into the output pane.

## Security-Sensitive Areas

- SSH credentials are entered in the UI and intentionally not committed to repository files.
- `ssh_device_manager_config.json` stores profiles but not passwords.
- The default host key policy is `warning`; `strict` rejects unknown host keys and `auto` silently accepts them.
- `sections.json` can define remote commands, so it should be reviewed like executable configuration and kept free of secrets.

## Key Technologies

- Python 3
- Tkinter
- Paramiko
- `unittest` with extensive mocks for Tkinter and Paramiko
- Pylint for static linting

## Architectural Decisions

Major decisions should be recorded in `docs/adr/`. The current package split favors a thin Tkinter composition root plus focused controllers so SSH behavior, configuration, output, and UI actions can be tested independently.
