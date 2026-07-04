# Product Requirements

This document defines the current product contract for SSH Device Manager. Requirement IDs are stable and should be referenced from tests, documentation, and future implementation work.

## Functional Requirements

| ID | Level | Requirement | Acceptance Criteria |
| --- | --- | --- | --- |
| **FR-001** | MUST | Connect to an SSH host using host, port, username, password, timeout, and host-key policy inputs. | FR-001-AC-1 rejects missing or invalid fields with specific messages. FR-001-AC-2 opens a Paramiko SSH session with the selected host-key policy. |
| **FR-002** | MUST | Execute configured and custom SSH commands only when connected. | FR-002-AC-1 blocks command execution while disconnected. FR-002-AC-2 returns combined stdout/stderr output. FR-002-AC-3 records custom command history without duplicates. |
| **FR-003** | MUST | Upload files to a connected host through SFTP workflows. | FR-003-AC-1 blocks uploads while disconnected. FR-003-AC-2 handles cancelled file selection without side effects. FR-003-AC-3 logs upload success or failure. |
| **FR-004** | SHOULD | Allow configurable action sections through `sections.json`. | FR-004-AC-1 loads valid section files. FR-004-AC-2 falls back safely on missing, empty, or invalid section files. FR-004-AC-3 resolves only supported command tokens. |
| **FR-005** | SHOULD | Provide a visual customizer for `sections.json`. | FR-005-AC-1 can add, edit, remove, load, and save sections/actions. FR-005-AC-2 handles cancelled dialogs safely. |
| **FR-006** | SHOULD | Persist connection profiles without storing passwords. | FR-006-AC-1 saves, loads, deletes, and refreshes profiles. FR-006-AC-2 stores host, port, username, timeout, and host-key mode only. |
| **FR-007** | SHOULD | Remember successful connection hosts for quick reuse. | FR-007-AC-1 records only successful connections. FR-007-AC-2 keeps the most recent host first. FR-007-AC-3 caps history at 10 hosts and supports clearing it. |
| **FR-008** | SHOULD | Provide output management for command logs and diagnostics. | FR-008-AC-1 supports append, copy, clear, and save. FR-008-AC-2 timestamps queued log messages. FR-008-AC-3 warns before saving empty output. FR-008-AC-4 exports structured JSON with raw text, split lines, line count, export timestamp, and format ID. |

## Non-Functional Requirements

| ID | Level | Requirement | Acceptance Criteria |
| --- | --- | --- | --- |
| **NFR-001** | MUST | Keep the UI responsive during SSH, command, and upload operations. | NFR-001-AC-1 network operations run in background threads. NFR-001-AC-2 output updates use queue-backed rendering. |
| **NFR-002** | MUST | Treat SSH credentials and trust decisions as security-sensitive. | NFR-002-AC-1 passwords are not persisted in profiles. NFR-002-AC-2 unknown host-key handling is explicit and configurable. NFR-002-AC-3 credentials can be cleared on disconnect. |
| **NFR-003** | SHOULD | Keep behavior testable without requiring live SSH devices. | NFR-003-AC-1 Tkinter and Paramiko interactions are mockable. NFR-003-AC-2 tests run without a network target. |
| **NFR-004** | SHOULD | Preserve backward compatibility for existing launcher imports. | NFR-004-AC-1 `SSH_DeviceManager.py` re-exports the public API expected by existing tests and users. |

## Non-Goals

- This project does not provide a hosted service, multi-user backend, or web API.
- This project does not manage SSH private keys or OS credential vault integration yet.
- This project does not guarantee that commands in `sections.json` are safe for every remote device; operators own review of device-specific command content.
