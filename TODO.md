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
- [ ] Reconcile `docs/TEST_MATRIX.md` and `docs/READING_GUIDE.md` with the current suite. Both still declare 158 tests (142 unit + 16 integration) and were last updated 2026-06-06; the suite is now 176 (163 in `test_SSH_DeviceManager.py`, 13 in `test_customizer.py`). The counts were deliberately left unchanged rather than edited in isolation, because the matrix enumerates individual cases and needs the ~18 missing rows added, not just a new total.
- [ ] Populate `docs/MEMORY.md`. It was installed as an empty scaffold; per the constitution its entries are user-discretionary and must be approved before being recorded.

## Governance

- [ ] Tag Constitution releases `v1.35.0`, `v1.36.0`, and `v1.37.0` in `esanacore/engineering-constitution`. `VERSION` and `CHANGELOG.md` on `main` declare 1.37.0, but the newest Git tag is `v1.34.0`, so every adopting repository pinned to current `main` reports `AHEAD/DIVERGED` against the tag-based version gate instead of a clean `CURRENT`.
- [ ] Once the OTS inventory is confirmed complete, switch `.github/workflows/constitution-ots.yml` to `--strict` so an undocumented dependency fails the build.
- [ ] Consider switching `.github/workflows/constitution-tests.yml` and `constitution-doc-freshness.yml` to `--strict` after a period of warn-only observation.

## Nice-to-Have

- [ ] Add import/export for reusable `sections.json` profiles.
