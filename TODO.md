# TODO

This file is the living roadmap for SSH Device Manager.

Keep entries specific, actionable, and current. When a gap in
`docs/TEST_PLAN.md` or `docs/REQUIREMENTS_TRACEABILITY.md` changes, update the
matching item here in the same commit.

## Features

- [ ] Add OS keyring-backed credential storage so operators can avoid repeated password entry without writing secrets into config files.
- [ ] Add import/export for connection profiles so shared device fleets can be onboarded without hand-entry.
- [ ] Add richer command-result filtering or search for long terminal-output sessions.

## Technical Debt

- [ ] Replace the remaining manual visual theme verification with a lightweight Tk smoke harness or snapshot strategy that can run headlessly.
- [ ] Add a small live-SSH integration harness for CI-optional verification of host-key modes, command execution, and SFTP behavior.

## Refactoring

- [ ] Continue shrinking Tkinter orchestration methods when new behavior appears, keeping controller and helper modules as the primary home for logic.
- [ ] Split `test_SSH_DeviceManager.py` into focused test modules when the single-file suite becomes materially harder to navigate.

## Testing

- [ ] Add optional real-server integration coverage for `FR-001` through `FR-003` so Paramiko interoperability is exercised beyond mocks.
- [ ] Add automated UI smoke checks for theme rendering, window startup, and section reload behavior.
- [ ] Publish line/branch percentages via `coverage.py` and enforce a documented floor in CI.

## Documentation

- [ ] Keep `docs/TEST_MATRIX.md`, `docs/TEST_PLAN.md`, and `docs/REQUIREMENTS_TRACEABILITY.md` aligned as the suite evolves.
- [ ] Document any future profile-export format or credential-storage behavior before shipping it.

## Nice-to-Have

- [ ] Add operator personas and recommended section-layout examples for common router, switch, and Linux maintenance workflows.
