# SSH Device Manager - Test Matrix

> **Test File:** `test_SSH_DeviceManager.py`
> **Total Tests:** 158 (142 unit + 16 integration)
> **Last Updated:** 2026-06-06
> **Run Command:** `python -m unittest test_SSH_DeviceManager.py -v`

---

## Table of Contents

1. [Test Summary](#test-summary)
2. [Unit Tests](#unit-tests)
   - [Data Models](#1-data-models)
   - [ToolTip](#2-tooltip)
   - [SSH Manager](#3-ssh-manager)
   - [SSH Manager Reconnect](#4-ssh-manager-reconnect)
   - [GUI App Core](#5-gui-app-core)
   - [Output Manager](#6-output-manager)
   - [Paramiko Compat Stub](#7-paramiko-compat-stub)
   - [Connection Input Validation](#8-connection-input-validation)
   - [Connect Error Handling](#9-connect-error-handling)
   - [Test Connection Error Handling](#10-test-connection-error-handling)
   - [Test Connection Generic Exception](#11-test-connection-generic-exception)
   - [Host Key Mode](#12-host-key-mode)
   - [Integer Input Parsing](#13-integer-input-parsing)
   - [Integer Input Parsing Boundary](#14-integer-input-parsing-boundary)
   - [Integer Input Parsing No-Max](#15-integer-input-parsing-no-max)
   - [Themes](#16-themes)
   - [Profiles](#17-profiles)
   - [Profile Controller](#18-profile-controller)
   - [Host History](#19-host-history)
   - [Connection State Monitor](#20-connection-state-monitor)
   - [Connection Controller](#21-connection-controller)
   - [Connection Monitor Poll](#22-connection-monitor-poll)
   - [Action Controller Upload](#23-action-controller-upload)
   - [Sections Controller](#24-sections-controller)
   - [Sections Loader Empty Command](#25-sections-loader-empty-command)
   - [Sections Watcher](#26-sections-watcher)
   - [Build Button Sections](#27-build-button-sections)
   - [App Config Missing File](#28-app-config-missing-file)
   - [Startup Error Logging](#29-startup-error-logging)
   - [Contracts](#30-contracts)
3. [Integration Tests](#integration-tests)
   - [Full Lifecycle](#31-connect--run--disconnect-lifecycle)
   - [Auth Failure Recovery](#32-auth-failure-recovery)
   - [Validation Blocks Connect](#33-validation-blocks-connect)
   - [Profile Workflow](#34-profile-workflow)
   - [Sections JSON Loading](#35-sections-json-loading)
   - [Command History](#36-command-history-integration)
   - [Command Failure Handling](#37-command-failure-handling)
   - [Config Round-Trip](#38-app-config-round-trip)
   - [Host History Limit](#39-host-history-limit)
   - [Disconnect Credential Clearing](#40-disconnect-credential-clearing)
4. [Requirements Traceability](#requirements-traceability)

---

## Test Summary

| Category | Class | Tests | Type |
|---|---|---|---|
| Shim Exports | `TestShimExports` | 2 | Unit |
| Data Models | `TestDataModels` | 2 | Unit |
| ToolTip | `TestToolTip` | 6 | Unit |
| SSH Manager | `TestSSHManager` | 15 | Unit |
| SSH Manager Reconnect | `TestSSHManagerReconnect` | 1 | Unit |
| GUI App Core | `TestSSHGuiApp` | 19 | Unit |
| Output Manager | `TestOutputManager` | 12 | Unit |
| Paramiko Compat Stub | `TestParamikoCompatStub` | 7 | Unit |
| Input Validation | `TestGetConnectionInputs` | 10 | Unit |
| Connect Errors | `TestOnConnectErrors` | 4 | Unit |
| Test Connection Errors | `TestTestConnectionErrors` | 2 | Unit |
| Test Connection Generic | `TestTestConnectionGenericException` | 1 | Unit |
| Host Key Mode | `TestGetHostKeyMode` | 3 | Unit |
| Int Parsing | `TestParseIntInput` | 6 | Unit |
| Int Parsing Boundary | `TestParseIntInputBoundary` | 3 | Unit |
| Int Parsing No-Max | `TestParseIntInputNoMaxBelowMin` | 1 | Unit |
| Themes | `TestThemes` | 3 | Unit |
| Profiles | `TestProfiles` | 8 | Unit |
| Profile Controller | `TestProfileControllerGaps` | 4 | Unit |
| Connection State | `TestConnectionStateMonitor` | 2 | Unit |
| Connection Controller | `TestConnectionControllerGaps` | 4 | Unit |
| Connection Monitor Poll | `TestConnectionMonitorPoll` | 1 | Unit |
| Host History | `TestHostHistory` | 3 | Unit |
| Action Controller Upload | `TestActionControllerPerformUpload` | 6 | Unit |
| Sections Controller | `TestSectionsController` | 8 | Unit |
| Sections Loader Empty Cmd | `TestSectionsLoaderEmptyCommand` | 1 | Unit |
| Sections Watcher | `TestSectionsWatcherFinallyRescheduling` | 2 | Unit |
| Build Button Sections | `TestBuildButtonSectionsAdditional` | 2 | Unit |
| App Config Missing File | `TestAppConfigMissingFile` | 1 | Unit |
| Startup Error Logging | `TestStartupErrorLogging` | 1 | Unit |
| Contracts | `TestContracts` | 7 | Unit |
| Full Lifecycle | `TestConnectRunDisconnectLifecycle` | 1 | Integration |
| Auth Recovery | `TestConnectAuthFailureRetry` | 1 | Integration |
| Validation Flow | `TestValidationBlocksConnect` | 1 | Integration |
| Profile Workflow | `TestProfileWorkflow` | 1 | Integration |
| Sections JSON | `TestSectionsJsonLoading` | 4 | Integration |
| Command History | `TestCommandHistoryIntegration` | 2 | Integration |
| Command Failure | `TestCommandFailureHandling` | 1 | Integration |
| Config File I/O | `TestAppConfigRoundTrip` | 2 | Integration |
| Host History Limit | `TestHostHistoryLimit` | 1 | Integration |
| Credential Clearing | `TestDisconnectClearsCredentials` | 2 | Integration |
| Customizer | `test_customizer.TestCustomizerApp` | 13 | Unit |
| **TOTAL** | **42 classes** | **176** | |

---

## Unit Tests

### 1. Data Models

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-DM-01 | `test_action_button` | Create ActionButton with all fields | label, enabled, handler, tooltip stored correctly |
| UT-DM-02 | `test_button_section` | Create ButtonSection with nested ActionButton | title, max_buttons, actions list stored correctly |

### 2. ToolTip

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-TT-01 | `test_with_text_binds_enter_and_leave` | ToolTip with text | Binds `<Enter>` and `<Leave>` events to widget |
| UT-TT-02 | `test_no_text_does_not_bind` | ToolTip with no text | Does not bind events |
| UT-TT-03 | `test_show_tip_creates_toplevel` | Show tip | Creates a Toplevel window with tooltip text |
| UT-TT-04 | `test_show_tip_no_op_when_already_shown` | Show when already visible | Does not create duplicate window |
| UT-TT-05 | `test_hide_tip_destroys_window` | Hide tip | Destroys the Toplevel window |
| UT-TT-06 | `test_hide_tip_no_op_when_not_shown` | Hide when not visible | No-op, no crash |

### 3. SSH Manager

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-SSH-01 | `test_is_connected_no_client` | No client set | Returns `False` |
| UT-SSH-02 | `test_is_connected_active_transport` | Client with active transport | Returns `True` |
| UT-SSH-03 | `test_is_connected_dead_transport` | Client with dead transport | Returns `False`, auto-disconnects, clears client |
| UT-SSH-04 | `test_is_connected_no_transport` | Client returns `None` transport | Returns `False`, auto-disconnects, clears client |
| UT-SSH-05 | `test_connect` | Connect with valid credentials | Paramiko SSHClient created, policy set, `.connect()` called with correct args |
| UT-SSH-06 | `test_disconnect` | Normal disconnect | SFTP closed, client closed, all refs set to `None` |
| UT-SSH-07 | `test_disconnect_with_error` | Disconnect when `.close()` raises OSError | No exception propagated, state cleaned up |
| UT-SSH-08 | `test_run_command_not_connected` | Run command with no client | Raises `RuntimeError` |
| UT-SSH-09 | `test_run_command` | Run command on connected client | `exec_command` called, stdout decoded, result returned |
| UT-SSH-10 | `test_run_command_decoding` | Run command returning invalid UTF-8 bytes | No `UnicodeDecodeError`, replacement char `U+FFFD` present |
| UT-SSH-11 | `test_upload_file` | Upload via SFTP | SFTP session opened, `.put()` called with correct paths |
| UT-SSH-12 | `test_run_command_with_stderr` | Run command returning stderr output | Both stdout and stderr content present in combined result |
| UT-SSH-13 | `test_connect_host_key_policies` | Connect with each host key mode | strict → RejectPolicy, warning → WarningPolicy, auto → AutoAddPolicy |
| UT-SSH-14 | `test_upload_file_not_connected` | Upload file with no client | Raises `RuntimeError` |
| UT-SSH-15 | `test_upload_file_reuses_sftp` | Two uploads in sequence | `open_sftp` called only once; second upload reuses existing SFTP channel |

### 4. SSH Manager Reconnect

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-SSH-16 | `test_connect_when_already_connected_disconnects_first` | Connect when already connected | Calls disconnect before reconnecting |

### 5. GUI App Core

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-APP-01 | `test_app_initialization` | Instantiate app with `init_ui=False` | SSH manager exists, sections list non-empty, all sections are valid `ButtonSection` objects |
| UT-APP-02 | `test_on_connect` | Call `on_connect` with valid fields | Worker thread spawned, `ssh.connect()` called with correct args including `host_key_mode` |
| UT-APP-03 | `test_on_disconnect` | Call `on_disconnect` with clear-creds enabled | `ssh.disconnect()` called, password cleared, UI set to disconnected |
| UT-APP-04 | `test_test_connection` | Call `test_connection` | Worker thread spawned, temp `SSHManager` created/connected/disconnected |
| UT-APP-05 | `test_run_ssh_command` | Run a command when connected | Command added to history, thread spawned, `ssh.run_command()` called |
| UT-APP-06 | `test_upload_config_template` | Upload file with mocked file dialog | Thread spawned, `ssh.upload_file()` called with correct local/remote paths |
| UT-APP-07 | `test_copy_output` | Copy output to clipboard | `clipboard_clear` and `clipboard_append` called with output text |
| UT-APP-08 | `test_log` | Log a message | Message queued in `log_queue` with content intact |
| UT-APP-09 | `test_save_output` | Save output to file | File dialog invoked, file opened for write, content written |
| UT-APP-10 | `test_save_output_empty` | Save when output is blank/whitespace | File is NOT opened; warning shown instead |
| UT-APP-11 | `test_save_output_write_error` | Save when file write raises IOError | Error logged with "ERROR" and exception message |
| UT-APP-12 | `test_clear_output` | Clear terminal output | Text widget enabled → deleted → re-disabled |
| UT-APP-13 | `test_on_connect_double_click_guard` | Call `on_connect` while `is_connecting=True` | Thread NOT spawned; double connection prevented |
| UT-APP-14 | `test_run_ssh_command_not_connected` | Run command when not connected | No command added to history; operation aborted |
| UT-APP-15 | `test_upload_config_template_not_connected` | Upload when not connected | `ssh.upload_file` not called |
| UT-APP-16 | `test_upload_config_template_cancelled` | Upload when file dialog cancelled | `ssh.upload_file` not called |
| UT-APP-17 | `test_log_message_has_timestamp` | Verify log message format | Queued message matches `[HH:MM:SS]` timestamp pattern |
| UT-APP-18 | `test_append_output_uses_output_manager_public_append` | Append output delegation | Uses OutputManager public append method |
| UT-APP-19 | `test_export_output_json` | Export output to structured JSON | File dialog invoked, JSON file opened, format ID, lines, line count, and raw text written |

### 6. Output Manager

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-OM-01 | `test_append_enables_inserts_and_disables` | Append text to output | Widget enabled, text inserted, widget re-disabled |
| UT-OM-02 | `test_clear_enables_deletes_and_disables` | Clear output | Widget enabled, content deleted, widget re-disabled |
| UT-OM-03 | `test_copy_clears_and_appends_to_clipboard` | Copy output to clipboard | Clipboard cleared and text appended |
| UT-OM-04 | `test_log_adds_timestamp_to_queue` | Log a message | Message with timestamp added to queue |
| UT-OM-05 | `test_save_writes_file_and_logs_ok` | Save output to file | File written successfully, success logged |
| UT-OM-06 | `test_save_empty_output_shows_warning` | Save empty output | Warning shown, no file written |
| UT-OM-07 | `test_save_no_file_chosen_does_not_write` | Save with cancelled dialog | No file written |
| UT-OM-08 | `test_save_write_error_logs_error` | Save with write error | Error logged |
| UT-OM-09 | `test_start_poller_drains_queue_into_widget` | Start log poller | Queue drained into text widget |
| UT-OM-10 | `test_build_structured_output_keeps_text_and_lines` | Build structured output payload | Format ID, export timestamp, split lines, line count, and raw text are preserved |
| UT-OM-11 | `test_export_json_writes_structured_output_and_logs_ok` | Export output as JSON | Structured payload is written and success is logged |
| UT-OM-12 | `test_export_json_empty_output_shows_warning` | Export empty output | Warning shown, no file written |

### 7. Paramiko Compat Stub

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-PC-01 | `test_stub_ssh_client_connect_raises` | Stub SSHClient.connect | Raises NotImplementedError |
| UT-PC-02 | `test_stub_ssh_client_exec_command_raises` | Stub SSHClient.exec_command | Raises NotImplementedError |
| UT-PC-03 | `test_stub_ssh_client_open_sftp_raises` | Stub SSHClient.open_sftp | Raises NotImplementedError |
| UT-PC-04 | `test_stub_ssh_client_get_transport_returns_none` | Stub SSHClient.get_transport | Returns None |
| UT-PC-05 | `test_stub_ssh_client_close_is_noop` | Stub SSHClient.close | No-op, no crash |
| UT-PC-06 | `test_stub_sftp_client_put_raises` | Stub SFTPClient.put | Raises NotImplementedError |
| UT-PC-07 | `test_stub_sftp_client_close_is_noop` | Stub SFTPClient.close | No-op, no crash |

### 8. Connection Input Validation

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-VAL-01 | `test_valid_inputs` | All fields valid | Returns tuple `(host, port, user, pw, timeout)` |
| UT-VAL-02 | `test_empty_host` | Host field empty | Returns `None`, logs "Host / IP is empty" |
| UT-VAL-03 | `test_empty_username` | Username field empty | Returns `None`, logs "Username is empty" |
| UT-VAL-04 | `test_empty_password` | Password field empty | Returns `None`, logs "Password is empty" |
| UT-VAL-05 | `test_multiple_empty_fields` | Host, username, and password all empty | Returns `None`, all three errors logged in single message |
| UT-VAL-06 | `test_port_tcl_error` | Port var raises TclError (blank field) | Returns `None`, logs port error |
| UT-VAL-07 | `test_port_out_of_range` | Port = 99999 | Returns `None`, logs "Port must be between" |
| UT-VAL-08 | `test_port_zero` | Port = 0 | Returns `None` |
| UT-VAL-09 | `test_timeout_tcl_error` | Timeout var raises TclError (blank field) | Returns `None`, logs timeout error |
| UT-VAL-10 | `test_timeout_out_of_range` | Timeout = 999 | Returns `None`, logs "Connection Timeout must be between" |

### 9. Connect Error Handling

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-CE-01 | `test_auth_exception` | `ssh.connect` raises `AuthenticationException` | Log contains "Authentication failed" and "Username and Password", UI set to disconnected |
| UT-CE-02 | `test_ssh_exception` | `ssh.connect` raises `SSHException` | Log contains "SSH error", UI set to disconnected |
| UT-CE-03 | `test_os_error` | `ssh.connect` raises `OSError` | Log contains "Network error", UI set to disconnected |
| UT-CE-04 | `test_generic_exception` | `ssh.connect` raises `RuntimeError` | Log contains "Connection failed", UI set to disconnected |

### 10. Test Connection Error Handling

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-TE-01 | `test_test_connection_auth_error` | Temp SSH raises `AuthenticationException` | Log contains "authentication rejected" |
| UT-TE-02 | `test_test_connection_os_error` | Temp SSH raises `OSError` | Log contains "network error" |

### 11. Test Connection Generic Exception

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-TE-03 | `test_generic_exception_logged` | Temp SSH raises generic Exception | Error logged gracefully |

### 12. Host Key Mode

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-HK-01 | `test_valid_modes` | Input: "strict", "warning", "auto" | Each returns itself verbatim |
| UT-HK-02 | `test_invalid_mode_defaults_to_warning` | Input: "nonsense" | Returns "warning" |
| UT-HK-03 | `test_empty_mode_defaults_to_warning` | Input: "" | Returns "warning" |

### 13. Integer Input Parsing

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-PI-01 | `test_valid_int` | Input: "22", range 1-65535 | Returns `22` |
| UT-PI-02 | `test_non_numeric` | Input: "abc" | Returns `None` |
| UT-PI-03 | `test_empty_string` | Input: "" | Returns `None` |
| UT-PI-04 | `test_below_minimum` | Input: "0", min=1 | Returns `None` |
| UT-PI-05 | `test_above_maximum` | Input: "99999", max=65535 | Returns `None` |
| UT-PI-06 | `test_no_maximum` | Input: "999999", no upper bound | Returns `999999` |

### 14. Integer Input Parsing Boundary

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-PI-07 | `test_exact_minimum_is_valid` | Input at exact minimum | Returns value |
| UT-PI-08 | `test_exact_maximum_is_valid` | Input at exact maximum | Returns value |
| UT-PI-09 | `test_float_string_is_invalid` | Input: "3.14" | Returns `None` |

### 15. Integer Input Parsing No-Max

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-PI-10 | `test_below_minimum_no_maximum_shows_range_text` | Below min with no max | Returns `None`, shows range text |

### 16. Themes

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-TH-01 | `test_all_themes_have_required_keys` | All THEMES entries | Each has: bg, fg, text_bg, text_fg, entry_bg, entry_fg, select_bg, select_fg |
| UT-TH-02 | `test_all_themes_have_optional_keys` | All THEMES entries | Each has: btn_bg, border, label_fg |
| UT-TH-03 | `test_solarized_dark_uses_canonical_palette` | Solarized Dark values | bg=#002b36, entry_bg=#073642, select_bg=#268bd2, border=#586e75 |

### 17. Profiles

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-PR-01 | `test_save_profile` | Save with valid name and fields | Profile stored in `app_config["profiles"]` with correct host/port/username, `_save_app_config` called |
| UT-PR-02 | `test_save_profile_no_name` | Save with both name fields empty | `_get_connection_inputs` never called, `_save_app_config` not called |
| UT-PR-03 | `test_load_selected_profile` | Load existing profile | `host_var`, `port_var`, `user_var`, `timeout_var` all `.set()` called with saved values |
| UT-PR-04 | `test_load_missing_profile` | Load profile that doesn't exist | No crash, `host_var.set` not called |
| UT-PR-05 | `test_delete_selected_profile` | Delete with confirmation (askyesno=True) | Profile removed from config, `_save_app_config` called |
| UT-PR-06 | `test_delete_profile_cancelled` | Delete cancelled (askyesno=False) | Profile remains in config |
| UT-PR-07 | `test_load_missing_profile_shows_error` | Load missing profile triggers cleanup | `_refresh_profile_list` called to sync stale dropdown |
| UT-PR-08 | `test_save_profile_via_dropdown_name` | Save when name field empty, dropdown populated | Profile saved using `profile_select_var` as fallback name |

### 18. Profile Controller

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-PR-09 | `test_load_selected_profile_no_selection_warns` | Load with no selection | Warning shown |
| UT-PR-10 | `test_delete_selected_profile_no_selection_warns` | Delete with no selection | Warning shown |
| UT-PR-11 | `test_refresh_profile_list_empty_clears_selection` | Refresh with empty profile list | Selection cleared |
| UT-PR-12 | `test_refresh_profile_list_keeps_valid_selection` | Refresh with valid selection | Selection preserved |

### 19. Host History

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-HH-01 | `test_on_host_selected_clear` | Select "\<Clear History\>" | History list emptied, host_var set to "" |
| UT-HH-02 | `test_connect_adds_to_host_history` | Connect with new host | Host added to `host_history` list |

### 20. Connection State Monitor

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-CS-01 | `test_detects_dropped_connection` | SSH session drops while status was "Connected" | UI set to disconnected, log warns "no longer active" |
| UT-CS-02 | `test_no_false_alarm_when_disconnected` | Status already "Disconnected", connection check runs | UI set to disconnected, NO spurious "no longer active" warning |

### 21. Connection Controller

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-CC-01 | `test_connect_worker_finally_clears_is_connecting` | Connect worker completes | `is_connecting` reset to False even on success |
| UT-CC-02 | `test_start_connection_monitor_schedules_poll` | Start connection monitor | Schedules periodic poll |
| UT-CC-03 | `test_test_connection_shows_info_when_already_connected` | Test connection when already connected | Shows info message |
| UT-CC-04 | `test_test_connection_ssh_exception` | Test connection raises SSHException | Error logged gracefully |

### 22. Connection Monitor Poll

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-CC-05 | `test_poll_calls_refresh_and_reschedules` | Poll fires | Calls refresh and reschedules next poll |

### 23. Action Controller Upload

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-AC-01 | `test_perform_upload_success` | Perform upload with valid file | Upload succeeds, success logged |
| UT-AC-02 | `test_perform_upload_error` | Perform upload with error | Error logged gracefully |
| UT-AC-03 | `test_send_file_scp_not_connected` | Send file when not connected | Operation aborted with warning |
| UT-AC-04 | `test_send_file_scp_no_file_chosen` | Send file with no file chosen | Operation aborted |
| UT-AC-05 | `test_upload_config_template_worker_success` | Upload template worker success | Upload completes, success logged |
| UT-AC-06 | `test_upload_config_template_worker_error` | Upload template worker error | Error logged gracefully |

### 24. Sections Controller

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-SC-01 | `test_build_button_sections_disabled_actions_excluded` | Build buttons with disabled actions | Disabled actions not rendered |
| UT-SC-02 | `test_build_button_sections_excess_buttons_truncated` | Build with excess buttons | Excess truncated with warning |
| UT-SC-03 | `test_get_mtime_returns_none_for_missing_file` | Get mtime for missing file | Returns None |
| UT-SC-04 | `test_get_mtime_returns_value_for_existing_file` | Get mtime for existing file | Returns timestamp value |
| UT-SC-05 | `test_open_sections_file_cancelled` | Open sections file dialog cancelled | No file loaded |
| UT-SC-06 | `test_open_sections_file_with_file_selected` | Open sections file dialog with selection | File loaded |
| UT-SC-07 | `test_reload_sections_updates_sections_and_mtime` | Reload sections | Sections and mtime updated |
| UT-SC-08 | `test_sections_watcher_detects_change_and_reloads` | Sections watcher detects change | Triggers reload |

### 25. Sections Loader Empty Command

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-SC-09 | `test_empty_command_handler_logs_warn` | Action with empty command | Warning logged |

### 26. Sections Watcher

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-SC-10 | `test_watcher_reschedules_after_successful_check` | Watcher completes check | Reschedules next check |
| UT-SC-11 | `test_watcher_reschedules_even_on_exception` | Watcher raises exception | Still reschedules |

### 27. Build Button Sections

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-SC-12 | `test_existing_children_are_destroyed` | Build button sections | Existing frame children destroyed first |
| UT-SC-13 | `test_multiple_sections_create_separator` | Two sections rendered | Vertical separator created between them |

### 28. App Config Missing File

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-CFG-01 | `test_creates_default_when_file_missing` | Config file missing | Creates default config |

### 29. Startup Error Logging

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-SE-01 | `test_startup_error_writes_log_file` | SSHGuiApp raises RuntimeError at startup | Traceback written to log file, contains exception class and message |

### 30. Contracts

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-CT-01 | `test_theme_color_values_are_valid_hex` | All color values in all themes | Every value is `#RRGGBB` hex or a recognized named color |
| UT-CT-02 | `test_theme_keys_match_apply_theme_usage` | Theme key sets vs apply_theme() | All keys used by apply_theme() exist; no unexpected keys present |
| UT-CT-03 | `test_sections_json_conforms_to_schema` | Shipped sections.json structure | Has `sections[]` with `title` (str), `max_buttons` (int), `actions[]` with `label`, `enabled`, `command` |
| UT-CT-04 | `test_sections_json_commands_are_valid_tokens` | Command values in sections.json | Every command is `run:*`, `__upload_template__`, `__send_file__`, `__custom_command__`, or empty |
| UT-CT-05 | `test_profile_schema_round_trip` | Save/load profile via config.py | All expected keys (`host`, `port`, `username`, `timeout`, `host_key_mode`) present with correct types after round-trip |
| UT-CT-06 | `test_ssh_manager_interface_contract` | SSHManager public API surface | Has `connect`, `disconnect`, `run_command`, `upload_file`, `is_connected` with expected required parameters |
| UT-CT-07 | `test_controller_interface_contract` | Controller classes vs app.py delegation | Each controller exposes every method that app.py delegates to it |

---

## Integration Tests

### 31. Connect -> Run -> Disconnect Lifecycle

| ID | Test Method | Flow |
|---|---|---|
| IT-LC-01 | `test_full_lifecycle` | **Connect** (verify `ssh.connect` args) -> **Run "show version"** (verify command, history[0]) -> **Run "show interfaces"** (verify history ordering) -> **Disconnect** (verify cleanup) -> **Verify log trail** contains Connecting, Connected, commands, Disconnecting |

### 32. Auth Failure Recovery

| ID | Test Method | Flow |
|---|---|---|
| IT-AF-01 | `test_auth_failure_then_success` | **Connect with wrong password** -> AuthenticationException raised -> "Authentication failed" logged, UI=disconnected -> **Fix password** -> **Connect again** -> Succeeds, UI=connected |

### 33. Validation Blocks Connect

| ID | Test Method | Flow |
|---|---|---|
| IT-VB-01 | `test_empty_fields_block_then_succeed` | **All fields empty** -> `on_connect()` -> Thread NOT spawned, all 3 errors logged (host, user, password) -> **Fill in all fields** -> `on_connect()` -> Thread spawned |

### 34. Profile Workflow

| ID | Test Method | Flow |
|---|---|---|
| IT-PW-01 | `test_save_load_connect` | **Fill fields** (router.local:2222, netadmin, s3cret, timeout=15) -> **Save as "RouterProfile"** -> Verify stored values -> **Load "RouterProfile"** -> Verify UI fields populated -> **Connect** -> Verify `ssh.connect` called with loaded values |

### 35. Sections JSON Loading

| ID | Test Method | Flow |
|---|---|---|
| IT-SJ-01 | `test_load_valid_sections_json` | Load JSON with 2 sections, 6 actions (plain cmd, `run:` prefix, `__upload_template__`, `__custom_command__`, `__send_file__`, disabled) -> Verify structure, labels, enabled flags, handler resolution to correct methods, all handlers callable |
| IT-SJ-02 | `test_load_missing_file_falls_back` | File doesn't exist -> Falls back to built-in `_define_sections()`, log contains "not found" |
| IT-SJ-03 | `test_load_invalid_json_falls_back` | File contains "NOT JSON" -> Falls back to built-in, log contains "ERROR" |
| IT-SJ-04 | `test_load_empty_sections_falls_back` | Valid JSON but `{"sections": []}` -> Falls back to built-in, log mentions "no sections" |

### 36. Command History Integration

| ID | Test Method | Flow |
|---|---|---|
| IT-CH-01 | `test_history_ordering_and_dedup` | Run cmd_a, cmd_b, cmd_c -> History = [cmd_c, cmd_b, cmd_a] -> Run cmd_a again -> History[0] = cmd_a (moved to front), count of cmd_a = 1 (no duplicates) |
| IT-CH-02 | `test_history_limit` | Run COMMAND_HISTORY_LIMIT + 50 unique commands -> History length <= COMMAND_HISTORY_LIMIT |

### 37. Command Failure Handling

| ID | Test Method | Flow |
|---|---|---|
| IT-CF-01 | `test_command_error_then_disconnect` | **Connect** -> **Run command** that raises RuntimeError("channel closed") -> Error logged with "channel closed" -> **Disconnect** -> Graceful cleanup, no crash |

### 38. App Config Round-Trip

| ID | Test Method | Flow |
|---|---|---|
| IT-CR-01 | `test_config_round_trip` | Create 2 profiles -> `_save_app_config()` to real temp file -> `_load_app_config()` from disk -> All profile data intact (hosts, ports, usernames, host_key_modes) |
| IT-CR-02 | `test_corrupt_config_returns_default` | Write invalid JSON to temp file -> `_load_app_config()` -> Returns default config `{"profiles": {}}`, no crash |

### 39. Host History Limit

| ID | Test Method | Flow |
|---|---|---|
| IT-HL-01 | `test_history_capped_at_10` | Connect to 15 different hosts sequentially -> History length <= 10, most recent host is first |

### 40. Disconnect Credential Clearing

| ID | Test Method | Flow |
|---|---|---|
| IT-DC-01 | `test_creds_cleared_on_disconnect` | clear_creds_var=True -> Disconnect -> `pass_var.set("")` called, log contains "Credentials cleared" |
| IT-DC-02 | `test_creds_preserved_on_disconnect` | clear_creds_var=False -> Disconnect -> `pass_var.set` NOT called |

---

## Requirements Traceability

| Requirement | Description | Test IDs |
|---|---|---|
| REQ-CONN-01 | App connects to SSH host with host/port/user/password | UT-SSH-05, UT-APP-02, IT-LC-01 |
| REQ-CONN-02 | App disconnects and cleans up resources | UT-SSH-06, UT-SSH-07, UT-APP-03, IT-LC-01 |
| REQ-CONN-03 | Connection state detected via transport check | UT-SSH-01..04, UT-CS-01, UT-CS-02 |
| REQ-CONN-04 | Concurrent connect attempts blocked | UT-APP-13 |
| REQ-CONN-05 | Dropped connection detected and reported | UT-CS-01 |
| REQ-CONN-06 | Host key policy maps to correct Paramiko class | UT-SSH-13 |
| REQ-VAL-01 | Empty Host/IP is rejected with specific message | UT-VAL-02, IT-VB-01 |
| REQ-VAL-02 | Empty Username is rejected with specific message | UT-VAL-03, IT-VB-01 |
| REQ-VAL-03 | Empty Password is rejected with specific message | UT-VAL-04, IT-VB-01 |
| REQ-VAL-04 | Invalid/blank Port is rejected (TclError, range) | UT-VAL-06..08 |
| REQ-VAL-05 | Invalid/blank Timeout is rejected (TclError, range) | UT-VAL-09..10 |
| REQ-VAL-06 | Multiple validation errors shown at once | UT-VAL-05, IT-VB-01 |
| REQ-ERR-01 | Auth failure produces actionable error message | UT-CE-01, UT-TE-01, IT-AF-01 |
| REQ-ERR-02 | SSH protocol error produces actionable message | UT-CE-02 |
| REQ-ERR-03 | Network/OS error produces actionable message | UT-CE-03, UT-TE-02 |
| REQ-ERR-04 | Unknown errors handled gracefully | UT-CE-04 |
| REQ-CMD-01 | Commands execute over SSH in background thread | UT-APP-05, IT-LC-01 |
| REQ-CMD-02 | Command output displayed (including stderr) | UT-SSH-09, UT-SSH-12 |
| REQ-CMD-03 | Invalid UTF-8 in output handled with replacement | UT-SSH-10 |
| REQ-CMD-04 | Command failure logged, app continues | IT-CF-01 |
| REQ-CMD-05 | Command without connection shows warning | UT-SSH-08, UT-APP-14 |
| REQ-HIST-01 | Commands added to history, most recent first | IT-CH-01 |
| REQ-HIST-02 | Duplicate commands deduplicated (old entry removed) | IT-CH-01 |
| REQ-HIST-03 | History respects COMMAND_HISTORY_LIMIT | IT-CH-02 |
| REQ-HOST-01 | Host history populated on connect | UT-HH-02, IT-HL-01 |
| REQ-HOST-02 | Host history capped at 10 entries | IT-HL-01 |
| REQ-HOST-03 | "\<Clear History\>" empties host list | UT-HH-01 |
| REQ-FILE-01 | File upload via SFTP works | UT-SSH-11, UT-APP-06 |
| REQ-FILE-02 | Output saved to text file | UT-APP-09 |
| REQ-FILE-03 | Output copied to clipboard | UT-APP-07 |
| REQ-FILE-04 | Save output with empty content is prevented | UT-APP-10 |
| REQ-FILE-05 | Save output write error handled gracefully | UT-APP-11 |
| REQ-FILE-06 | Output terminal can be cleared | UT-APP-12 |
| REQ-FILE-07 | Upload aborted when not connected | UT-APP-15 |
| REQ-FILE-08 | Upload aborted when file dialog cancelled | UT-APP-16 |
| REQ-FILE-09 | SFTP channel reused across multiple uploads | UT-SSH-15 |
| REQ-FILE-10 | Upload file when not connected raises error | UT-SSH-14 |
| REQ-PROF-01 | Profiles saved with connection details | UT-PR-01, UT-PR-08, IT-PW-01 |
| REQ-PROF-02 | Profiles loaded and fields populated | UT-PR-03, IT-PW-01 |
| REQ-PROF-03 | Missing profile handled gracefully | UT-PR-04, UT-PR-07 |
| REQ-PROF-04 | Profile deleted with confirmation | UT-PR-05, UT-PR-06 |
| REQ-PROF-05 | Save without name is rejected | UT-PR-02 |
| REQ-CFG-01 | Config persists to disk and reloads | IT-CR-01 |
| REQ-CFG-02 | Corrupt config falls back to defaults | IT-CR-02 |
| REQ-SEC-01 | Sections loaded from JSON file | IT-SJ-01 |
| REQ-SEC-02 | Missing/invalid sections file falls back to built-in | IT-SJ-02..04 |
| REQ-SEC-03 | Handler tokens resolved correctly | IT-SJ-01 |
| REQ-THEME-01 | All themes have required color keys | UT-TH-01, UT-TH-02 |
| REQ-THEME-02 | Solarized Dark uses canonical palette | UT-TH-03 |
| REQ-HK-01 | Host key mode validates to strict/warning/auto | UT-HK-01 |
| REQ-HK-02 | Invalid host key mode defaults to "warning" | UT-HK-02, UT-HK-03 |
| REQ-CRED-01 | Credentials cleared on disconnect when enabled | IT-DC-01 |
| REQ-CRED-02 | Credentials preserved when option disabled | IT-DC-02 |
| REQ-LOG-01 | Thread-safe logging via queue | UT-APP-08 |
| REQ-LOG-02 | Log messages include HH:MM:SS timestamp | UT-APP-17 |
| REQ-PARSE-01 | Integer input parsing with range validation | UT-PI-01..06 |
| REQ-START-01 | Startup errors logged to file for diagnostics | UT-SE-01 |
| REQ-CT-01 | Theme color values are valid hex/named | UT-CT-01 |
| REQ-CT-02 | Theme keys match apply_theme() usage | UT-CT-02 |
| REQ-CT-03 | sections.json conforms to expected schema | UT-CT-03 |
| REQ-CT-04 | sections.json commands use recognized tokens | UT-CT-04 |
| REQ-CT-05 | Profile config round-trip preserves schema | UT-CT-05 |
| REQ-CT-06 | SSHManager exposes expected public interface | UT-CT-06 |
| REQ-CT-07 | Controller classes expose expected methods | UT-CT-07 |
