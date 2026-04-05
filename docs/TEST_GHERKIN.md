# SSH Device Manager - Test Specifications (Gherkin)

> **Test File:** `test_SSH_DeviceManager.py`
> **Total Scenarios:** 74
> **Last Updated:** 2025-01-XX
> **Format:** Gherkin (Given/When/Then) for requirements traceability

---

## Table of Contents

1. [Data Models](#feature-data-models)
2. [SSH Manager](#feature-ssh-manager)
3. [GUI App Core](#feature-gui-app-core)
4. [Connection Input Validation](#feature-connection-input-validation)
5. [Connect Error Handling](#feature-connect-error-handling)
6. [Test Connection Error Handling](#feature-test-connection-error-handling)
7. [Host Key Mode](#feature-host-key-mode)
8. [Integer Input Parsing](#feature-integer-input-parsing)
9. [Themes](#feature-themes)
10. [Profiles](#feature-profiles)
11. [Host History](#feature-host-history)
12. [Connect-Run-Disconnect Lifecycle](#feature-connect-run-disconnect-lifecycle)
13. [Auth Failure Recovery](#feature-auth-failure-recovery)
14. [Validation Blocks Connect](#feature-validation-blocks-connect)
15. [Profile Workflow](#feature-profile-workflow)
16. [Sections JSON Loading](#feature-sections-json-loading)
17. [Command History](#feature-command-history)
18. [Command Failure Handling](#feature-command-failure-handling)
19. [App Config Persistence](#feature-app-config-persistence)
20. [Host History Limit](#feature-host-history-limit)
21. [Disconnect Credential Clearing](#feature-disconnect-credential-clearing)

---

## Feature: Data Models

```gherkin
Feature: Data Models
  The application uses dataclass models to define UI buttons and sections.

  @unit @UT-DM-01
  Scenario: Create an ActionButton with all fields
    Given a callable handler function
    When I create an ActionButton with label "Label", enabled True, handler, and tooltip "Tooltip"
    Then the button label is "Label"
    And the button enabled state is True
    And the button handler is the provided function
    And the button tooltip is "Tooltip"

  @unit @UT-DM-02
  Scenario: Create a ButtonSection with nested ActionButton
    Given an ActionButton with label "Label" and enabled True
    When I create a ButtonSection with title "Title", max_buttons 5, and actions containing that button
    Then the section title is "Title"
    And the section max_buttons is 5
    And the section actions list contains the button
```

---

## Feature: SSH Manager

```gherkin
Feature: SSH Manager
  The SSHManager wraps Paramiko for connect, disconnect, command execution,
  and file upload operations.

  @unit @UT-SSH-01
  Scenario: Not connected when no client exists
    Given an SSHManager with no client set
    When I check is_connected
    Then the result is False

  @unit @UT-SSH-02
  Scenario: Connected when transport is active
    Given an SSHManager with a client whose transport is active
    When I check is_connected
    Then the result is True

  @unit @UT-SSH-03
  Scenario: Dead transport triggers auto-disconnect
    Given an SSHManager with a client whose transport is NOT active
    When I check is_connected
    Then the result is False
    And the client is set to None
    And the SFTP reference is set to None

  @unit @UT-SSH-04
  Scenario: No transport triggers auto-disconnect
    Given an SSHManager with a client that returns None for get_transport
    When I check is_connected
    Then the result is False
    And the client is set to None

  @unit @UT-SSH-05
  Scenario: Connect with valid credentials
    Given an SSHManager
    When I call connect with host "host", port 22, user "user", password "pass"
    Then a Paramiko SSHClient is created
    And a missing host key policy is set
    And SSHClient.connect is called with the provided credentials
    And the client reference is not None
    And the host_key is stored as "host"

  @unit @UT-SSH-06
  Scenario: Disconnect cleans up all resources
    Given an SSHManager with an active client and SFTP session
    When I call disconnect
    Then the SFTP session is closed
    And the SSH client is closed
    And the client reference is set to None
    And the SFTP reference is set to None
    And the host_key is set to None

  @unit @UT-SSH-07
  Scenario: Disconnect handles close errors gracefully
    Given an SSHManager with a client that raises OSError on close
    When I call disconnect
    Then no exception is propagated
    And the client reference is set to None

  @unit @UT-SSH-08
  Scenario: Run command without connection raises error
    Given an SSHManager with no client
    When I call run_command with "ls"
    Then a RuntimeError is raised

  @unit @UT-SSH-09
  Scenario: Run command returns decoded output
    Given an SSHManager with a connected client
    And exec_command returns stdout "output" and empty stderr
    When I call run_command with "ls"
    Then the result is "output"
    And exec_command was called with "ls" and timeout 30

  @unit @UT-SSH-10
  Scenario: Run command handles invalid UTF-8 bytes
    Given an SSHManager with a connected client
    And exec_command returns stdout containing byte 0x80 and empty stderr
    When I call run_command with "ls"
    Then the result is a string (no UnicodeDecodeError)
    And the result contains the Unicode replacement character U+FFFD

  @unit @UT-SSH-11
  Scenario: Upload file via SFTP
    Given an SSHManager with a connected client
    When I call upload_file with local "local" and remote "remote"
    Then an SFTP session is opened
    And sftp.put is called with "local" and "remote"
```

---

## Feature: GUI App Core

```gherkin
Feature: GUI App Core
  The SSHGuiApp manages connection, command execution, output, and UI state.

  @unit @UT-APP-01
  Scenario: App initializes with valid state
    When I create an SSHGuiApp with init_ui=False
    Then the SSH manager exists
    And the sections list is not empty
    And every section is a valid ButtonSection with at least one action

  @unit @UT-APP-02
  Scenario: on_connect spawns worker thread with correct args
    Given a connected app with host "192.168.1.1", port 22, user "admin", password "password"
    When I call on_connect
    Then a background thread is spawned
    And the worker calls ssh.connect with the provided credentials and host_key_mode "warning"

  @unit @UT-APP-03
  Scenario: on_disconnect clears credentials when option enabled
    Given an app with clear_creds_var set to True
    When I call on_disconnect
    Then ssh.disconnect is called
    And the password field is cleared to ""
    And the UI is set to disconnected state

  @unit @UT-APP-04
  Scenario: test_connection creates temporary SSH session
    Given an app that is not currently connected
    And valid connection fields are filled in
    When I call test_connection
    Then a background thread is spawned
    And a temporary SSHManager is created, connected, and disconnected

  @unit @UT-APP-05
  Scenario: run_ssh_command executes command and updates history
    Given an app that is connected
    When I call run_ssh_command with "show version"
    Then "show version" is added to command_history at index 0
    And a background thread is spawned
    And ssh.run_command is called with "show version"

  @unit @UT-APP-06
  Scenario: upload_config_template uploads selected file
    Given an app that is connected
    And the file dialog returns "/path/to/file"
    When I call upload_config_template
    Then a background thread is spawned
    And ssh.upload_file is called with "/path/to/file" and "/tmp/uploaded_config.txt"

  @unit @UT-APP-07
  Scenario: Copy output to clipboard
    Given an app with output text "some output"
    When I call copy_output
    Then the clipboard is cleared
    And "some output" is appended to the clipboard

  @unit @UT-APP-08
  Scenario: Log message is queued with timestamp
    Given an app
    When I call log with "test message"
    Then the log_queue is not empty
    And the queued message contains "test message"

  @unit @UT-APP-09
  Scenario: Save output to file
    Given an app with output text "some output"
    And the save dialog returns "/tmp/saved_output.txt"
    When I call save_output
    Then the file "/tmp/saved_output.txt" is opened for writing
    And "some output" is written to the file
```

---

## Feature: Connection Input Validation

```gherkin
Feature: Connection Input Validation
  All connection fields are validated individually before connect attempts.
  Each problem is reported with a specific message.

  @unit @UT-VAL-01
  Scenario: All fields valid
    Given host "192.168.1.1", port 22, user "admin", password "secret", timeout 10
    When I call _get_connection_inputs
    Then a tuple (host, port, user, pw, timeout) is returned

  @unit @UT-VAL-02
  Scenario: Empty host is rejected
    Given host "", port 22, user "admin", password "secret", timeout 10
    When I call _get_connection_inputs
    Then None is returned
    And the log contains "Host / IP is empty"

  @unit @UT-VAL-03
  Scenario: Empty username is rejected
    Given host "192.168.1.1", port 22, user "", password "secret", timeout 10
    When I call _get_connection_inputs
    Then None is returned
    And the log contains "Username is empty"

  @unit @UT-VAL-04
  Scenario: Empty password is rejected
    Given host "192.168.1.1", port 22, user "admin", password "", timeout 10
    When I call _get_connection_inputs
    Then None is returned
    And the log contains "Password is empty"

  @unit @UT-VAL-05
  Scenario: Multiple empty fields reported together
    Given host "", port 22, user "", password "", timeout 10
    When I call _get_connection_inputs
    Then None is returned
    And the log contains "Host / IP is empty"
    And the log contains "Username is empty"
    And the log contains "Password is empty"

  @unit @UT-VAL-06
  Scenario: Blank port field (TclError) is rejected
    Given a port variable that raises TclError on .get()
    When I call _get_connection_inputs
    Then None is returned
    And the log contains "Port"

  @unit @UT-VAL-07
  Scenario: Port out of range is rejected
    Given port 99999
    When I call _get_connection_inputs
    Then None is returned
    And the log contains "Port must be between"

  @unit @UT-VAL-08
  Scenario: Port zero is rejected
    Given port 0
    When I call _get_connection_inputs
    Then None is returned

  @unit @UT-VAL-09
  Scenario: Blank timeout field (TclError) is rejected
    Given a timeout variable that raises TclError on .get()
    When I call _get_connection_inputs
    Then None is returned
    And the log contains "Connection Timeout"

  @unit @UT-VAL-10
  Scenario: Timeout out of range is rejected
    Given timeout 999
    When I call _get_connection_inputs
    Then None is returned
    And the log contains "Connection Timeout must be between"
```

---

## Feature: Connect Error Handling

```gherkin
Feature: Connect Error Handling
  Specific SSH exceptions produce actionable error messages in the terminal.

  @unit @UT-CE-01
  Scenario: Authentication exception shows credential guidance
    Given an app configured with valid connection fields
    And ssh.connect raises paramiko.AuthenticationException
    When the on_connect worker executes
    Then the log contains "Authentication failed"
    And the log contains "Username and Password"
    And the UI is set to disconnected

  @unit @UT-CE-02
  Scenario: SSH exception shows protocol guidance
    Given an app configured with valid connection fields
    And ssh.connect raises paramiko.SSHException
    When the on_connect worker executes
    Then the log contains "SSH error"
    And the UI is set to disconnected

  @unit @UT-CE-03
  Scenario: OS error shows network guidance
    Given an app configured with valid connection fields
    And ssh.connect raises OSError("No route to host")
    When the on_connect worker executes
    Then the log contains "Network error"
    And the UI is set to disconnected

  @unit @UT-CE-04
  Scenario: Unknown exception shows generic error
    Given an app configured with valid connection fields
    And ssh.connect raises RuntimeError("unexpected")
    When the on_connect worker executes
    Then the log contains "Connection failed"
```

---

## Feature: Test Connection Error Handling

```gherkin
Feature: Test Connection Error Handling
  The Test Connection feature surfaces the same specific error messages.

  @unit @UT-TE-01
  Scenario: Test connection auth error
    Given an app that is not connected with valid fields
    And the temporary SSHManager raises AuthenticationException
    When the test_connection worker executes
    Then the log contains "authentication rejected"

  @unit @UT-TE-02
  Scenario: Test connection network error
    Given an app that is not connected with valid fields
    And the temporary SSHManager raises OSError
    When the test_connection worker executes
    Then the log contains "network error"
```

---

## Feature: Host Key Mode

```gherkin
Feature: Host Key Mode
  The host key policy setting validates to known values.

  @unit @UT-HK-01
  Scenario Outline: Valid host key modes accepted
    Given the host_key_mode_var is set to "<mode>"
    When I call _get_host_key_mode
    Then the result is "<mode>"

    Examples:
      | mode    |
      | strict  |
      | warning |
      | auto    |

  @unit @UT-HK-02
  Scenario: Invalid mode defaults to warning
    Given the host_key_mode_var is set to "nonsense"
    When I call _get_host_key_mode
    Then the result is "warning"

  @unit @UT-HK-03
  Scenario: Empty mode defaults to warning
    Given the host_key_mode_var is set to ""
    When I call _get_host_key_mode
    Then the result is "warning"
```

---

## Feature: Integer Input Parsing

```gherkin
Feature: Integer Input Parsing
  The _parse_int_input method validates string inputs as bounded integers.

  @unit @UT-PI-01
  Scenario: Valid integer within range
    Given input "22" with label "Port", minimum 1, maximum 65535
    When I call _parse_int_input
    Then the result is 22

  @unit @UT-PI-02
  Scenario: Non-numeric input rejected
    Given input "abc" with label "Port", minimum 1, maximum 65535
    When I call _parse_int_input
    Then the result is None

  @unit @UT-PI-03
  Scenario: Empty string rejected
    Given input "" with label "Port", minimum 1, maximum 65535
    When I call _parse_int_input
    Then the result is None

  @unit @UT-PI-04
  Scenario: Value below minimum rejected
    Given input "0" with label "Port", minimum 1, maximum 65535
    When I call _parse_int_input
    Then the result is None

  @unit @UT-PI-05
  Scenario: Value above maximum rejected
    Given input "99999" with label "Port", minimum 1, maximum 65535
    When I call _parse_int_input
    Then the result is None

  @unit @UT-PI-06
  Scenario: No upper bound allows large values
    Given input "999999" with label "Count", minimum 1, no maximum
    When I call _parse_int_input
    Then the result is 999999
```

---

## Feature: Themes

```gherkin
Feature: Themes
  All themes must define required color keys for consistent rendering.

  @unit @UT-TH-01
  Scenario: All themes have required color keys
    Given the THEMES dictionary
    When I check each theme
    Then every theme contains keys: bg, fg, text_bg, text_fg, entry_bg, entry_fg, select_bg, select_fg

  @unit @UT-TH-02
  Scenario: All themes have optional extended keys
    Given the THEMES dictionary
    When I check each theme
    Then every theme contains keys: btn_bg, border, label_fg

  @unit @UT-TH-03
  Scenario: Solarized Dark uses canonical palette values
    Given the "Solarized Dark" theme
    Then bg is "#002b36" (base03)
    And entry_bg is "#073642" (base02)
    And select_bg is "#268bd2" (blue)
    And border is "#586e75" (base01)
```

---

## Feature: Profiles

```gherkin
Feature: Profiles
  Connection profiles can be saved, loaded, and deleted.

  @unit @UT-PR-01
  Scenario: Save a profile with valid data
    Given an app with host "10.0.0.1", port 22, user "root", password "password"
    And profile_name_var is "MyProfile"
    When I call save_profile
    Then "MyProfile" exists in app_config["profiles"]
    And the saved host is "10.0.0.1"
    And the saved port is 22
    And the saved username is "root"
    And _save_app_config is called

  @unit @UT-PR-02
  Scenario: Save with no profile name is rejected
    Given profile_name_var is "" and profile_select_var is ""
    When I call save_profile
    Then _get_connection_inputs is never called
    And _save_app_config is never called

  @unit @UT-PR-03
  Scenario: Load an existing profile populates fields
    Given a saved profile "TestProf" with host "1.2.3.4", port 2222, user "testuser", timeout 30
    When I call load_selected_profile with "TestProf"
    Then host_var is set to "1.2.3.4"
    And port_var is set to 2222
    And user_var is set to "testuser"
    And timeout_var is set to 30

  @unit @UT-PR-04
  Scenario: Load a missing profile does not crash
    Given no profile named "DoesNotExist" exists
    When I call load_selected_profile with "DoesNotExist"
    Then host_var.set is never called

  @unit @UT-PR-05
  Scenario: Delete a profile with confirmation
    Given a saved profile "ToDelete"
    And the confirmation dialog returns True
    When I call delete_selected_profile
    Then "ToDelete" is removed from app_config["profiles"]
    And _save_app_config is called

  @unit @UT-PR-06
  Scenario: Delete a profile cancelled by user
    Given a saved profile "KeepMe"
    And the confirmation dialog returns False
    When I call delete_selected_profile
    Then "KeepMe" still exists in app_config["profiles"]
```

---

## Feature: Host History

```gherkin
Feature: Host History
  The host combobox tracks recently connected hosts.

  @unit @UT-HH-01
  Scenario: Clear host history
    Given host_history contains ["10.0.0.1", "10.0.0.2"]
    And the user selects "<Clear History>"
    When on_host_selected fires
    Then host_history is empty
    And host_var is set to ""

  @unit @UT-HH-02
  Scenario: Connect adds host to history
    Given host_history is empty
    When I connect to "newhost.example.com"
    Then "newhost.example.com" is in host_history
```

---

## Feature: Connect-Run-Disconnect Lifecycle

```gherkin
Feature: Connect-Run-Disconnect Lifecycle
  Full end-to-end workflow from connect through command execution to disconnect.

  @integration @IT-LC-01
  Scenario: Complete session lifecycle
    Given an app with host "10.0.0.1", user "admin", password "secret"
    When I connect
    Then ssh.connect is called with the correct arguments
    And the UI is set to connected

    When I run "show version"
    Then command_history[0] is "show version"
    And ssh.run_command is called with "show version"

    When I run "show interfaces"
    Then command_history[0] is "show interfaces"
    And command_history[1] is "show version"

    When I disconnect
    Then ssh.disconnect is called
    And the UI is set to disconnected

    Then the log trail contains "Connecting", "[OK] Connected", "show version", "Disconnecting"
```

---

## Feature: Auth Failure Recovery

```gherkin
Feature: Auth Failure Recovery
  User can recover from a failed authentication by correcting credentials.

  @integration @IT-AF-01
  Scenario: Wrong password then correct password
    Given an app with password "wrong_password"
    And ssh.connect raises AuthenticationException

    When I call on_connect
    And the worker executes
    Then the log contains "Authentication failed"
    And the UI is set to disconnected

    When I change the password to "correct_password"
    And ssh.connect no longer raises
    And I call on_connect again
    And the worker executes
    Then ssh.connect is called with "correct_password"
    And the UI is set to connected
```

---

## Feature: Validation Blocks Connect

```gherkin
Feature: Validation Blocks Connect
  Empty fields prevent connect; filling them in allows connection.

  @integration @IT-VB-01
  Scenario: All fields empty then filled in
    Given host is "", username is "", password is ""
    When I call on_connect
    Then no background thread is spawned
    And the log contains "Host / IP is empty"
    And the log contains "Username is empty"
    And the log contains "Password is empty"

    When I set host to "10.0.0.1", username to "admin", password to "secret"
    And I call on_connect
    Then a background thread IS spawned
```

---

## Feature: Profile Workflow

```gherkin
Feature: Profile Workflow
  Save profile, load it later, and connect using loaded values.

  @integration @IT-PW-01
  Scenario: Save, load, and connect with profile
    Given an app with host "router.local", port 2222, user "netadmin", password "s3cret", timeout 15

    When I save profile as "RouterProfile"
    Then "RouterProfile" is stored with host "router.local", port 2222, user "netadmin", timeout 15

    When I load profile "RouterProfile"
    Then host_var is set to "router.local"
    And port_var is set to 2222
    And user_var is set to "netadmin"
    And timeout_var is set to 15

    When I connect
    Then ssh.connect is called with host "router.local", port 2222, user "netadmin", password "s3cret", timeout 15
```

---

## Feature: Sections JSON Loading

```gherkin
Feature: Sections JSON Loading
  Button sections can be defined in an external JSON file.

  @integration @IT-SJ-01
  Scenario: Load valid sections JSON with all handler types
    Given a JSON file with 2 sections:
      | Section      | Actions                                                          |
      | Diagnostics  | Ping (plain cmd), Disk (run: prefix), Upload (__upload_template__), Custom (__custom_command__), SCP (__send_file__), Disabled (enabled=false) |
      | Empty Section| (no actions)                                                     |
    When I call load_sections_from_file
    Then 2 sections are returned
    And the Diagnostics section has 6 actions
    And the "Ping" action is enabled
    And the "Disabled" action is NOT enabled
    And the "Upload" handler resolves to upload_config_template
    And the "Custom" handler resolves to prompt_and_run_custom_command
    And the "SCP" handler resolves to send_file_scp
    And all handlers are callable

  @integration @IT-SJ-02
  Scenario: Missing file falls back to built-in sections
    Given the sections file does not exist
    When I call load_sections_from_file
    Then built-in sections are returned
    And the log contains "not found"

  @integration @IT-SJ-03
  Scenario: Invalid JSON falls back to built-in sections
    Given the sections file contains "NOT JSON"
    When I call load_sections_from_file
    Then built-in sections are returned
    And the log contains "ERROR"

  @integration @IT-SJ-04
  Scenario: Empty sections array falls back to built-in sections
    Given the sections file contains {"sections": []}
    When I call load_sections_from_file
    Then built-in sections are returned
    And the log mentions "no sections"
```

---

## Feature: Command History

```gherkin
Feature: Command History
  Commands are tracked in order with deduplication and a size limit.

  @integration @IT-CH-01
  Scenario: History ordering and deduplication
    Given an app that is connected
    When I run "cmd_a" then "cmd_b" then "cmd_c"
    Then command_history is ["cmd_c", "cmd_b", "cmd_a"]

    When I run "cmd_a" again
    Then command_history[0] is "cmd_a"

  @integration @IT-CH-02
  Scenario: History respects COMMAND_HISTORY_LIMIT
    Given an app that is connected
    When I run COMMAND_HISTORY_LIMIT + 50 unique commands
    Then the history length is at most COMMAND_HISTORY_LIMIT
```

---

## Feature: Command Failure Handling

```gherkin
Feature: Command Failure Handling
  A failed command logs the error but does not prevent further operations.

  @integration @IT-CF-01
  Scenario: Command fails then disconnect succeeds
    Given an app that is connected
    And ssh.run_command raises RuntimeError("channel closed")
    When I run "bad_command"
    And the worker executes
    Then the log contains "ERROR" and "channel closed"

    When I disconnect
    Then ssh.disconnect is called
    And the UI is set to disconnected
    And no exception is raised
```

---

## Feature: App Config Persistence

```gherkin
Feature: App Config Persistence
  Application configuration (profiles) persists to a JSON file on disk.

  @integration @IT-CR-01
  Scenario: Config round-trip to disk
    Given an app with 2 profiles:
      | Name    | Host    | Port | Username | Timeout | Host Key Mode |
      | Server1 | 1.1.1.1 | 22   | root     | 10      | auto          |
      | Server2 | 2.2.2.2 | 2222 | admin    | 30      | strict        |
    When I call _save_app_config to a temp file
    And I call _load_app_config from the same file
    Then "Server1" is present with host "1.1.1.1"
    And "Server2" is present with port 2222 and host_key_mode "strict"

  @integration @IT-CR-02
  Scenario: Corrupt config file returns defaults
    Given a config file containing "NOT VALID JSON {{{"
    When I call _load_app_config
    Then the result contains an empty "profiles" dictionary
    And no exception is raised
```

---

## Feature: Host History Limit

```gherkin
Feature: Host History Limit
  The host history is capped at 10 entries.

  @integration @IT-HL-01
  Scenario: History capped at 10 after many connections
    Given an app
    When I connect to 15 different hosts sequentially
    Then host_history has at most 10 entries
    And the most recently connected host is at index 0
```

---

## Feature: Disconnect Credential Clearing

```gherkin
Feature: Disconnect Credential Clearing
  Password can optionally be cleared on disconnect.

  @integration @IT-DC-01
  Scenario: Credentials cleared when option is enabled
    Given clear_creds_var is True
    When I disconnect
    Then pass_var is set to ""
    And the log contains "Credentials cleared"

  @integration @IT-DC-02
  Scenario: Credentials preserved when option is disabled
    Given clear_creds_var is False
    When I disconnect
    Then pass_var.set is NOT called
```
