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

This repository declares its dependencies in **`pyproject.toml`** (PEP 621), which is the single
source of truth. `constitution/scripts/check_ots_inventory.sh` reads the `[project] dependencies`
array from it and cross-checks each entry against the Managed Dependencies table below.

Contributor tooling lives in the `dev` optional-dependency extra rather than in the runtime
dependency array, deliberately: the checker reads only runtime dependencies, so development-time
tools are not reported as shipped components. They are still recorded below as system-level OTS
for completeness.

Two consequences of the declared `requires-python = ">=3.8"` floor are worth stating plainly
rather than leaving implicit:

- **Python 3.8 reached end of life in October 2024** and no longer receives security fixes. The
  floor exists because commit `e103746` deliberately restored 3.8 typing compatibility and
  `.github/workflows/pylint.yml` lints against it. Raising the floor to 3.9 would let the project
  drop an EOL runtime and require Paramiko 4.x uniformly — see the Review Cadence note below.
- **Anyone installing on Python 3.8 silently receives the Paramiko 3.x line**, not 4.x, because
  Paramiko 4.x declares `requires-python >=3.9`. The dependency is specified as `paramiko>=3.4`
  with an open ceiling precisely so pip can resolve the newest release each interpreter supports.
  This means the security posture of a 3.8 install differs from a 3.9+ install; assess Paramiko
  advisories against **both** lines while the 3.8 floor stands.

## Managed Dependencies

Components declared in a dependency manifest in this repository.
`constitution/scripts/check_ots_inventory.sh` cross-checks the manifests against this table, so a
dependency added without a row here is flagged.

| Component ID | Name | Version | Supplier / Maintainer | Purpose | Risk | Verification | Anomaly Review | Update Policy | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OTS-001 | `paramiko` | Declared `>=3.4` in `pyproject.toml`. Resolves to 3.5.x on Python 3.8 and 4.x on 3.9+; 4.0.0 on the current dev machine | Paramiko project (Jeff Forcier / community), LGPL-2.1 | SSH transport, authentication, remote command execution, and SFTP upload — the entire remote-device capability of this application | High | Exercised throughout the suite via mocked `SSHManager` unit, controller, contract, and integration-style tests (`test_SSH_DeviceManager.py`); mature upstream project with its own extensive test suite. `.github/workflows/ci.yml` installs from the manifest across Python 3.8–3.12, so both the 3.x and 4.x resolution paths are exercised. No live-device verification yet — see GAP-002 in `docs/TEST_PLAN.md` | [GitHub advisories](https://github.com/paramiko/paramiko/security/advisories) / [CVE search](https://nvd.nist.gov/vuln/search/results?query=paramiko) — last reviewed 2026-07-19. **Assess advisories against both the 3.x and 4.x lines** while the Python 3.8 floor stands | Open ceiling so pip resolves the newest release each interpreter supports; a Dependabot ecosystem entry for `pip` is not yet configured | Active |

**Why `paramiko` is High risk**: it is the credential-handling and trust-boundary component of
this system. It receives user passwords and key material, negotiates and validates SSH host keys,
and executes commands on remote hosts. A defect or compromise here is directly exploitable against
every device the user connects to. Host-key policy in particular is a security-relevant setting —
see `SECURITY.md` and the strict host-key mode discussion in `TODO.md`.

## System-Level OTS

Software the project depends on that is **not** declared in a dependency manifest: operating systems, language runtimes, databases, message brokers, container base images, and similar. The checker cannot discover these automatically — keep this section honest by hand.

| Component ID | Name | Version | Supplier / Maintainer | Purpose | Risk | Verification | Anomaly Review | Update Policy | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OTS-101 | CPython | Declared floor `>=3.8` in `pyproject.toml`; 3.8–3.12 verified in CI; 3.14.0 on the current dev machine | Python Software Foundation | Language runtime for the application, `customizer.py`, and the test suite | Medium | Full suite runs green across the 3.8–3.12 CI matrix (`.github/workflows/ci.yml`). Before this, the suite ran on 3.11/3.12 only while `pylint.yml` linted 3.8/3.9/3.10, so commit `e103746`'s 3.8 typing-compatibility work was lint-verified but never test-verified | [Python security advisories](https://www.python.org/news/security/) — last reviewed 2026-07-19 | Track supported CPython releases; CI matrix updated as versions reach end of life. **3.8 is itself EOL since October 2024** — raising the floor to 3.9 is tracked in `TODO.md` | Active |
| OTS-102 | Tk / Tcl (via stdlib `tkinter`) | Tk 8.6 | Tcl/Tk core team, bundled with CPython | Desktop GUI toolkit for the `SSHGuiApp` interface and `customizer.py` | Low | Contract tests cover theme keys and widget-facing interfaces; widgets are mocked rather than realized, so no display server is required in CI. Real event-loop behavior is untested — see GAP-003 in `docs/TEST_PLAN.md` | [Tcl/Tk announcements](https://www.tcl-lang.org/software/tcltk/) — last reviewed 2026-07-19 | Follows whichever Tk the installed CPython bundles | Active |
| OTS-103 | Pylint | Declared in the `dev` extra of `pyproject.toml`; unpinned. Configured via `.pylintrc` | Pylint project / PyCQA | Static analysis for contributors and the `pylint.yml` workflow | Low | Development-time tooling only — not shipped, not on any runtime path. Repository currently scores 10.00/10 | [Pylint releases](https://github.com/pylint-dev/pylint/releases) — last reviewed 2026-07-19 | Unpinned; `pip install -e ".[dev]"` resolves the newest compatible release | Active |
| OTS-104 | flake8 | Declared in the `dev` extra of `pyproject.toml`; unpinned | PyCQA | Supplementary style check in `ci.yml`'s optional lint step (`--max-line-length=120`, non-blocking) | Low | Development-time tooling only — not shipped, not on any runtime path | [flake8 releases](https://github.com/PyCQA/flake8/releases) — last reviewed 2026-07-19 | Unpinned developer tooling | Active |
| OTS-105 | pre-commit | Declared in the `dev` extra of `pyproject.toml`; unpinned | pre-commit project | Runs the hooks in `.pre-commit-config.yaml`, including the constitution secrets sweep bound to the pre-push stage | Low | Development-time tooling only. Hooks are opt-in per machine (`pre-commit install --hook-type pre-push`); CI is the backstop | [pre-commit releases](https://github.com/pre-commit/pre-commit/releases) — last reviewed 2026-07-19 | Unpinned developer tooling | Active |
| OTS-106 | build | Declared in the `dev` extra of `pyproject.toml`; unpinned | PyPA | PEP 517 frontend used by `python-publish.yml` to produce the sdist and wheel on release | Low | Development-time tooling only. Verified locally: `python -m build` produces `ssh_device_manager-0.3.0` sdist and wheel with correct metadata | [build releases](https://github.com/pypa/build/releases) — last reviewed 2026-07-19 | Unpinned developer tooling | Active |

## Review Cadence

- Review this inventory whenever a dependency is added, removed, or upgraded — in the **same change**, not a later documentation pass.
- Periodically (at least once per release), re-review the Anomaly Review column: check each `Medium`/`High` component's tracker for newly reported defects and CVEs, and refresh the last-reviewed dates.
- A dependency the checker reports as undocumented is a gap: add its row (or remove the dependency) before the change merges.
