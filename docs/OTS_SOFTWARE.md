# OTS Software Inventory

This inventory tracks every off-the-shelf (OTS) software component this project depends on: third-party libraries, frameworks, runtimes, databases, and any other software the project uses but did not develop. It answers, for each component: what it is, why we use it, how risky it is, how we verified it is fit for use, and how it stays current.

The structure follows the intent of the FDA's OTS software guidance and IEC 62304's SOUP (Software of Unknown Provenance) requirements, generalized for any repository — regulated or not. For most projects it is simply the auditable answer to "what third-party software are we shipping, and is anyone watching it?"

It is a living document. Update it in the same change that adds, removes, or upgrades a dependency.

Related documents:

- `SECURITY.md` (constitution) — dependency risk review expectations and threat-modeling triggers.
- `docs/TEST_PLAN.md` — where verification evidence (test suites exercising a component) is declared.

## Conventions

- **Component ID**: a stable identifier, `OTS-001`, `OTS-002`, ... Once assigned, an ID is never reused, even after the component is removed. When a component is removed, set its Status to `Removed` rather than deleting the row.
- **Name**: the component's name **exactly as it is declared in the dependency manifest** (`package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Gemfile`, ...). The automated checker (`constitution/scripts/check_ots_inventory.sh`) matches manifest entries against this cell by exact value (case-insensitive), so a paraphrased or prettified name counts as undocumented.
- **Risk**: `Low`, `Medium`, or `High`. A component is at least `Medium` when it sits in a trust-sensitive position — handling credentials, parsing untrusted input, or running with elevated privileges (see `SECURITY.md`'s "Threat Modeling Triggers").
- **Verification**: how fitness for use was established — for example, the project's own integration tests that exercise it, upstream test-suite maturity, vendor certification, or a manual validation record.
- **Anomaly Review**: known-issue posture — where known defects/CVEs for this component are tracked, and the date they were last reviewed.
- **Update Policy**: how the version moves — pinned exactly, pinned to a range, Dependabot/Renovate-managed, vendored, etc.
- **Status**: `Active`, `Evaluating`, or `Removed`.

## Dependency Manifest Status

This repository does **not** yet declare a dependency manifest. Paramiko is currently installed
ad hoc (`pip install paramiko` in `.github/workflows/ci.yml` and
`.github/workflows/constitution-tests.yml`) rather than pinned in `requirements.txt` or
`pyproject.toml`.

Because `constitution/scripts/check_ots_inventory.sh` cross-checks manifests against the table
below, it currently has no manifest to read and therefore reports nothing to verify. That is a
gap in the manifest, not in this inventory — the `paramiko` row below is already named to match
what a future manifest will declare, so the checker will bind to it as soon as one exists.

Adding the manifest is tracked in `TODO.md` under Technical Debt.

## Managed Dependencies

Components that are (or will be) declared in a dependency manifest in this repository.
`constitution/scripts/check_ots_inventory.sh` cross-checks the manifests against this table, so a
dependency added without a row here is flagged.

| Component ID | Name | Version | Supplier / Maintainer | Purpose | Risk | Verification | Anomaly Review | Update Policy | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OTS-001 | `paramiko` | 4.0.0 (installed); unpinned in CI | Paramiko project (Jeff Forcier / community), LGPL-2.1 | SSH transport, authentication, remote command execution, and SFTP upload — the entire remote-device capability of this application | High | Exercised throughout the suite via mocked `SSHManager` unit, controller, contract, and integration-style tests (`test_SSH_DeviceManager.py`); mature upstream project with its own extensive test suite. No live-device verification yet — see GAP-002 in `docs/TEST_PLAN.md` | [GitHub advisories](https://github.com/paramiko/paramiko/security/advisories) / [CVE search](https://nvd.nist.gov/vuln/search/results?query=paramiko) — last reviewed 2026-07-19 | Currently unpinned; to become manifest-pinned and Dependabot-managed once a manifest exists | Active |

**Why `paramiko` is High risk**: it is the credential-handling and trust-boundary component of
this system. It receives user passwords and key material, negotiates and validates SSH host keys,
and executes commands on remote hosts. A defect or compromise here is directly exploitable against
every device the user connects to. Host-key policy in particular is a security-relevant setting —
see `SECURITY.md` and the strict host-key mode discussion in `TODO.md`.

## System-Level OTS

Software the project depends on that is **not** declared in a dependency manifest: operating systems, language runtimes, databases, message brokers, container base images, and similar. The checker cannot discover these automatically — keep this section honest by hand.

| Component ID | Name | Version | Supplier / Maintainer | Purpose | Risk | Verification | Anomaly Review | Update Policy | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OTS-101 | CPython | 3.11 / 3.12 verified in CI; 3.14.0 on the current dev machine | Python Software Foundation | Language runtime for the application, `customizer.py`, and the test suite | Medium | Full suite runs green on the 3.11 and 3.12 CI matrix (`.github/workflows/ci.yml`); Python 3.8 typing compatibility was deliberately restored in commit `e103746` | [Python security advisories](https://www.python.org/news/security/) — last reviewed 2026-07-19 | Track supported CPython releases; CI matrix updated as versions reach end of life | Active |
| OTS-102 | Tk / Tcl (via stdlib `tkinter`) | Tk 8.6 | Tcl/Tk core team, bundled with CPython | Desktop GUI toolkit for the `SSHGuiApp` interface and `customizer.py` | Low | Contract tests cover theme keys and widget-facing interfaces; widgets are mocked rather than realized, so no display server is required in CI. Real event-loop behavior is untested — see GAP-003 in `docs/TEST_PLAN.md` | [Tcl/Tk announcements](https://www.tcl-lang.org/software/tcltk/) — last reviewed 2026-07-19 | Follows whichever Tk the installed CPython bundles | Active |
| OTS-103 | Pylint | Configured via `.pylintrc`; unpinned | Pylint project / PyCQA | Optional static analysis for contributors and the `pylint.yml` workflow | Low | Development-time tooling only — not shipped, not on any runtime path | [Pylint releases](https://github.com/pylint-dev/pylint/releases) — last reviewed 2026-07-19 | Unpinned developer tooling; pin alongside the future dependency manifest | Active |

## Review Cadence

- Review this inventory whenever a dependency is added, removed, or upgraded — in the **same change**, not a later documentation pass.
- Periodically (at least once per release), re-review the Anomaly Review column: check each `Medium`/`High` component's tracker for newly reported defects and CVEs, and refresh the last-reviewed dates.
- A dependency the checker reports as undocumented is a gap: add its row (or remove the dependency) before the change merges.
