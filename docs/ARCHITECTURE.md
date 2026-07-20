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

## Key Design Constraints

- The application must remain usable without a network connection to any hosted backend. Everything is local except the SSH/SFTP sessions it initiates.
- `sections.json` is operator-editable metadata, so malformed input must fail safely and predictably rather than crashing the UI.
- Tests mock `tkinter` and `paramiko` heavily so the suite runs headlessly on developer machines and in CI, with no display server and no reachable SSH host.
- Host-key verification must stay explicit and configurable rather than silently bypassed.

## Layer Boundaries

**No layer table is declared yet, and that is deliberate.** Dependency Rule enforcement via
`constitution/scripts/check_architecture.sh` activates only when this section contains a
`Layer Boundaries` pipe table. Until then the checker reports `SKIP` and emits advisory structural
signals only. Adopting enforcement is tracked in `TODO.md` under Architecture.

Two traps make this worth reading before anyone edits this section.

**Do not sketch a draft table here, not even inside an HTML comment.**
`check_architecture.sh` parses the table by text and does not respect comment boundaries, so a
commented-out example is still read as a live declaration. A draft whose paths do not resolve
produces per-layer `WARN`s but still summarizes "all dependencies point inward" — enforcement that
looks active while verifying nothing, which is worse than declaring no layers at all.

**Avoid HTML comments in this file entirely.** `check_compliance.sh` treats any comment marker as
placeholder content and fails the file under `--strict`. The upstream template for this document
ships several, so following it verbatim breaks strict compliance; this file uses ordinary prose
instead.

The candidate layering for this project, written as prose so it cannot be parsed as a declaration:

- **domain** (innermost, depends on nothing) — `models`, `constants`, `themes`
- **services** (may depend on domain) — `ssh_manager`, `config`, `validation`, `sections_loader`, `output`, `paramiko_compat`
- **controllers** (may depend on domain, services) — the `controllers` package
- **ui** (outermost) — `app.py`

Only `controllers` is currently a directory. The checker attributes imports by path component, so
the other three would each need to become a package before they could be declared as layer paths.
That restructuring is the substance of the decision, not a detail to settle at enforcement time.

Before declaring anything, confirm every existing import already complies. If any do not, that is a
real finding to fix or justify, not a reason to loosen the table. Once a real table exists, tighten
`.github/workflows/constitution-architecture.yml` to `--strict`.

## Architectural Decisions

Major decisions should be recorded in `docs/adr/`. The current package split favors a thin Tkinter composition root plus focused controllers so SSH behavior, configuration, output, and UI actions can be tested independently.
