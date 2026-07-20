# Test Plan

This document defines how SSH Device Manager is tested, what coverage is expected, and which gaps remain.

## How to Run Tests

This section is machine-readable. `constitution/scripts/run_declared_tests.sh` (invoked by
`.github/workflows/constitution-tests.yml`) extracts the `Full suite` command below and runs it,
so the command must stay a real, runnable one-liner.

- Full suite: `python -m unittest test_SSH_DeviceManager test_customizer -v`

## Test Commands

Primary suite:

```bash
python -m unittest test_SSH_DeviceManager.py test_customizer.py -v
```

Focused host-history regression:

```bash
python -m unittest test_SSH_DeviceManager.TestHostHistory test_SSH_DeviceManager.TestHostHistoryLimit -v
```

Constitution compliance:

```bash
"C:\Program Files\Git\bin\bash.exe" constitution/scripts/check_compliance.sh --strict --product .
"C:\Program Files\Git\bin\bash.exe" constitution/scripts/check_traceability.sh docs/PRODUCT_REQUIREMENTS.md docs/REQUIREMENTS_TRACEABILITY.md
```

Optional lint:

```bash
pylint $(git ls-files '*.py')
```

## Test Strategy

- **Unit tests** cover validation helpers, data models, theme contracts, output management and structured output export, config serialization, profile behavior, SSH manager behavior, and compatibility shims.
- **Controller tests** cover connection, action/upload, profile, and sections controllers with mocked UI/Paramiko dependencies.
- **Integration-style tests** exercise connect, command, disconnect, validation recovery, profile round trip, sections loading, and command failure workflows without requiring live SSH devices.
- **Contract tests** verify theme keys, sections schema, command tokens, profile schema, public SSHManager interface, and controller interfaces.

## Coverage Targets

| Area | Target | Notes |
| --- | --- | --- |
| Changed code | Regression test for every bug fix or behavior change | Required before implementation. |
| Core SSH/profile/config/controllers | Meaningful branch coverage through mocked unit tests | Live SSH devices are not required for default validation. |
| Product requirements | Every requirement ID maps to at least one verifying test | See `docs/REQUIREMENTS_TRACEABILITY.md`. |
| Governance docs/scripts | Constitution checks pass under `--strict --product` | Uses the pinned `constitution/` submodule. |

Line coverage is not currently measured in CI. The near-term target is to add a coverage command and record the first measured baseline here before enforcing a numeric floor.

## Continuous Coverage Record

| Date | Evidence | Notes |
| --- | --- | --- |
| 2026-06-30 | `Ran 171 tests in 0.515s` / `OK` | Baseline before host-history regression fix in `codex/constitution-hardening`. |
| 2026-06-30 | `Ran 172 tests in 0.634s` / `OK` | Full suite after host-history regression fix and Constitution documentation updates. |
| 2026-07-04 | `Ran 176 tests in 0.518s` / `OK` | Full suite after structured JSON output export and Constitution 1.29.0 alignment updates. |
| 2026-07-19 | `Ran 176 tests in 0.641s` / `OK` | Full suite after Constitution 1.37.0 alignment. Governance-only change; no runtime code touched. |
| 2026-07-19 | `Ran 176 tests in 0.6s` / `OK`; pylint `10.00/10` | Full suite after adding `pyproject.toml`. CI test matrix widened from 3.11/3.12 to 3.8–3.12, so the Python 3.8 compatibility restored in commit `e103746` is now test-verified rather than lint-verified only. |

## Coverage Gap Log

| Gap ID | Area / behavior | Risk | Related requirement | Status | TODO ref |
| --- | --- | --- | --- | --- | --- |
| GAP-001 | No measured line/branch coverage command or stored baseline. | Medium | NFR-003 | Open | `TODO.md` Testing |
| GAP-002 | No live-device smoke checklist for real SSH/SFTP behavior after mocked tests pass. | Medium | FR-001, FR-002, FR-003 | Open | `TODO.md` Testing |
| GAP-003 | UI thread-affinity behavior is tested through mocks but not exercised with a real Tk event loop. | Medium | NFR-001 | Open | `TODO.md` Testing |
| GAP-004 | Paramiko is mocked in every test, so neither resolved line is exercised against the real library. Python 3.8 resolves Paramiko 3.x and 3.9+ resolves 4.x, meaning two distinct dependency lines ship with zero unmocked coverage between them. | Medium | FR-001, FR-002 | Open | `TODO.md` Testing |
