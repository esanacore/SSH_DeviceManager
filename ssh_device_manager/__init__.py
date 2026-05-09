"""
SSH Device Manager - Modular Tkinter + Paramiko application.

Re-exports public API for backward compatibility with code that imports
from the package directly.
"""

from .models import ActionButton, ButtonSection, ToolTip
from .ssh_manager import SSHManager
from .themes import THEMES
from .app import SSHGuiApp
from .constants import COMMAND_HISTORY_LIMIT, APP_CONFIG_FILE, DEFAULT_SECTIONS_FILE
from .paramiko_compat import paramiko

__all__ = [
    "ActionButton",
    "ButtonSection",
    "ToolTip",
    "SSHManager",
    "THEMES",
    "SSHGuiApp",
    "COMMAND_HISTORY_LIMIT",
    "APP_CONFIG_FILE",
    "DEFAULT_SECTIONS_FILE",
    "paramiko",
]
