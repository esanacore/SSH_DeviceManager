# Troubleshooting

## App Does Not Open

- **Symptoms**: Double-clicking or running `python SSH_DeviceManager.py` exits without a visible window.
- **Cause**: Startup exception, missing Tkinter, or an import/runtime problem.
- **Fix**: Open `ssh_device_manager_startup_error.log` in the project root and inspect the traceback. Then run from a terminal with `python SSH_DeviceManager.py` to see stderr output.

## Paramiko Is Missing

- **Symptoms**: Real connections fail immediately with a message that Paramiko is not installed.
- **Cause**: The active Python environment does not include Paramiko.
- **Fix**:

```bash
pip install paramiko
```

The tests use a compatibility shim, but real SSH/SFTP use requires the package.

## Unknown Host Key Prompts Or Warnings

- **Symptoms**: First connection to a host warns about an unknown host key, or strict mode rejects the host.
- **Cause**: The host key is not in the user's system known-hosts file.
- **Fix**: Prefer adding the host key through a trusted SSH workflow before using strict mode. Use `warning` for first-use visibility or `auto` only in trusted lab environments.

## Failed Hosts Appear In History

- **Symptoms**: A mistyped host remains in the host dropdown.
- **Cause**: Older versions remembered hosts before the connection succeeded.
- **Fix**: Use the current version, which records host history only after successful connection. Select `<Clear History>` to reset existing local history.

## `sections.json` Changes Do Not Appear

- **Symptoms**: The action panel still shows older buttons.
- **Cause**: The active sections file was not saved, has invalid JSON, or the watcher has not observed the timestamp change yet.
- **Fix**: Save the file, validate it as JSON, then use **Config > Reload Sections** in the app.

## Windows Cannot Run Bash Commands

- **Symptoms**: `bash` opens WSL errors or reports no distribution installed.
- **Cause**: Plain `bash` resolves to the Windows WSL shim.
- **Fix**: Use Git Bash explicitly:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' constitution/scripts/check_compliance.sh --strict --product .
```

## Saved Profiles Are Missing Or Corrupted

- **Symptoms**: Expected connection profiles are absent, or the app loads an empty profile list.
- **Cause**: `ssh_device_manager_config.json` was overwritten, malformed, moved, or hand-edited incorrectly.
- **Fix**:
  1. Inspect `ssh_device_manager_config.json` for malformed JSON.
  2. Restore it from a local backup if you keep snapshots — the file is gitignored, so Git cannot recover it.
  3. If recovery is impossible, delete or rename the file and let the app recreate a clean default profile store.

## Buttons Or Sections Disappear After Editing `sections.json`

- **Symptoms**: Expected actions do not render, or the app logs section-loading warnings after a config edit.
- **Cause**: Invalid JSON syntax, an unsupported command token, or `max_buttons` truncating more actions than expected.
- **Fix**:
  1. Open `sections.json` in `customizer.py`, which produces schema-conforming output, or validate the JSON manually.
  2. Run the suite — the contract tests cover `sections.json` shape and command tokens.
  3. Restore the last known-good backup of `sections.json` if needed.
