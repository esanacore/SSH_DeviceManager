# Requirements Traceability Matrix

This matrix links each SSH Device Manager requirement to the automated evidence
that currently verifies it.

Related documents:

- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/TEST_PLAN.md`
- `docs/TEST_MATRIX.md`

## Functional Requirements

| Requirement ID | Level | Description | Acceptance Criteria | Verifying Tests | Status |
| --- | --- | --- | --- | --- | --- |
| FR-001 | MUST | Connect and disconnect with explicit connection inputs and host-key mode. | `FR-001-AC-1`, `FR-001-AC-2`, `FR-001-AC-3` | `UT-APP-02`, `UT-APP-03`, `UT-VAL-01` through `UT-VAL-10`, `UT-SSH-05`, `UT-SSH-06`, `UT-SSH-13`, `IT-LC-01`, `IT-VB-01`, `IT-DC-01`, `IT-DC-02` | Verified |
| FR-002 | MUST | Run predefined and ad hoc SSH commands with visible combined output. | `FR-002-AC-1`, `FR-002-AC-2`, `FR-002-AC-3` | `UT-SSH-08`, `UT-SSH-09`, `UT-SSH-10`, `UT-SSH-12`, `UT-APP-05`, `UT-APP-14`, `IT-LC-01`, `IT-CH-01`, `IT-CF-01` | Verified |
| FR-003 | MUST | Transfer files over SFTP for template and selected uploads. | `FR-003-AC-1`, `FR-003-AC-2` | `UT-SSH-11`, `UT-SSH-14`, `UT-SSH-15`, `UT-APP-06`, `UT-APP-15`, `UT-APP-16`, `UT-AC-01` through `UT-AC-06` | Verified |
| FR-004 | MUST | Persist connection profiles and bounded host history. | `FR-004-AC-1`, `FR-004-AC-2` | `UT-PR-01` through `UT-PR-08`, `UT-HH-01`, `UT-HH-02`, `IT-PW-01`, `IT-CR-01`, `IT-HL-01` | Verified |
| FR-005 | MUST | Load and reload `sections.json` safely. | `FR-005-AC-1`, `FR-005-AC-2`, `FR-005-AC-3` | `UT-SC-01` through `UT-SC-08`, `UT-SLE-01`, `UT-SW-01`, `UT-SW-02`, `UT-BBS-01`, `UT-BBS-02`, `CT-03`, `CT-04`, `IT-35` | Verified |
| FR-006 | SHOULD | Support standalone maintenance of `sections.json` through `customizer.py`. | `FR-006-AC-1`, `FR-006-AC-2` | `README.md` launch instructions, config reload tests `UT-SW-01`, `UT-SW-02`, `IT-35` | In Progress |

## Non-Functional Requirements

| Requirement ID | Level | Description | Acceptance Criteria | Verifying Tests | Status |
| --- | --- | --- | --- | --- | --- |
| NFR-001 | MUST | Keep trust behavior explicit and keep secrets out of UI metadata. | `NFR-001-AC-1`, `NFR-001-AC-2` | `UT-SSH-13`, `CT-04`, README security notes, docs/COMMAND_REFERENCE.md guidance | Verified |
| NFR-002 | MUST | Fail safely on dropped connections, broken config, or startup/runtime errors. | `NFR-002-AC-1`, `NFR-002-AC-2` | `UT-SSH-03`, `UT-SSH-04`, `UT-CS-01`, `UT-CS-02`, `UT-CE-01` through `UT-CE-04`, `UT-TE-01` through `UT-TE-03`, `UT-SE-01`, `IT-AF-01`, `IT-SJ-02` through `IT-SJ-04`, `IT-CF-01`, `IT-CR-02` | Verified |
| NFR-003 | SHOULD | Keep the UI responsive and log updates thread-safe. | `NFR-003-AC-1`, `NFR-003-AC-2` | `UT-APP-02`, `UT-APP-04`, `UT-APP-05`, `UT-APP-06`, `UT-OM-01` through `UT-OM-09` | Verified |
| NFR-004 | MUST | Preserve deterministic automated coverage for core logic and keep docs aligned. | `NFR-004-AC-1`, `NFR-004-AC-2` | `python -m unittest test_SSH_DeviceManager.py -v`, `docs/TEST_MATRIX.md`, `docs/TEST_PLAN.md`, `TODO.md` | In Progress |

## Coverage Summary

| Metric | Count |
| --- | --- |
| Total requirements | 10 |
| Verified | 8 |
| In progress | 2 |
| Not started | 0 |
| Requirements without a verifying test (gaps) | 1 |
