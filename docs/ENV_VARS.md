# Environment & Configuration Contract

This document lists all environment variables required or optionally supported by this project.
It acts as the single source of truth for configuration parameters across development, staging, and production environments.

> [!IMPORTANT]
> If you add a new environment variable to a manifest (like `.env.example` or `docker-compose.yml`), you **must** document it in this file in the same pull request.

## Summary: This Project Uses No Environment Variables

SSH Device Manager is a local desktop application, not a deployed service. It reads **no** environment variables — a repository-wide scan for `os.environ`, `os.getenv`, and `environ[...]` across `ssh_device_manager/`, `SSH_DeviceManager.py`, and `customizer.py` returns nothing.

All configuration is file-based and user-facing, described under "File-Based Configuration" below. There is no `.env` file, no `.env.example`, and no container or orchestration manifest in this repository.

This is a deliberate design property rather than an oversight: connection details are entered in the GUI or loaded from a user-selected profile, so there is no deployment-time configuration surface to document.

## Required Variables

None. The application starts with no environment configuration.

## Optional Variables

None.

Standard interpreter and toolkit variables (`PYTHONPATH`, `DISPLAY` on Linux/X11, and similar) affect this application only in the ordinary way they affect any Python or Tk program. They are not read by this project's own code and are therefore out of scope for this contract.

## File-Based Configuration

Configuration this project *does* read, for completeness. These are runtime data files, not environment variables, and are not checked by `constitution/scripts/check_env_vars.sh`.

| File | Constant | Purpose | Created by |
| :--- | :--- | :--- | :--- |
| `ssh_device_manager_config.json` | `APP_CONFIG_FILE` in `ssh_device_manager/constants.py` | Saved connection profiles and app preferences | Written by the app when a profile is saved. Gitignored — it can contain hostnames and usernames |
| `sections.json` | `DEFAULT_SECTIONS_FILE` in `ssh_device_manager/constants.py` | Button section and action definitions loaded at startup, with automatic reload on change | Ships with the repository; editable by hand or through `customizer.py` |

Credentials are never persisted to either file. Passwords live only in memory for the duration of a session, and the `clear_creds_var` option clears them on disconnect. See `SECURITY.md`.

## Adding a Variable Later

If this project ever gains an environment variable, add a row to the appropriate table above **in the same change**, and delete the "Summary" section's claim that none exist. `constitution/scripts/check_env_vars.sh` cross-checks configuration manifests against this file and will flag an undocumented variable.
