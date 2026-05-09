"""
SSH Device Manager - Thin launcher / backward-compatibility shim.

The real implementation lives in the ``ssh_device_manager`` package.
This file re-exports every public name so that existing imports like
``import SSH_DeviceManager`` and ``SSH_DeviceManager.SSHGuiApp`` keep working.
"""

# Re-export public API from the package
from ssh_device_manager import (           # noqa: F401
    ActionButton,
    ButtonSection,
    ToolTip,
    SSHManager,
    SSHGuiApp,
    THEMES,
    COMMAND_HISTORY_LIMIT,
    APP_CONFIG_FILE,
    DEFAULT_SECTIONS_FILE,
)
from ssh_device_manager.paramiko_compat import paramiko  # noqa: F401

# Re-export stdlib / third-party names that tests and external code reference
# through this module (e.g. ``SSH_DeviceManager.paramiko``).
import threading         # noqa: F401
from tkinter import filedialog, messagebox  # noqa: F401

def main():
    app = SSHGuiApp()
    app.mainloop()

if __name__ == "__main__":
    main()
