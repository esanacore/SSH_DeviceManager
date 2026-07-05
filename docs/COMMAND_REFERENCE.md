# Command Reference

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

```bash
"C:\Program Files\Git\bin\bash.exe" constitution/scripts/check_compliance.sh --strict --product .
```

Checks required, recommended, and product-facing Constitution files.

```bash
"C:\Program Files\Git\bin\bash.exe" constitution/scripts/check_traceability.sh docs/PRODUCT_REQUIREMENTS.md docs/REQUIREMENTS_TRACEABILITY.md
```

Verifies every requirement ID has traceability evidence.
