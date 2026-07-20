# Command Reference

## Installation

```bash
pip install -e .
```

Installs the application and its runtime dependency (Paramiko) from `pyproject.toml`, which is the
single source of truth for dependencies. Also provides an `ssh-device-manager` command that launches
the GUI.

```bash
pip install -e ".[dev]"
```

Adds contributor tooling: Pylint, flake8, pre-commit, and build.

```bash
python -m build
```

Builds the sdist and wheel, the same way `.github/workflows/python-publish.yml` does on release.

## Application

```bash
python SSH_DeviceManager.py
```

Starts the SSH Device Manager GUI.

```bash
python customizer.py
```

Starts the visual `sections.json` editor.

## Testing

```bash
python -m unittest test_SSH_DeviceManager.py test_customizer.py -v
```

Runs the full local suite.

```bash
python -m unittest test_SSH_DeviceManager.TestHostHistory test_SSH_DeviceManager.TestHostHistoryLimit -v
```

Runs the focused host-history regression tests.

## Linting

```bash
pylint $(git ls-files '*.py')
```

Runs the repository lint command used by CI-style validation. On Windows PowerShell, use Git Bash or another shell that supports command substitution.

## Constitution Checks

Each of these has a matching CI gate under `.github/workflows/constitution-*.yml`, so running them
locally reproduces what CI will report. Most follow the framework's warn-by-default contract: they
report findings and exit zero unless given `--strict`. The exceptions are noted below.

On Windows these are shell scripts, so run them through Git Bash. The explicit interpreter path is
used here because it works from PowerShell, `cmd`, and IDE task runners alike; from a Git Bash
prompt, plain `bash constitution/scripts/...` is equivalent.

```bash
"C:\Program Files\Git\bin\bash.exe" constitution/scripts/check_compliance.sh --strict --product .
```

Checks required, recommended, and product-facing Constitution files. Also flags files that still
contain unedited template placeholder content.

```bash
"C:\Program Files\Git\bin\bash.exe" constitution/scripts/check_traceability.sh docs/PRODUCT_REQUIREMENTS.md docs/REQUIREMENTS_TRACEABILITY.md
```

Verifies every requirement ID has traceability evidence.

```bash
"C:\Program Files\Git\bin\bash.exe" constitution/scripts/check_version_alignment.sh .
```

Scans governance files for stale Constitution version references. Note it cannot distinguish a
historical mention from a stale claim, so deliberately-historical references are best written as
commit SHAs rather than version strings.

```bash
"C:\Program Files\Git\bin\bash.exe" constitution/scripts/check_constitution_freshness.sh .
```

Reports whether the pinned `constitution/` submodule is `CURRENT`, `BEHIND`, or `AHEAD/DIVERGED`
against the latest upstream release tag. This is what the `SessionStart` hook in
`.claude/settings.json` runs automatically. `BEHIND` fails the CI version gate; `AHEAD/DIVERGED`
only warns.

```bash
"C:\Program Files\Git\bin\bash.exe" constitution/scripts/check_secrets.sh --strict .
```

Sweeps for credential-shaped filenames and high-confidence secret patterns, and (under `--strict`)
verifies `.gitignore` covers env files, private keys, service-account JSON, `.netrc`, and Terraform
state. A real secret hit **always** fails, with or without `--strict`. Run this before pushing.

```bash
"C:\Program Files\Git\bin\bash.exe" constitution/scripts/check_ots_inventory.sh --strict .
```

Cross-checks runtime dependencies declared in `pyproject.toml` against `docs/OTS_SOFTWARE.md`, so a
dependency added without an inventory row is flagged. Only `[project] dependencies` are checked —
the `dev` extra is development tooling and is intentionally out of scope.

```bash
"C:\Program Files\Git\bin\bash.exe" constitution/scripts/check_env_vars.sh --strict .
```

Cross-checks configuration manifests against `docs/ENV_VARS.md`. This project reads no environment
variables, so there is currently nothing to verify — see that document for why.

```bash
"C:\Program Files\Git\bin\bash.exe" constitution/scripts/run_declared_tests.sh .
```

Extracts the `Full suite` command from `docs/TEST_PLAN.md`'s "How to Run Tests" section and runs it.
That line is machine-readable, so keep it a real runnable one-liner. A declared command that fails
always fails the build, regardless of `--strict`.
