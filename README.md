# SSH_DeviceManager

A Python-based GUI application for managing SSH connections and executing commands on remote devices. Built with Tkinter and Paramiko, it provides a modular interface for network device management, automation, and monitoring.

## Features

*   **SSH Connection Management**: Easily connect to remote hosts using IP/Hostname, Port, Username, and Password.
*   **Modular Action Buttons**: Pre-configured buttons organized into sections (Status, Maintenance, Custom) for common tasks.
*   **Terminal Output**: Real-time display of command output in a scrolling text widget.
*   **Command History**: Remembers recently executed commands for quick recall.
*   **File Upload**: Integrated SFTP support for uploading configuration files or templates.
*   **Custom Commands**: Execute arbitrary commands via a dialog or the custom action button.
*   **Output Management**: Options to clear, copy to clipboard, or save terminal output to a file.
*   **Threaded Operations**: Background processing ensures the UI remains responsive during network operations.
*   **Theming**: Choose from multiple themes (Default, Dark Mode, Solarized, Retro Terminal, Cyberpunk) to customize the look and feel.
*   **Help & Usage**: Built-in help dialog for quick reference.

## Requirements

*   Python 3.x
*   `tkinter` (usually included with Python)
*   `paramiko` library

## Installation

1.  Clone the repository or download the source code.
2.  Install the required dependencies:

    ```bash
    pip install paramiko
    ```

    *Note: On Linux, you might need to install `python3-tk` if it's not already present.*

## Usage

Run the application using Python:

```bash
python3 SSH_DeviceManager.py
```

1.  **Connect**: Enter the Host/IP, Port, Username, and Password in the top connection bar and click "Connect".
2.  **Execute Actions**: Click buttons in the "Actions" panel to run predefined commands (e.g., "Show Version", "Show Interfaces").
3.  **Custom Commands**: Use the "Run Custom Command..." button to enter specific commands.
4.  **Upload Files**: Use the "Upload Config" button to transfer files to the remote device, or "Send File via SCP" for specific destinations.
5.  **View Output**: Check the "Terminal Output" pane for results. You can save or copy this output using the buttons below the pane.
6.  **Themes**: Use the "Theme" menu to switch between different visual styles.
7.  **Help**: Access the "Help" menu for a quick overview of the application.

## Contributing

We welcome contributions! To keep the project organized, please follow these guidelines:

1.  **Changelog**: When you make significant changes (features, fixes, etc.), please update `CHANGELOG.md`.
    *   Add a bullet point under the `[Unreleased]` section.
    *   Categorize your change under `### Added`, `### Changed`, `### Fixed`, or `### Removed`.
2.  **Tests**: If you add new functionality, please add corresponding unit tests in `test_SSH_DeviceManager.py`.
3.  **Style**: Try to maintain the existing code style and structure.

## Unit Tests

This project includes a comprehensive unit test suite located in `test_SSH_DeviceManager.py`. The tests cover the core functionality of the application, including data models, SSH management, and the GUI application logic.

### Running the Tests

To run the unit tests, execute the following command in the project root directory:

```bash
python3 -m unittest test_SSH_DeviceManager.py
```

### Test Coverage

The test suite covers the following components:

1.  **Data Models**:
    *   `ActionButton`: Verifies initialization and attribute assignment.
    *   `ButtonSection`: Verifies initialization and attribute assignment.

2.  **SSHManager**:
    *   `is_connected`: Checks connection status reporting.
    *   `connect`: Verifies SSH connection establishment using mocked `paramiko.SSHClient`.
    *   `disconnect`: Verifies resource cleanup and exception handling during disconnection.
    *   `run_command`: Tests command execution, output retrieval, and error handling (e.g., not connected).
    *   `upload_file`: Verifies file upload functionality using mocked SFTP client.

3.  **SSHGuiApp**:
    *   **Initialization**: Verifies that the application initializes correctly with mocked Tkinter modules.
    *   **Connection Handling**: Tests `on_connect`, `on_disconnect`, and `test_connection` methods, ensuring proper threading and SSH manager interaction.
    *   **Command Execution**: Tests `run_ssh_command`, verifying command history updates and background thread execution.
    *   **File Upload**: Tests `upload_config_template`, mocking file dialogs and verifying upload calls.
    *   **Output Management**: Tests `copy_output` (clipboard interaction) and `save_output` (file writing).
    *   **Logging**: Verifies that log messages are correctly added to the thread-safe queue.

### Mocks

The tests use `unittest.mock` to mock external dependencies, ensuring that tests run quickly and without side effects:
*   `paramiko`: SSH and SFTP clients are mocked to simulate network operations.
*   `tkinter`: GUI components are mocked to allow testing application logic without a display server.
