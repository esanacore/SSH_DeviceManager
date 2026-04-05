# How to Read the Test Documentation
# How to Read the Test Documentation

This guide explains the structure, terminology, and ID systems used in the two
test documents so that any team member
can navigate them confidently.

---

## Document Overview

```
docs/
  TEST_MATRIX.md    <-- Technical reference (tables, IDs, traceability)
  TEST_GHERKIN.md   <-- Behavioral specs (plain-English scenarios)
  READING_GUIDE.md  <-- You are here
```

| Document | Audience | Purpose |
|---|---|---|
| **TEST_MATRIX.md** | Developers, QA leads, auditors | Lookup any test by ID, see exactly what it asserts, trace it back to a requirement |
| **TEST_GHERKIN.md** | Product owners, QA, non-developers | Understand *what the app should do* in plain English without reading code |

Both documents describe the **same 74 tests**. They are two views of the same
data — one structured for machines/databases, one structured for humans.

---

## Part 1: Reading TEST_MATRIX.md

### 1.1 Header Block

```
> Test File: test_SSH_DeviceManager.py
> Total Tests: 74 (58 unit + 16 integration)
> Run Command: python -m unittest test_SSH_DeviceManager.py -v
```

This tells you which source file contains the actual Python test code, how many
tests exist, and the exact command to run them. If the total here doesn't match
what `python -m unittest` reports, the document is out of date.

### 1.2 Test Summary Table

```
| Category         | Class                             | Tests | Type        |
|------------------|-----------------------------------|-------|-------------|
| Data Models      | TestDataModels                    | 2     | Unit        |
| SSH Manager      | TestSSHManager                    | 11    | Unit        |
| Full Lifecycle   | TestConnectRunDisconnectLifecycle  | 1     | Integration |
```

How to read each column:

| Column | Meaning |
|---|---|
| **Category** | Human-friendly group name (e.g. "Input Validation") |
| **Class** | The exact `unittest.TestCase` class name in `test_SSH_DeviceManager.py` |
| **Tests** | Number of `test_*` methods inside that class |
| **Type** | **Unit** = tests one method in isolation; **Integration** = tests a multi-step flow |

The **TOTAL** row at the bottom is your quick health check: 21 classes, 74 tests.

### 1.3 Unit Test Detail Tables

Each numbered section (e.g. "### 2. SSH Manager") contains a table like this:

```
| ID         | Test Method                    | Description                    | Verifies                                  |
|------------|--------------------------------|--------------------------------|-------------------------------------------|
| UT-SSH-03  | test_is_connected_dead_transport | Client with dead transport   | Returns False, auto-disconnects, clears   |
```

Column definitions:

| Column | Meaning | Example |
|---|---|---|
| **ID** | Unique, stable identifier you can reference in bug tickets, Jira, TestRail, etc. | `UT-SSH-03` |
| **Test Method** | Exact Python method name — you can search the test file for this string | `test_is_connected_dead_transport` |
| **Description** | One-line summary of the setup / scenario | "Client with dead transport" |
| **Verifies** | The specific assertions made — what *must* be true for the test to pass | "Returns False, auto-disconnects, clears client" |

### 1.4 Integration Test Detail Tables

Integration tables use a slightly different format:

```
| ID        | Test Method                    | Flow                                                |
|-----------|--------------------------------|-----------------------------------------------------|
| IT-LC-01  | test_full_lifecycle            | Connect -> Run "show version" -> Run "show..."  -> |
```

The **Flow** column replaces Description + Verifies with a step-by-step
narrative using `->` arrows. Bold text marks the user-visible actions.
Each arrow represents a sequential dependency — Step 2 can't happen without
Step 1 succeeding.

### 1.5 The ID System

Every test has a unique ID with a predictable structure:

```
  UT-SSH-03
  ^^  ^^^  ^^
  |   |    |
  |   |    +-- Sequence number (01, 02, 03...)
  |   +------- Category code (see table below)
  +----------- Type prefix: UT = Unit Test, IT = Integration Test
```

#### Category Codes

