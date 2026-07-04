# MVP Backlog

This backlog translates the current SSH Device Manager requirements into reviewable delivery slices. `TODO.md` remains the living engineering roadmap; this file groups work into milestone-sized product increments.

## Milestone 1: Constitution Adoption

- [x] Install the Engineering Constitution as the pinned `constitution/` submodule.
- [x] Add product requirements, requirements traceability, and test plan documentation.
- [x] Add Constitution version, compliance, and submodule-update guardrails.

## Milestone 2: Core SSH Workflow Hardening

- [x] Keep host history limited to successful SSH connections.
- [ ] Add a live-device smoke checklist for SSH command execution and SFTP upload validation.
- [ ] Document trusted-host onboarding for strict host-key mode.

## Milestone 3: Contributor Reproducibility

- [ ] Add a dependency manifest for runtime and contributor tooling.
- [ ] Add measured coverage reporting and record the first line/branch coverage baseline.
- [ ] Decide whether pre-commit hooks should include Python-specific lint or formatting hooks beyond the universal Constitution defaults.

## Milestone 4: User-Facing Polish

- [ ] Add screenshots or a short walkthrough for the main app and `customizer.py`.
- [ ] Add import/export support for reusable `sections.json` profiles.
- [x] Add optional structured log export for command runs and uploads.
