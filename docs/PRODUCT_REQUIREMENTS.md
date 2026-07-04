# Product Requirements

This document defines the current engineering contract for SSH Device Manager,
an internal desktop application for connecting to SSH-enabled devices, running
curated maintenance commands, and transferring files without requiring shell
fluency from every operator.

The repository already contains mature implementation and tests. This file
captures the behavior that should stay stable as the codebase evolves.

## Requirement Levels

- `MUST`: Required for the current release line.
- `SHOULD`: Important, but deferrable if a change must be staged.
- `COULD`: Useful future enhancement.
- `WON'T`: Explicitly out of scope for the current release line.

## Product Summary

SSH Device Manager is a local Tkinter desktop app used to connect to remote
devices over SSH/SFTP, run predefined or ad hoc commands, and manage reusable
profiles and JSON-driven action layouts. The current release goal is to keep
the operator workflow stable while preserving safe connection defaults,
actionable error handling, and a testable modular architecture.

## Functional Requirements

### Connection and Session Management

**FR-001** `MUST` let an operator connect to and disconnect from a remote host
using host, port, username, password, timeout, and host-key mode inputs.

- Level: `MUST`
- Acceptance criteria:
  - `FR-001-AC-1`: valid connection details start an SSH session without
    freezing the UI.
  - `FR-001-AC-2`: invalid or missing connection fields are rejected with a
    specific, actionable error message.
  - `FR-001-AC-3`: disconnect clears runtime connection state and honors the
    "clear credentials on disconnect" option.

**FR-002** `MUST` let an operator run predefined and ad hoc SSH commands and
review the combined output in the application log pane.

- Level: `MUST`
- Acceptance criteria:
  - `FR-002-AC-1`: predefined button actions can trigger SSH commands from the
    active `sections.json`.
  - `FR-002-AC-2`: ad hoc command execution preserves command history and shows
    stdout/stderr output in the UI log.
  - `FR-002-AC-3`: command execution is blocked or reported clearly when no
    connection is active.

**FR-003** `MUST` support SFTP-based file transfer for both template uploads
and operator-selected file destinations.

- Level: `MUST`
- Acceptance criteria:
  - `FR-003-AC-1`: upload actions call through the SSH/SFTP layer with the
    selected local and remote paths.
  - `FR-003-AC-2`: uploads are prevented with a clear message when no SSH
    session is active.

### Configuration and Workflow

**FR-004** `MUST` allow operators to save, load, and delete connection profiles
and retain a bounded host history for common connections.

- Level: `MUST`
- Acceptance criteria:
  - `FR-004-AC-1`: profile persistence round-trips host, port, username,
    timeout, and host-key mode through the JSON config file.
  - `FR-004-AC-2`: host history deduplicates repeated entries and keeps only
    the configured maximum.

**FR-005** `MUST` load action sections from `sections.json` and tolerate
missing, invalid, or changed configuration files without crashing.

- Level: `MUST`
- Acceptance criteria:
  - `FR-005-AC-1`: valid section definitions render as titled button groups.
  - `FR-005-AC-2`: invalid or missing config files are reported cleanly.
  - `FR-005-AC-3`: configuration reload keeps the application responsive.

**FR-006** `SHOULD` provide a standalone customizer that helps maintain
`sections.json` without hand-editing the JSON structure.

- Level: `SHOULD`
- Acceptance criteria:
  - `FR-006-AC-1`: operators can launch `customizer.py` separately from the
    main app.
  - `FR-006-AC-2`: saved configuration can be reloaded by the main app.

## Non-Functional Requirements

### Security

**NFR-001** `MUST` avoid expanding the app into a secret-management system and
keep SSH trust behavior explicit.

- Level: `MUST`
- Acceptance criteria:
  - `NFR-001-AC-1`: `sections.json` is treated as UI metadata only and must not
    carry embedded credentials.
  - `NFR-001-AC-2`: the app exposes strict, warning, and auto host-key modes,
    with warning remaining the default behavior.

### Reliability

**NFR-002** `MUST` fail safely when connections drop, config files are broken,
or dependencies are unavailable.

- Level: `MUST`
- Acceptance criteria:
  - `NFR-002-AC-1`: connection loss cleans up the SSH state instead of leaving
    a false "connected" state behind.
  - `NFR-002-AC-2`: startup and runtime exceptions produce operator-visible or
    developer-actionable diagnostics.

### Performance and Responsiveness

**NFR-003** `SHOULD` keep the desktop UI responsive during connect, test,
command, and upload workflows.

- Level: `SHOULD`
- Acceptance criteria:
  - `NFR-003-AC-1`: long-running SSH actions run off the main Tkinter event
    loop.
  - `NFR-003-AC-2`: log updates remain thread-safe.

### Testability

**NFR-004** `MUST` preserve automated verification for business and controller
logic whenever behavior changes.

- Level: `MUST`
- Acceptance criteria:
  - `NFR-004-AC-1`: connection, validation, profile, config, and output
    behaviors have deterministic automated coverage.
  - `NFR-004-AC-2`: governance docs stay aligned with the actual test suite and
    known gaps.

## Explicit Non-Goals

- `WON'T` store credentials in the repository or in `sections.json`.
- `WON'T` replace a full terminal emulator; the app remains a curated SSH task
  runner with ad hoc command support.
- `WON'T` guarantee headless CI validation of visual theme quality until UI
  smoke coverage is added.

## Acceptance Criteria Summary

A release is ready when every `MUST` requirement is `Verified` in
`docs/REQUIREMENTS_TRACEABILITY.md`, the documented test commands pass, and the
known gaps remain explicitly tracked.

## Traceability

Each requirement above is mapped to verifying automated evidence in
`docs/REQUIREMENTS_TRACEABILITY.md`. Update both files in the same change.
