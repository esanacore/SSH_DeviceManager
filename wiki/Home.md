# Home

Welcome to the **SSH Device Manager** wiki. Wiki pages are authored under
`wiki/` in this repository and reviewed through normal pull requests.

## What this project does

A Python Tkinter GUI application for managing SSH connections and executing
commands on remote devices, using `paramiko` for SSH/SFTP. It provides a
configurable, themeable SSH command console (18 built-in themes) with a
separate GUI customizer and automatic configuration reload.

## Getting started

Run `SSH_DeviceManager.py`, the thin launcher shim. Install `paramiko` first;
`paramiko_compat.py` keeps imports clean when it is absent. See
`docs/SETUP.md`.

## How it works

`ssh_device_manager/` is the main package: `app.py` orchestrates the Tkinter
UI, `ssh_manager.py` wraps Paramiko, and focused controllers under
`controllers/` own connection lifecycle, SSH actions and uploads, profile
CRUD, and section loading/rendering. Configuration and profiles persist via
`config.py`; action buttons load from JSON via `sections_loader.py`.

## Where things live

- `ssh_device_manager/` — the package (models, themes, config, controllers)
- `SSH_DeviceManager.py` — launcher / backward-compat shim
- `constitution/` — Eric's Engineering Constitution submodule (read-only)

## See also

- `docs/HELP.md` — common questions and troubleshooting
- `TODO.md` — the living roadmap
