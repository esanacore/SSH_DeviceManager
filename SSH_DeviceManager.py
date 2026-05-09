"""
SSH Device Manager - Thin launcher / backward-compatibility shim.

The real implementation lives in the ``ssh_device_manager`` package.
This file re-exports every public name so that existing imports like
``import SSH_DeviceManager`` and ``SSH_DeviceManager.SSHGuiApp`` keep working.
"""

import os
import threading  # noqa: F401
import traceback
from tkinter import filedialog, messagebox  # noqa: F401

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

def main():
    """Run the SSH Device Manager GUI app."""
    app = SSHGuiApp()
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "ssh_device_manager_startup_error.log",
        )
        with open(log_path, "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        # Also print to stderr so terminal users still see it
        traceback.print_exc()
        raise SystemExit(1) from exc
