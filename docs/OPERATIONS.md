# Operations

SSH Device Manager is a local desktop application. There is no hosted production environment, database, server daemon, or scheduled job to operate.

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

4. Update `CHANGELOG.md` and `VERSION` for release candidates.
5. Open a review branch or pull request; do not merge directly to `main`.

## Monitoring & Observability

- **Runtime logs**: terminal output and the in-app Terminal Output pane.
- **Startup failures**: `ssh_device_manager_startup_error.log` in the project root.
- **Remote command evidence**: saved text output and structured JSON exports created through the app's output controls.
- **Metrics/alerts**: not applicable; this is not a hosted service.

## Backup And Restore

- Repository state is restored from Git.
- User-local profiles are stored in ignored `ssh_device_manager_config.json`; back up this file manually if profile recovery matters.
- `sections.json` is committed and restored with the repository.

## Rollback

Rollback is a Git operation: check out or reinstall the previous known-good commit/tag. For local user state, keep or restore the prior `ssh_device_manager_config.json` if the profile schema changes.

## Incident Response

1. Identify whether the issue is local startup, SSH connectivity, SFTP upload, configuration loading, or remote command behavior.
2. Preserve `ssh_device_manager_startup_error.log`, relevant saved text/JSON output, and the active `sections.json`.
3. Confirm no secrets were written to logs, JSON exports, `sections.json`, screenshots, or bug reports.
4. Reproduce with mocked tests when possible, then add or update a regression test before changing behavior.
5. Record follow-up work in `TODO.md`.
