# Project Memory

This file contains durable memories, codebase learnings, user preferences, and key architectural decisions. AI agents read this file at the start of each session to align with past context, and update it (at the user's discretion) at the end of a session.

> [!IMPORTANT]
> **User Discretion**: Do not add or edit entries in this file without presenting them to the user for review. The user has absolute discretion over what memories are retained.

## User Preferences & Styling Choices

<!-- 
  Record the user's development preferences, styling decisions, and custom choices.
  Examples:
  - "User prefers TailwindCSS for styling, styled-components for theme overrides."
  - "User prefers HSL values for colors in stylesheets."
  - "Avoid verbose inline comments; document code using JSDoc type definitions."
-->

- Governance work is expected to be brought fully current *before* starting feature or `TODO.md` work. Recorded 2026-07-19, when the user scoped the Constitution 1.37.0 alignment session as an explicit prerequisite to any other roadmap item.

## Codebase Learnings & Gotchas

<!-- 
  Record critical codebase quirks, system anomalies, test runner behaviors, or API gotchas.
  Examples:
  - "Database port must be forwarded to localhost:5432 during integration tests."
  - "The mock auth service in test environment times out after 30 seconds."
  - "Ensure Git CRLF conversion is disabled when modifying binary images."
-->

- **Tk is mocked at import time, so tests need no display server.** `test_SSH_DeviceManager.py` replaces `tkinter` before importing the application module, and widgets are never realized. CI therefore requires neither `python3-tk` nor `xvfb` — `actions/setup-python` plus `pip install paramiko` is the whole setup. Do not add display plumbing to a workflow to "fix" a GUI test failure; the cause will be somewhere else.
- **`AHEAD/DIVERGED` from the constitution freshness check is expected here — do not "fix" it by downgrading the pin.** The upstream `esanacore/engineering-constitution` repo declares 1.37.0 in `VERSION`/`CHANGELOG.md`, but releases 1.35.0–1.37.0 were never Git-tagged; the newest tag is `v1.34.0`. Because the version gate compares against tags, any repo pinned to current `main` reports `AHEAD/DIVERGED` rather than `CURRENT`. The gate explicitly does not fail on AHEAD. Pinning back to `v1.34.0` would be actively harmful: that tag predates `scripts/check_ots_inventory.sh` and the `docs/MEMORY.md` template, so it would break the OTS gate and this file's own basis. The real fix is tagging the releases upstream — tracked in `TODO.md` under Governance.
- **When patching `SSHManager` for tests that exercise `test_connection()`**, patch `ssh_device_manager.app.SSHManager`, not `SSH_DeviceManager.SSHManager` — the app module holds its own import reference. (Carried over from `.github/copilot-instructions.md`.)

## Active Project Decisions

<!-- 
  Record major technical and architectural decisions approved by the user that govern current work.
  Examples:
  - "Approved using SQLite for local development and PostgreSQL for production."
  - "Adopted the Compliance Validation Triad to gate pull requests."
-->

- **Paramiko is this project's security-critical trust boundary; treat host-key policy changes as security-sensitive.** It receives user passwords and private key material, negotiates and validates SSH host keys, and executes commands on remote hosts, so a defect or compromise there is directly exploitable against every device the user connects to. It is recorded as **High** risk in `docs/OTS_SOFTWARE.md` (OTS-001) for this reason. Any change touching `ssh_device_manager/ssh_manager.py`'s host-key policy (`strict` / `warning` / `auto`, currently defaulting to `WarningPolicy`), credential handling, or the `clear_creds_var` teardown path warrants an explicit security review under `constitution/SECURITY.md`'s threat-modeling triggers — not just a passing test run.
- Approved 2026-07-19: remain pinned to Constitution **1.37.0** (untagged `main` tip) rather than the newest tag `v1.34.0`, accepting the non-blocking `AHEAD/DIVERGED` warning in exchange for the OTS inventory, project-memory framework, and agent skills that 1.35.0–1.37.0 introduced.