| Code | Full Name | Maps To |
|---|---|---|
| DM | Data Models | `TestDataModels` |
| SSH | SSH Manager | `TestSSHManager` |
| APP | GUI App Core | `TestSSHGuiApp` |
| VAL | Connection Input Validation | `TestGetConnectionInputs` |
| CE | Connect Errors | `TestOnConnectErrors` |
| TE | Test Connection Errors | `TestTestConnectionErrors` |
| HK | Host Key Mode | `TestGetHostKeyMode` |
| PI | Parse Integer Input | `TestParseIntInput` |
| TH | Themes | `TestThemes` |
| PR | Profiles | `TestProfiles` |
| HH | Host History | `TestHostHistory` |
| LC | Lifecycle | `TestConnectRunDisconnectLifecycle` |
| AF | Auth Failure | `TestConnectAuthFailureRetry` |
| VB | Validation Blocks | `TestValidationBlocksConnect` |
| PW | Profile Workflow | `TestProfileWorkflow` |
| SJ | Sections JSON | `TestSectionsJsonLoading` |
| CH | Command History | `TestCommandHistoryIntegration` |
| CF | Command Failure | `TestCommandFailureHandling` |
| CR | Config Round-trip | `TestAppConfigRoundTrip` |
| HL | Host History Limit | `TestHostHistoryLimit` |
| DC | Disconnect Credentials | `TestDisconnectClearsCredentials` |

#### Example lookups

> "What tests cover the password validation?"
> ? Search the ID column for `UT-VAL-04` (empty password) and `IT-VB-01`
>   (integration test that includes empty password in the flow).

> "Test UT-CE-01 failed in CI — what broke?"
> ? Find `UT-CE-01` in section 5. It tests that `AuthenticationException`
>   produces "Authentication failed" in the log. The method name is
>   `test_auth_exception` in class `TestOnConnectErrors`.

### 1.6 Requirements Traceability Matrix (RTM)

The final section connects **requirements** to **tests**:

```
| Requirement  | Description                                    | Test IDs                    |
|--------------|------------------------------------------------|-----------------------------|
| REQ-VAL-03   | Empty Password is rejected with specific msg   | UT-VAL-04, IT-VB-01         |
```

How to read each column:

| Column | Meaning |
|---|---|
| **Requirement** | A stable requirement ID using the `REQ-` prefix |
| **Description** | What the system *must* do |
| **Test IDs** | Which tests prove this requirement works (comma-separated) |

#### Requirement ID prefixes

| Prefix | Domain |
|---|---|
| REQ-CONN | SSH connection management |
| REQ-VAL | Input validation |
| REQ-ERR | Error handling / messages |
| REQ-CMD | Command execution |
| REQ-HIST | Command history |
| REQ-HOST | Host combobox history |
| REQ-FILE | File operations (upload, save, copy) |
| REQ-PROF | Connection profiles |
| REQ-CFG | Config file persistence |
| REQ-SEC | Button sections / JSON loading |
| REQ-THEME | Theme system |
| REQ-HK | Host key policy |
| REQ-CRED | Credential management |
| REQ-LOG | Logging system |
| REQ-PARSE | Input parsing utilities |

#### How to use the RTM

**Forward trace** (requirement ? tests):
> "Is REQ-ERR-01 tested?" ? Find `REQ-ERR-01` in the Requirement column ?
> Test IDs are `UT-CE-01, UT-TE-01, IT-AF-01` ? Three tests cover it.

**Reverse trace** (test ? requirement):
> "What requirement does UT-SSH-10 prove?" ? Search the Test IDs column for
> `UT-SSH-10` ? Found in `REQ-CMD-03`: "Invalid UTF-8 in output handled with
> replacement."

**Gap analysis**:
> If a requirement has no Test IDs, it's untested. If a test ID appears in no
> requirement row, it may be testing implementation detail rather than a
> requirement.

---

## Part 2: Reading TEST_GHERKIN.md

### 2.1 What is Gherkin?

Gherkin is a structured plain-English format for describing software behavior.
It was created for the BDD (Behavior-Driven Development) methodology. You don't
need any programming knowledge to read it.

