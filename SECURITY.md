# Project Security

This project follows [Eric's Engineering Constitution Security Standards](constitution/SECURITY.md).

## Local Security Concerns

- **LAN Exposure**: This is a local Tkinter desktop app. It does not bind a listening service or expose a network port.
- **Credential Handling**: Passwords are entered interactively at runtime and are not persisted in connection profiles. Do not hard-code them in source files, `sections.json`, or committed config, and do not commit `ssh_device_manager_config.json`, shell history, screenshots, or notes that contain credentials.
- **Host Key Verification**: The default mode is `warning`, which makes first-use trust visible without silently accepting every key. `strict` and `auto` are both available, but `auto` should be reserved for trusted lab environments — it accepts any key without prompting.
- **Action Definitions**: `sections.json` drives **executable** SSH actions, not just UI labels. Keep secrets out of button labels, tooltips, and command text, and review changes to it as you would review code.
- **Local Config Files**: `ssh_device_manager_config.json` stores connection profile metadata. Treat it as workstation-local state and review it before sharing or committing.
- **Sensitive Data**: Terminal output, saved text output, structured JSON exports, startup logs, and uploaded file paths may contain hostnames, usernames, device inventory, command output, or secrets returned by remote devices. Review exports before sharing bug reports or audit artifacts, and prefer scrubbed test hosts when capturing logs for review.

## Security Checklist

Items marked complete describe properties the code currently holds; unchecked items are open work tracked in `TODO.md`.

- [x] Connection passwords are entered at runtime and are not persisted in profiles or committed files.
- [x] Host, port, timeout, profile, section, command, and upload inputs are validated at the GUI boundary before connection attempts.
- [x] Host-key verification is explicit and configurable (`strict`, `warning`, `auto`) rather than silently bypassed.
- [x] Third-party dependencies are registered with risk assessments in `docs/OTS_SOFTWARE.md`.
- [ ] Add OS-backed secret storage instead of relying solely on interactive password entry and local profile metadata.
- [ ] Establish a repeatable dependency-audit command for Paramiko and future Python dependencies.
- [ ] Review log messages periodically to confirm hostnames, usernames, and command output do not leak sensitive operational data.
- [ ] Saved text output, JSON exports, screenshots, and startup logs are reviewed for secrets or PII before sharing.
