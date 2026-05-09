"""SSH Device Manager - Thin launcher / backward-compatibility shim.

This script serves as the main entry point for the SSH Device Manager. It
re-exports the public API from the `ssh_device_manager` package to maintain
backward compatibility with existing imports.
"""

import os
import threading  # noqa: F401  # Re-exported for backward compatibility
import traceback
from tkinter import filedialog, messagebox  # noqa: F401  # Re-exported names

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
    """Run the SSH Device Manager GUI app.

    Instantiates the main SSHGuiApp and enters the Tkinter main loop.
    """
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
