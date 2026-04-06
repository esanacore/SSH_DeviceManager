# SSH Device Manager - Test Matrix
# SSH Device Manager - Test Matrix

> **Test File:** `test_SSH_DeviceManager.py`
> **Total Tests:** 92 (76 unit + 16 integration)
> **Last Updated:** 2026-04-05
> **Run Command:** `python -m unittest test_SSH_DeviceManager.py -v`

---

## Table of Contents

1. [Test Summary](#test-summary)
2. [Unit Tests](#unit-tests)
   - [Data Models](#1-data-models)
   - [SSH Manager](#2-ssh-manager)
   - [GUI App Core](#3-gui-app-core)
   - [Connection Input Validation](#4-connection-input-validation)
   - [Connect Error Handling](#5-connect-error-handling)
   - [Test Connection Error Handling](#6-test-connection-error-handling)
   - [Host Key Mode](#7-host-key-mode)
   - [Integer Input Parsing](#8-integer-input-parsing)
   - [Themes](#9-themes)
   - [Profiles](#10-profiles)
   - [Host History](#11-host-history)
   - [Connection State Monitor](#12-connection-state-monitor)
3. [Integration Tests](#integration-tests)
   - [Full Lifecycle](#13-connect--run--disconnect-lifecycle)
   - [Auth Failure Recovery](#14-auth-failure-recovery)
   - [Validation Blocks Connect](#15-validation-blocks-connect)
   - [Profile Workflow](#16-profile-workflow)
   - [Sections JSON Loading](#17-sections-json-loading)
   - [Command History](#18-command-history-integration)
   - [Command Failure Handling](#19-command-failure-handling)
   - [Config Round-Trip](#20-app-config-round-trip)
   - [Host History Limit](#21-host-history-limit)
   - [Disconnect Credential Clearing](#22-disconnect-credential-clearing)
4. [Requirements Traceability](#requirements-traceability)

---

## Test Summary

| Category | Class | Tests | Type |
|---|---|---|---|
| Shim Exports | `TestShimExports` | 2 | Unit |
| Data Models | `TestDataModels` | 2 | Unit |
| SSH Manager | `TestSSHManager` | 15 | Unit |
| GUI App Core | `TestSSHGuiApp` | 17 | Unit |
| Input Validation | `TestGetConnectionInputs` | 10 | Unit |
| Connect Errors | `TestOnConnectErrors` | 4 | Unit |
| Test Connection Errors | `TestTestConnectionErrors` | 2 | Unit |
| Host Key Mode | `TestGetHostKeyMode` | 3 | Unit |
| Int Parsing | `TestParseIntInput` | 6 | Unit |
| Themes | `TestThemes` | 3 | Unit |
| Profiles | `TestProfiles` | 8 | Unit |
| Connection State | `TestConnectionStateMonitor` | 2 | Unit |
| Host History | `TestHostHistory` | 2 | Unit |
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
| **TOTAL** | **23 classes** | **92** | |

---

## Unit Tests

### 1. Data Models

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-DM-01 | `test_action_button` | Create ActionButton with all fields | label, enabled, handler, tooltip stored correctly |
| UT-DM-02 | `test_button_section` | Create ButtonSection with nested ActionButton | title, max_buttons, actions list stored correctly |

### 2. SSH Manager

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

### 3. GUI App Core

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

### 4. Connection Input Validation

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

### 5. Connect Error Handling

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-CE-01 | `test_auth_exception` | `ssh.connect` raises `AuthenticationException` | Log contains "Authentication failed" and "Username and Password", UI set to disconnected |
| UT-CE-02 | `test_ssh_exception` | `ssh.connect` raises `SSHException` | Log contains "SSH error", UI set to disconnected |
| UT-CE-03 | `test_os_error` | `ssh.connect` raises `OSError` | Log contains "Network error", UI set to disconnected |
| UT-CE-04 | `test_generic_exception` | `ssh.connect` raises `RuntimeError` | Log contains "Connection failed", UI set to disconnected |

### 6. Test Connection Error Handling

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-TE-01 | `test_test_connection_auth_error` | Temp SSH raises `AuthenticationException` | Log contains "authentication rejected" |
| UT-TE-02 | `test_test_connection_os_error` | Temp SSH raises `OSError` | Log contains "network error" |

### 7. Host Key Mode

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-HK-01 | `test_valid_modes` | Input: "strict", "warning", "auto" | Each returns itself verbatim |
| UT-HK-02 | `test_invalid_mode_defaults_to_warning` | Input: "nonsense" | Returns "warning" |
| UT-HK-03 | `test_empty_mode_defaults_to_warning` | Input: "" | Returns "warning" |

### 8. Integer Input Parsing

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-PI-01 | `test_valid_int` | Input: "22", range 1-65535 | Returns `22` |
| UT-PI-02 | `test_non_numeric` | Input: "abc" | Returns `None` |
| UT-PI-03 | `test_empty_string` | Input: "" | Returns `None` |
| UT-PI-04 | `test_below_minimum` | Input: "0", min=1 | Returns `None` |
| UT-PI-05 | `test_above_maximum` | Input: "99999", max=65535 | Returns `None` |
| UT-PI-06 | `test_no_maximum` | Input: "999999", no upper bound | Returns `999999` |

### 9. Themes

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-TH-01 | `test_all_themes_have_required_keys` | All THEMES entries | Each has: bg, fg, text_bg, text_fg, entry_bg, entry_fg, select_bg, select_fg |
| UT-TH-02 | `test_all_themes_have_optional_keys` | All THEMES entries | Each has: btn_bg, border, label_fg |
| UT-TH-03 | `test_solarized_dark_uses_canonical_palette` | Solarized Dark values | bg=#002b36, entry_bg=#073642, select_bg=#268bd2, border=#586e75 |

### 10. Profiles

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

### 11. Host History

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-HH-01 | `test_on_host_selected_clear` | Select "\<Clear History\>" | History list emptied, host_var set to "" |
| UT-HH-02 | `test_connect_adds_to_host_history` | Connect with new host | Host added to `host_history` list |

### 12. Connection State Monitor

| ID | Test Method | Description | Verifies |
|---|---|---|---|
| UT-CS-01 | `test_detects_dropped_connection` | SSH session drops while status was "Connected" | UI set to disconnected, log warns "no longer active" |
| UT-CS-02 | `test_no_false_alarm_when_disconnected` | Status already "Disconnected", connection check runs | UI set to disconnected, NO spurious "no longer active" warning |

---

## Integration Tests

### 13. Connect -> Run -> Disconnect Lifecycle

| ID | Test Method | Flow |
|---|---|---|
| IT-LC-01 | `test_full_lifecycle` | **Connect** (verify `ssh.connect` args) -> **Run "show version"** (verify command, history[0]) -> **Run "show interfaces"** (verify history ordering) -> **Disconnect** (verify cleanup) -> **Verify log trail** contains Connecting, Connected, commands, Disconnecting |

### 14. Auth Failure Recovery

| ID | Test Method | Flow |
|---|---|---|
| IT-AF-01 | `test_auth_failure_then_success` | **Connect with wrong password** -> AuthenticationException raised -> "Authentication failed" logged, UI=disconnected -> **Fix password** -> **Connect again** -> Succeeds, UI=connected |

### 15. Validation Blocks Connect

| ID | Test Method | Flow |
|---|---|---|
| IT-VB-01 | `test_empty_fields_block_then_succeed` | **All fields empty** -> `on_connect()` -> Thread NOT spawned, all 3 errors logged (host, user, password) -> **Fill in all fields** -> `on_connect()` -> Thread spawned |

### 16. Profile Workflow

| ID | Test Method | Flow |
|---|---|---|
| IT-PW-01 | `test_save_load_connect` | **Fill fields** (router.local:2222, netadmin, s3cret, timeout=15) -> **Save as "RouterProfile"** -> Verify stored values -> **Load "RouterProfile"** -> Verify UI fields populated -> **Connect** -> Verify `ssh.connect` called with loaded values |

### 17. Sections JSON Loading

| ID | Test Method | Flow |
|---|---|---|
| IT-SJ-01 | `test_load_valid_sections_json` | Load JSON with 2 sections, 6 actions (plain cmd, `run:` prefix, `__upload_template__`, `__custom_command__`, `__send_file__`, disabled) -> Verify structure, labels, enabled flags, handler resolution to correct methods, all handlers callable |
| IT-SJ-02 | `test_load_missing_file_falls_back` | File doesn't exist -> Falls back to built-in `_define_sections()`, log contains "not found" |
| IT-SJ-03 | `test_load_invalid_json_falls_back` | File contains "NOT JSON" -> Falls back to built-in, log contains "ERROR" |
| IT-SJ-04 | `test_load_empty_sections_falls_back` | Valid JSON but `{"sections": []}` -> Falls back to built-in, log mentions "no sections" |

### 18. Command History Integration

| ID | Test Method | Flow |
|---|---|---|
| IT-CH-01 | `test_history_ordering_and_dedup` | Run cmd_a, cmd_b, cmd_c -> History = [cmd_c, cmd_b, cmd_a] -> Run cmd_a again -> History[0] = cmd_a (moved to front), count of cmd_a = 1 (no duplicates) |
| IT-CH-02 | `test_history_limit` | Run COMMAND_HISTORY_LIMIT + 50 unique commands -> History length <= COMMAND_HISTORY_LIMIT |

### 19. Command Failure Handling

| ID | Test Method | Flow |
|---|---|---|
| IT-CF-01 | `test_command_error_then_disconnect` | **Connect** -> **Run command** that raises RuntimeError("channel closed") -> Error logged with "channel closed" -> **Disconnect** -> Graceful cleanup, no crash |

### 20. App Config Round-Trip

| ID | Test Method | Flow |
|---|---|---|
| IT-CR-01 | `test_config_round_trip` | Create 2 profiles -> `_save_app_config()` to real temp file -> `_load_app_config()` from disk -> All profile data intact (hosts, ports, usernames, host_key_modes) |
| IT-CR-02 | `test_corrupt_config_returns_default` | Write invalid JSON to temp file -> `_load_app_config()` -> Returns default config `{"profiles": {}}`, no crash |

### 21. Host History Limit

| ID | Test Method | Flow |
|---|---|---|
| IT-HL-01 | `test_history_capped_at_10` | Connect to 15 different hosts sequentially -> History length <= 10, most recent host is first |

### 22. Disconnect Credential Clearing

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
