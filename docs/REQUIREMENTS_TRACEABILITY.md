# Requirements Traceability Matrix

This matrix maps each product requirement to current verification evidence. Update it when adding requirements, changing behavior, or adding tests.

## Functional Requirements

| Requirement ID | Level | Acceptance Criteria | Verifying Tests | Status |
| --- | --- | --- | --- | --- |
| FR-001 | MUST | Validate connection inputs and connect with host-key policy. | `TestGetConnectionInputs`, `TestParseIntInput`, `TestGetHostKeyMode`, `TestSSHManager.test_connect`, `TestSSHManager.test_connect_host_key_policies`, `TestOnConnectErrors` | Verified |
| FR-002 | MUST | Run commands only when connected and preserve output/history behavior. | `TestSSHGuiApp.test_run_ssh_command`, `TestSSHGuiApp.test_run_ssh_command_not_connected`, `TestSSHManager.test_run_command_with_stderr`, `TestCommandHistoryIntegration` | Verified |
| FR-003 | MUST | Upload files only when connected and handle success/failure/cancel paths. | `TestActionControllerPerformUpload`, `TestSSHGuiApp.test_upload_config_template`, `TestSSHManager.test_upload_file`, `TestSSHManager.test_upload_file_not_connected` | Verified |
| FR-004 | SHOULD | Load and validate configurable action sections. | `TestSectionsJsonLoading`, `TestSectionsController`, `TestContracts.test_sections_json_conforms_to_schema`, `TestContracts.test_sections_json_commands_are_valid_tokens` | Verified |
| FR-005 | SHOULD | Edit section/action config through the customizer. | `test_customizer.TestCustomizerApp` | Verified |
| FR-006 | SHOULD | Save, load, delete, and refresh profiles without passwords. | `TestProfiles`, `TestProfileWorkflow`, `test_delete_selected_profile_no_selection_warns`, `test_load_selected_profile_no_selection_warns`, `test_refresh_profile_list_empty_clears_selection`, `test_refresh_profile_list_keeps_valid_selection`, `TestContracts.test_profile_schema_round_trip` | Verified |
| FR-007 | SHOULD | Remember only successful hosts, keep recent-first order, cap at 10, and clear history. | `TestHostHistory.test_connect_adds_to_host_history`, `TestHostHistory.test_failed_connect_does_not_add_to_host_history`, `TestHostHistoryLimit.test_history_capped_at_10`, `TestHostHistory.test_on_host_selected_clear` | Verified |
| FR-008 | SHOULD | Append, timestamp, copy, clear, save, and structured-export output. | `TestOutputManager`, `TestOutputManager.test_build_structured_output_keeps_text_and_lines`, `TestOutputManager.test_export_json_writes_structured_output_and_logs_ok`, `TestOutputManager.test_export_json_empty_output_shows_warning`, `TestSSHGuiApp.test_clear_output`, `TestSSHGuiApp.test_copy_output`, `TestSSHGuiApp.test_save_output`, `TestSSHGuiApp.test_export_output_json` | Verified |

## Non-Functional Requirements

| Requirement ID | Level | Acceptance Criteria | Verifying Tests | Status |
| --- | --- | --- | --- | --- |
| NFR-001 | MUST | Keep UI responsive through threaded network work and queue-backed logs. | `TestSSHGuiApp.test_on_connect`, `TestSSHGuiApp.test_run_ssh_command`, `TestActionControllerPerformUpload`, `TestOutputManager.test_start_poller_drains_queue_into_widget` | Verified |
| NFR-002 | MUST | Avoid password persistence and make host-key trust explicit. | `TestDisconnectClearsCredentials`, `TestSSHManager.test_connect_host_key_policies`, `TestGetHostKeyMode`, `TestContracts.test_profile_schema_round_trip` | Verified |
| NFR-003 | SHOULD | Run deterministic tests without real SSH devices. | Full suite: `python -m unittest test_SSH_DeviceManager.py test_customizer.py -v` | Verified |
| NFR-004 | SHOULD | Preserve launcher import compatibility. | `TestShimExports` | Verified |

## Coverage Gap Summary

| Status | Count |
| --- | ---: |
| Requirements with verifying tests | 12 |
| Requirements without verifying tests | 0 |
