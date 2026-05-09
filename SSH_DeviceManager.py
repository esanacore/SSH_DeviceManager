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
    try:
        main()
    except Exception:
        import traceback, os
        log_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "ssh_device_manager_startup_error.log",
        )
        with open(log_path, "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        # Also print to stderr so terminal users still see it
        traceback.print_exc()
        raise SystemExit(1)