The three core keywords:

| Keyword | Meaning | Analogy |
|---|---|---|
| **Given** | The starting state / preconditions | "Assume the following is already true..." |
| **When** | The action the user or system takes | "The user clicks / the system does..." |
| **Then** | The expected result / what we verify | "We expect to see..." |
| **And** | Continues the previous Given/When/Then | (same meaning as above, avoids repetition) |

### 2.2 Document Structure

```
## Feature: SSH Manager               <-- Feature = a capability of the app

  ```gherkin
  Feature: SSH Manager
    Description text here...

    @unit @UT-SSH-01                   <-- Tags (type + ID)
    Scenario: Not connected when...    <-- One test case
      Given ...                        <-- Setup
      When ...                         <-- Action
      Then ...                         <-- Expected result
  ```
```

Each **Feature** block maps to one test class. Each **Scenario** maps to one
`test_*` method.

### 2.3 Tags

Tags appear on the line above each Scenario:

```
@unit @UT-SSH-03
Scenario: Dead transport triggers auto-disconnect
```

| Tag | Purpose |
|---|---|
| `@unit` | This is a unit test (isolated, single-method) |
| `@integration` | This is an integration test (multi-step flow) |
| `@UT-SSH-03` | Cross-reference ID — same as in TEST_MATRIX.md |

Tags let you filter scenarios. In a BDD runner like `behave`:
```bash
behave --tags=@integration          # Run only integration tests
behave --tags=@UT-VAL-04            # Run one specific test
```

In a test management tool (Jira Xray, TestRail), import tags as labels.

### 2.4 Reading a Simple Scenario

```gherkin
@unit @UT-VAL-04
Scenario: Empty password is rejected
  Given host "192.168.1.1", port 22, user "admin", password "", timeout 10
  When I call _get_connection_inputs
  Then None is returned
  And the log contains "Password is empty"
```

Read it like a sentence:

> **Assuming** the host is "192.168.1.1", port is 22, user is "admin", the
> password is blank, and timeout is 10...
> **when** the system validates the connection inputs...
> **then** the validation rejects them (returns None),
> **and** the terminal log shows "Password is empty".

### 2.5 Reading a Multi-Step Integration Scenario

```gherkin
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

Notice the blank lines — they visually separate **phases** of the test:
1. Phase 1: Attempt with wrong password ? fails
2. Phase 2: Fix password ? succeeds

Each phase has its own Given/When/Then block. The scenario reads like a story.

### 2.6 Scenario Outlines (Parameterized)

```gherkin
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
```

A **Scenario Outline** is a template that runs once for every row in the
**Examples** table. The `<mode>` placeholder is replaced with each value.
This one scenario actually represents 3 test executions.

### 2.7 Feature Descriptions

The text between `Feature:` and the first Scenario is a description:

```gherkin
Feature: SSH Manager
  The SSHManager wraps Paramiko for connect, disconnect, command execution,
  and file upload operations.
```

This is not executable — it's documentation for the reader explaining *what
this group of scenarios is about* and *why it exists*.

---

## Part 3: Cross-Referencing Between Documents

The two documents share IDs. Here's how to jump between them:

```
  TEST_MATRIX.md                         TEST_GHERKIN.md
  ????????????????????????               ????????????????????????
  ? ## 5. Connect Errors ?               ? ## Feature: Connect  ?
  ?                      ?               ?    Error Handling     ?
  ? | UT-CE-01 | test_.. ????? same ????? @unit @UT-CE-01      ?
  ? |          |         ?     ID        ? Scenario: Auth...    ?
  ? | Verifies: log has  ?               ?   Given ...          ?
  ? |  "Auth failed"     ?               ?   When ...           ?
  ?                      ?               ?   Then log contains  ?
  ?                      ?               ?    "Auth failed"     ?
  ????????????????????????               ????????????????????????
             ?
             ?  traces to
             ?
  ????????????????????????????????????
  ? ## Requirements Traceability     ?
  ?                                  ?
  ? | REQ-ERR-01 | Auth failure...   ?
  ? |            | UT-CE-01, UT-TE-01?
  ? |            | IT-AF-01          ?
  ????????????????????????????????????
