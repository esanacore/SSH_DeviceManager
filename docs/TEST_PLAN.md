# Test Plan

This document defines how SSH Device Manager is tested, what quality floor the
current suite is expected to hold, and which important behaviors still rely on
manual or future verification.

It is a living document. Update it whenever the test strategy, commands, or
known coverage gaps change.

## Test Strategy

SSH Device Manager is a desktop Tkinter application with most behavior pushed
into testable modules. The repository currently leans on deterministic
logic-level tests and mocked UI seams rather than brittle full-desktop UI
automation.

- **Unit tests**: `test_SSH_DeviceManager.py` exercises the data models, SSH
  manager, validation helpers, output manager, theme contracts, and controller
  logic with mocked Paramiko/Tkinter boundaries.
- **Integration tests**: the same suite includes end-to-end-in-process flows
  for connect-run-disconnect, profile workflows, config round-trips, sections
  loading, command-history behavior, and credential clearing.
- **Manual / visual verification**: theme appearance, widget spacing, window
  geometry, and real-network SSH behavior are still checked manually when those
  areas change.

## How to Run Tests

- Full suite: `python -m unittest test_SSH_DeviceManager.py -v`
- Syntax check: `python -m py_compile SSH_DeviceManager.py customizer.py test_SSH_DeviceManager.py`
- Lint: `pylint $(git ls-files '*.py')`

## Coverage Targets

Targets are a floor, not a ceiling. New work should preserve the current
logic-first test posture and avoid pushing important rules back into
unexercised Tkinter callbacks.

| Scope | Metric | Floor |
| --- | --- | --- |
| Repository default | Automated behavioral coverage of modified logic paths | Required |
| Core connection / action logic | Deterministic unit or integration tests | Required |
| Validation, profile persistence, and config parsing | Negative-case automated tests | Required |
| UI presentation / theme visuals | Manual verification when touched | Required |

## Continuous Coverage Evaluation

The repository does not yet publish line/branch percentages via `coverage.py`.
The current baseline is instead tracked as the automated suite size and the
command set that must keep passing on each change.

| Date | Overall coverage signal | Notes |
| --- | --- | --- |
| 2026-07-01 | 158 automated tests | Baseline behavioral suite from `test_SSH_DeviceManager.py`; percentage instrumentation not yet configured. |

## Coverage Gap Log

Track known untested behavior here. Each gap should have a matching follow-up
in `TODO.md` under Testing or Technical Debt.

| Gap ID | Area / behavior | Risk | Related requirement | Status | TODO ref |
| --- | --- | --- | --- | --- | --- |
| GAP-001 | Real SSH interoperability against a live server matrix (host-key modes, SFTP, reconnect) is not exercised in CI. | Medium | FR-001, FR-002, FR-003, NFR-002 | Open | TODO.md#testing |
| GAP-002 | Visual rendering of themes, resizing, and Tk widget layout remains manual. | Medium | FR-005, NFR-003 | Open | TODO.md#testing |
| GAP-003 | Line/branch percentages are not yet collected or enforced in CI. | Low | NFR-004 | Open | TODO.md#testing |

## Requirement Coverage

The authoritative mapping from product requirements to verifying tests lives in
`docs/REQUIREMENTS_TRACEABILITY.md`. Requirements with no verifying test are
coverage gaps and should also appear in the table above.
