# Project Security

This project follows [Eric's Engineering Constitution Security Standards](constitution/SECURITY.md).

## Local Security Concerns

- **LAN Exposure**: This is a local Tkinter desktop app. It does not bind a listening service or expose a network port.
- **Credential Handling**: Passwords are entered at runtime and are not persisted in connection profiles. Do not commit `ssh_device_manager_config.json`, shell history, screenshots, or notes that contain credentials.
- **Sensitive Data**: Terminal output, saved text output, structured JSON exports, startup logs, and uploaded file paths may contain hostnames, usernames, device inventory, command output, or secrets returned by remote devices. Review exports before sharing bug reports or audit artifacts.

## Security Checklist

- [ ] Connection passwords are not persisted in profiles or committed files.
- [ ] Dependencies are audited for vulnerabilities before release.
- [ ] Host, port, timeout, profile, section, command, and upload inputs are validated at boundaries.
- [ ] Saved text output, JSON exports, screenshots, and startup logs are reviewed for secrets or PII before sharing.