```

### Workflow Examples

**"A customer reported a bug where blank passwords get through."**
1. Open `TEST_MATRIX.md` ? Requirements Traceability ? find `REQ-VAL-03`
2. Test IDs: `UT-VAL-04`, `IT-VB-01`
3. Run just those tests: search for `test_empty_password` and
   `test_empty_fields_block_then_succeed` in the test file
4. If they pass, the bug is elsewhere. If they fail, you found the regression.

**"I need to write a test plan for the profile feature."**
1. Open `TEST_GHERKIN.md` ? Feature: Profiles + Feature: Profile Workflow
2. Copy the 7 scenarios (UT-PR-01 through UT-PR-06 + IT-PW-01)
3. Paste into your test management tool as test cases
4. The Given/When/Then steps become your manual test steps

**"The CI pipeline shows UT-SSH-03 failing. What does it test?"**
1. Open `TEST_MATRIX.md` ? Section 2. SSH Manager ? row `UT-SSH-03`
2. Description: "Client with dead transport"
3. Verifies: "Returns False, auto-disconnects, clears client"
4. Method: `test_is_connected_dead_transport` — search the test file for this
5. Open `TEST_GHERKIN.md` ? Feature: SSH Manager ? `@UT-SSH-03` for the
   plain-English version of what should happen

---

## Part 4: Keeping Documents Up to Date

### When to update

| Event | Action |
|---|---|
| **New test added** | Add a row to `TEST_MATRIX.md` with the next ID in sequence. Add a Scenario to `TEST_GHERKIN.md` with matching tag. Update the total count in both headers. |
| **Test deleted** | Remove the row/scenario. Do NOT reuse the ID — retired IDs stay retired so old bug tickets still make sense. |
| **Test renamed** | Update the Test Method column. The ID stays the same. |
| **New requirement** | Add a row to the RTM. Assign the next `REQ-` number. Link existing test IDs or note "untested". |
| **Feature removed** | Mark the requirement as "Deprecated" rather than deleting, so audit trails remain. |

### Validation

After editing, run this quick check:

```powershell
# Count tests in code vs docs
python -m unittest test_SSH_DeviceManager.py -v 2>&1 | Select-String "^Ran"
# Should match the "Total Tests: 74" in both doc headers
```

---

## Glossary

| Term | Definition |
|---|---|
| **Unit Test** | Tests a single method or function in isolation. External dependencies (SSH, filesystem, GUI) are replaced with mocks. |
| **Integration Test** | Tests a multi-step workflow where several methods interact. Still uses mocks for external I/O, but exercises the real control flow between methods. |
| **Mock** | A fake object that replaces a real dependency (e.g., a fake SSH connection). Lets tests run without a real server. |
| **RTM** | Requirements Traceability Matrix — a table that maps every requirement to the tests that prove it works. |
| **Gherkin** | A plain-English format for writing test scenarios. Uses Given/When/Then keywords. |
| **BDD** | Behavior-Driven Development — a methodology where tests are written as behavioral specifications before code. |
| **Feature** | In Gherkin, a group of related scenarios describing one capability. Maps to a test class. |
| **Scenario** | In Gherkin, a single test case. Maps to one `test_*` method. |
| **Tag** | A label on a Gherkin scenario (e.g., `@unit`, `@UT-SSH-03`) used for filtering and cross-referencing. |
| **Forward Trace** | Following a requirement to the tests that cover it. Answers: "Is this requirement tested?" |
| **Reverse Trace** | Following a test back to the requirement it satisfies. Answers: "Why does this test exist?" |
| **Gap** | A requirement with no test IDs — represents untested behavior. |
| **Scenario Outline** | A parameterized Gherkin scenario that runs once per row in an Examples table. |
| **TclError** | A Tkinter-specific exception raised when a `tk.IntVar` is read while its GUI field is blank. |
| **Transport** | Paramiko's underlying SSH connection layer. `is_active()` checks if the TCP session is still alive. |
