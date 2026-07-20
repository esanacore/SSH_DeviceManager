# Operations

SSH Device Manager is a local desktop application. There is no hosted production environment, database, server daemon, or scheduled job to operate. The operational focus is safe local configuration, repeatable validation, and recoverable changes to `sections.json` and saved profiles.

## Environments

- **Developer workstation**: the primary environment. Run `SSH_DeviceManager.py`, edit `sections.json`, and execute the test suite locally.
- **Release-candidate checkout**: an optional clean clone used to confirm the app starts, tests pass, and the shipped `sections.json` still renders correctly before a tagged release.

## Release Procedure

1. Run the full test suite:

   ```bash
   python -m unittest test_SSH_DeviceManager.py test_customizer.py -v
   ```

2. Run Constitution checks:

   ```bash
   "C:\Program Files\Git\bin\bash.exe" constitution/scripts/check_compliance.sh --strict --product .
   "C:\Program Files\Git\bin\bash.exe" constitution/scripts/check_traceability.sh docs/PRODUCT_REQUIREMENTS.md docs/REQUIREMENTS_TRACEABILITY.md
   ```

3. Run lint where Pylint is installed:

   ```bash
   pylint $(git ls-files '*.py')
   ```

4. Launch `python SSH_DeviceManager.py` and confirm the GUI starts cleanly. If `sections.json` changed, also launch `python customizer.py` and verify the action layout still renders.
5. Update `CHANGELOG.md` and `VERSION` for release candidates.
6. Open a review branch or pull request; do not merge directly to `main`.
7. Follow [`docs/release-process.md`](release-process.md) for the GitHub workflow-driven release steps.

## Monitoring & Observability

- **Runtime logs**: terminal output and the in-app Terminal Output pane.
- **Startup failures**: `ssh_device_manager_startup_error.log` in the project root.
- **Remote command evidence**: saved text output and structured JSON exports created through the app's output controls.
- **Configuration drift**: `sections.json` and `ssh_device_manager_config.json` are the first files to inspect when UI actions or saved profiles behave unexpectedly.
- **Automated diagnostics**: the unittest suite and `pylint` are the supported pre-release health checks.
- **Metrics/alerts**: not applicable; this is not a hosted service.

## Safe Operations

- Keep secrets out of `sections.json`. It is committed UI metadata and must remain safe to commit — note that it also defines **executable** SSH commands, so treat its contents as code, not just labels.
- Use the default `warning` host-key mode unless there is an explicit reason to prefer `strict` or `auto`. Reserve `auto` for trusted lab environments.
- Back up `sections.json` and `ssh_device_manager_config.json` before risky edits, especially when restructuring button sections or replacing saved profiles.
- Prefer editing `sections.json` through `customizer.py` when you want a live preview and schema-conforming output.

## Backup And Restore

- **Repository state** is restored from Git; `sections.json` is committed and restored with it.
- **Back up**: copy `sections.json` and `ssh_device_manager_config.json` to a safe local location before large changes. The latter is gitignored, so Git will not recover it.
- **Restore**: replace the modified file with the backup copy and relaunch. If the UI still fails to start, inspect `ssh_device_manager_startup_error.log`.
- **Reset profiles**: delete or rename `ssh_device_manager_config.json` to let the app recreate a clean default profile store.

## Rollback

- **Code regressions**: check out the previous known-good commit or release tag and rerun the test suite.
- **Configuration regressions**: restore the last known-good `sections.json` and `ssh_device_manager_config.json`. Keep the prior config file if the profile schema changes.
- **SSH trust-policy mistakes**: switch the host-key mode back to `warning` or `strict` and reconnect, so the session uses the intended verification mode.

## Incident Response

1. Identify whether the issue is local startup, SSH connectivity, SFTP upload, configuration loading, or remote command behavior.
2. Preserve `ssh_device_manager_startup_error.log`, relevant saved text/JSON output, and the active `sections.json`.
3. Confirm no secrets were written to logs, JSON exports, `sections.json`, screenshots, or bug reports.
4. Reproduce with the documented validation commands to separate genuine code failures from workstation-specific SSH or Tkinter problems.
5. Restore the last known-good `sections.json` or `ssh_device_manager_config.json` if the incident is configuration-driven.
6. Reproduce with mocked tests when possible, then add or update a regression test before changing behavior.
7. Record follow-up work in `TODO.md`, and in `CHANGELOG.md` if the issue reveals a product or maintenance gap.
