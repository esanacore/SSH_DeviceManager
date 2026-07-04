# TODO

This file is the living roadmap for SSH Device Manager.

## Features

- [ ] Add OS keyring integration so users can opt into secure credential storage without writing passwords to repository or profile files.
- [ ] Add a real-device smoke-test checklist for SSH command execution and SFTP uploads against a disposable test host.

## Technical Debt

- [ ] Add a coverage tool and record the first measured line/branch coverage baseline in `docs/TEST_PLAN.md`.
- [ ] Add a dependency manifest for runtime and contributor tooling so Paramiko and Pylint setup is reproducible.

## Refactoring

- [ ] Centralize Tk event-loop dispatch for UI state updates that can be requested from worker threads.
- [ ] Continue slimming `SSHGuiApp` by moving remaining direct UI workflow logic into focused controllers where tests can cover it independently.

## Testing

- [ ] Cover real Tk event-loop scheduling behavior for connection-state changes instead of relying only on mocks.
- [ ] Add a live-device smoke-test script or documented manual checklist for release candidates.
- [ ] Add measured coverage reporting and set an enforceable project floor after the first baseline.

## Documentation

- [ ] Add screenshots or a short walkthrough for the main app and `customizer.py`.
- [ ] Document a recommended trusted-host onboarding workflow for strict host-key mode.

## Nice-to-Have

- [ ] Add import/export for reusable `sections.json` profiles.
