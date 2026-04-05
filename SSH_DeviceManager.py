"""
Tkinter + SSH (Paramiko) UI Template

Goals:
- User enters Host/IP, Port, Username, Password
- App connects/disconnects via SSH
- Button "sections" with vertical separators
- Buttons are modular and easy to enable/disable
- Each button can run a command or upload a file (template stubs included)
- Terminal output is displayed in a scrolling text widget

Notes:
- This is a template: swap in your own commands later.
- For "network devices", you may need to tweak prompt handling, paging, etc.
- Paramiko is a third-party library; install via `pip install paramiko`
- This code is modular and can be extended with more features as needed.
- Designed for clarity and ease of modification.

SECURITY NOTES:
- AutoAddPolicy accepts all host keys without verification. For production,
  load known_hosts or use WarningPolicy. See SSHManager.connect() comments.
- Credentials are held in memory. Consider clearing them after disconnect.
- Default credentials are blank; enter your own values.
"""

import json
import os
import queue
import threading
import time
import tkinter as tk

from contextlib import suppress
from dataclasses import dataclass
from tkinter import filedialog, messagebox, ttk
from typing import Callable, List, Optional

# Third-party dependency
import paramiko

# Paramiko allows SSH connections and SFTP file transfers.

# Config: command history limit
COMMAND_HISTORY_LIMIT = 500
APP_CONFIG_FILE = "ssh_device_manager_config.json"
DEFAULT_SECTIONS_FILE = "sections.json"


# -----------------------------
# Data models for modular UI
# -----------------------------


@dataclass
class ActionButton:
    """
    Represents one button/action in the UI.
    - label: text on the button
    - enabled: whether it should appear / be clickable
    - handler: function called when clicked
    - tooltip: optional help text (simple hover tooltip added below)
    """

    label: str
    enabled: bool
    handler: Callable[[], None]
    tooltip: str = ""


@dataclass
class ButtonSection:
    """
    Represents a 'section' (a vertical group) of buttons.
    - title: shown at top of section
    - max_buttons: hard limit to keep layout consistent
    - actions: list of ActionButton items
    """

    title: str
    max_buttons: int
    actions: List[ActionButton]


# -----------------------------
# Simple tooltip helper
# -----------------------------


class ToolTip:
    """Minimal tooltip implementation for Tkinter widgets."""

    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tipwindow = None

        if text:
            widget.bind("<Enter>", self.show_tip)
            widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, _event=None):
        if self.tipwindow or not self.text:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10

        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
        )
        label.pack(ipadx=6, ipady=4)

    def hide_tip(self, _event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


# -----------------------------
# SSH Manager (Paramiko)
# -----------------------------


class SSHManager:
    """
    Wraps Paramiko SSHClient with:
    - connect / disconnect
    - run_command
    - upload_file (SFTP)
    """

    def __init__(self):
        self.client: Optional[paramiko.SSHClient] = None
        self.sftp: Optional[paramiko.SFTPClient] = None
        self.host_key: Optional[str] = None

    def is_connected(self) -> bool:
        if not self.client:
            return False

        transport = self.client.get_transport()
        is_active = bool(transport and transport.is_active())
        if not is_active:
            self.disconnect()
        return is_active

    def connect(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        timeout: int = 10,
        host_key_mode: str = "warning",
    ):
        """
        Connect via SSH.

        SECURITY NOTE:
        - RejectPolicy requires the host key to already exist in known_hosts.
        - WarningPolicy warns and then trusts the presented host key.
        - AutoAddPolicy trusts all host keys silently.
        - This template defaults to WarningPolicy so first-use trust is visible.
        """

        if self.client:
            self.disconnect()

        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()

        policies = {
            "strict": paramiko.RejectPolicy,
            "warning": paramiko.WarningPolicy,
            "auto": paramiko.AutoAddPolicy,
        }
        policy_cls = policies.get(host_key_mode, paramiko.WarningPolicy)
        ssh.set_missing_host_key_policy(policy_cls())
        ssh.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=timeout,
            allow_agent=False,
            look_for_keys=False,
        )

        self.client = ssh
        self.host_key = host
        # SFTP is optional; only created when needed, but you can also open it here.
        self.sftp = None

    def disconnect(self):
        """Close SSH and SFTP connections, clear sensitive data."""
        with suppress(OSError, paramiko.SSHException):
            if self.sftp:
                self.sftp.close()

        with suppress(OSError, paramiko.SSHException):
            if self.client:
                self.client.close()

        self.client = None
        self.sftp = None
        self.host_key = None

    def run_command(self, command: str, timeout: int = 30) -> str:
        if not self.client:
            raise RuntimeError("Not connected")

        # exec_command is simplest for one-off commands.
        # Many network devices behave best with an interactive shell (invoke_shell).
        # Keep this template simple; can be extended later.
        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        combined = out + (("\n" + err) if err.strip() else "")
        return combined

    def upload_file(self, local_path: str, remote_path: str):
        if not self.client:
            raise RuntimeError("Not connected")

        if not self.sftp:
            self.sftp = self.client.open_sftp()

        self.sftp.put(local_path, remote_path)


# -----------------------------
# Main App
# -----------------------------


class SSHGuiApp(tk.Tk):
    """
    Tkinter App Template:
    - Top: connection fields + connect/disconnect + settings
    - Middle: button sections (with vertical separators)
    - Bottom: terminal output pane
    """

    THEMES = {
        "Default": {
            "bg": "#f0f0f0",
            "fg": "black",
            "text_bg": "white",
            "text_fg": "black",
            "entry_bg": "white",
            "entry_fg": "black",
            "select_bg": "#0078d7",
            "select_fg": "white",
            "btn_bg": "#f0f0f0",
            "border": "#999999",
            "label_fg": "black",
        },
        "Solarized Dark": {
            "bg": "#002b36",            # base03 - main window background
            "fg": "#839496",            # base0  - default body text
            "text_bg": "#002b36",       # base03 - terminal/editor background
            "text_fg": "#839496",       # base0  - terminal/editor text
            "entry_bg": "#073642",      # base02 - input fields (raised surface)
            "entry_fg": "#93a1a1",      # base1  - input text (slightly brighter)
            "select_bg": "#268bd2",     # blue   - selection highlight
            "select_fg": "#fdf6e3",     # base3  - selected text
            "btn_bg": "#073642",        # base02 - button background
            "border": "#586e75",        # base01 - borders and separators
            "label_fg": "#93a1a1",      # base1  - section titles / labels
        },
        "Solarized Light": {
            "bg": "#fdf6e3",
            "fg": "#657b83",
            "text_bg": "#eee8d5",
            "text_fg": "#586e75",
            "entry_bg": "#eee8d5",
            "entry_fg": "#586e75",
            "select_bg": "#268bd2",
            "select_fg": "#fdf6e3",
            "btn_bg": "#eee8d5",
            "border": "#93a1a1",
            "label_fg": "#586e75",
        },
        "Dark Mode": {
            "bg": "#1e1e1e",
            "fg": "#d4d4d4",
            "text_bg": "#1e1e1e",
            "text_fg": "#d4d4d4",
            "entry_bg": "#3c3c3c",
            "entry_fg": "#d4d4d4",
            "select_bg": "#094771",
            "select_fg": "white",
            "btn_bg": "#333333",
            "border": "#555555",
            "label_fg": "#d4d4d4",
        },
        "Retro Terminal": {
            "bg": "#000000",
            "fg": "#00ff00",
            "text_bg": "#000000",
            "text_fg": "#00ff00",
            "entry_bg": "#000000",
            "entry_fg": "#00ff00",
            "select_bg": "#00ff00",
            "select_fg": "#000000",
            "btn_bg": "#000000",
            "border": "#00ff00",
            "label_fg": "#00ff00",
        },
        "Cyberpunk": {
            "bg": "#0b0c15",        # Very dark blue/black
            "fg": "#00f3ff",        # Electric Blue
            "text_bg": "#120424",   # Deep purple/black
            "text_fg": "#ff00ff",   # Bright Pink
            "entry_bg": "#120424",
            "entry_fg": "#fcee0a",  # Bright Yellow
            "select_bg": "#ff00ff",
            "select_fg": "#0b0c15",
            "btn_bg": "#1a0a30",
            "border": "#ff00ff",
            "label_fg": "#00f3ff",
        },
    }

    def __init__(self, init_ui: bool = True):
        super().__init__()
        self.app_config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            APP_CONFIG_FILE,
        )
        self.app_config = self._load_app_config()

        # Allow headless/test initialization: when init_ui is False, skip building UI
        # but still initialize core state so unit tests can exercise logic.
        # This flag is False only in test environments (tests pass init_ui=False).
        if not init_ui:
            # Thread-safe queue for log messages (background threads -> UI)
            self.log_queue: "queue.Queue[str]" = queue.Queue()

            # Connection state and history
            self.ssh = SSHManager()
            self.command_history: List[str] = []
            self.history_index: int = 0
            self.is_connecting = False
            self.host_history: List[str] = []

            # Theme state (minimal)
            self.current_theme = tk.StringVar(value="Default")

            # Minimal UI variables used by tests (MagicMocks or simple widgets)
            try:
                from unittest.mock import MagicMock
            except Exception:
                MagicMock = lambda *a, **k: None

            self.host_var = MagicMock()
            self.user_var = MagicMock()
            self.port_var = MagicMock()
            self.pass_var = MagicMock()
            self.timeout_var = MagicMock()
            self.clear_creds_var = MagicMock()
            self.host_key_mode_var = MagicMock()
            self.host_key_mode_var.get.return_value = "warning"
            self.profile_name_var = MagicMock()
            self.profile_name_var.get.return_value = ""
            self.profile_select_var = MagicMock()
            self.profile_select_var.get.return_value = ""

            # Host combobox placeholder (supports item assignment)
            class _ComboPlaceholder:
                def __init__(self):
                    self._items = {}
                def __setitem__(self, k, v):
                    self._items[k] = v
                def __getitem__(self, k):
                    return self._items.get(k)
            self.host_combo = _ComboPlaceholder()
            self.profile_combo = _ComboPlaceholder()

            # Connect/disconnect buttons placeholders
            class _BtnPlaceholder:
                def configure(self, *a, **k):
                    pass
            self.connect_btn = _BtnPlaceholder()
            self.disconnect_btn = _BtnPlaceholder()

            # Output text placeholder
            self.output_text = MagicMock()

            # Load sections from JSON (fallback to built-in)
            self.sections_path = DEFAULT_SECTIONS_FILE
            self.sections = self.load_sections_from_file(self.sections_path)

            return

        self.title("SSH Command Console (Template)")
        self.geometry("1400x900")
        self.minsize(1000, 700)

        # Attempt to maximize window
        try:
            if self.tk.call("tk", "windowingsystem") == "x11":
                self.attributes("-zoomed", True)
            elif self.tk.call("tk", "windowingsystem") == "win32":
                self.state("zoomed")
        except (tk.TclError, Exception):
            pass

        # Thread-safe queue for log messages (background threads -> UI)
        self.log_queue: "queue.Queue[str]" = queue.Queue()

        # Connection state and history
        self.ssh = SSHManager()
        self.command_history: List[str] = []
        self.history_index: int = 0
        self.is_connecting = False
        self.host_history: List[str] = []

        # Theme state
        self.current_theme = tk.StringVar(value="Default")

        self._build_menu()
        self._build_ui()
        self._start_log_poller()
        self._start_connection_monitor()

        # Load sections from JSON (fallback to built-in)
        self.sections_path = DEFAULT_SECTIONS_FILE
        self.sections = self.load_sections_from_file(self.sections_path)
        self._build_button_sections(self.sections)
        self._refresh_profile_list()

        # Start watcher to auto-reload sections.json on changes
        self._sections_mtime = self._get_mtime(self.sections_path)
        self._start_sections_watcher()

        # Apply default theme
        self.apply_theme("Default")

    # -------------------------
    # UI Construction
    # -------------------------

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About / Usage", command=self.show_help_dialog)

        # Theme Menu
        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="     Theme", menu=theme_menu)

        for theme_name in sorted(self.THEMES.keys()):
            theme_menu.add_radiobutton(
                label=theme_name,
                variable=self.current_theme,
                value=theme_name,
                command=lambda t=theme_name: self.apply_theme(t),
            )

        # Config Menu: reload sections
        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Config", menu=config_menu)
        config_menu.add_command(
            label="Reload Sections",
            command=lambda: self.reload_sections(DEFAULT_SECTIONS_FILE),
        )
        config_menu.add_command(
            label="Open Sections File...",
            command=lambda: self.open_sections_file(DEFAULT_SECTIONS_FILE),
        )

    def _build_ui(self):
        # Main layout: connection frame, settings frame, command frame, output frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        self.connection_frame = ttk.LabelFrame(self, text="SSH Connection")
        self.connection_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        self.connection_frame.columnconfigure(10, weight=1)

        self.commands_frame = ttk.LabelFrame(self, text="Actions")
        self.commands_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=8)

        self.settings_frame = ttk.LabelFrame(self, text="Settings")
        self.settings_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 8))

        self.output_frame = ttk.LabelFrame(self, text="Terminal Output")
        self.output_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.output_frame.rowconfigure(0, weight=1)
        self.output_frame.columnconfigure(0, weight=1)

        # ----- Connection inputs -----
        ttk.Label(self.connection_frame, text="Host / IP:").grid(
            row=0, column=0, padx=6, pady=6, sticky="w"
        )
        self.host_var = tk.StringVar(value="")
        self.host_combo = ttk.Combobox(
            self.connection_frame,
            textvariable=self.host_var,
            width=20,
        )
        self.host_combo.grid(row=0, column=1, padx=6, pady=6)
        self.host_combo.bind("<<ComboboxSelected>>", self.on_host_selected)

        ttk.Label(self.connection_frame, text="Port:").grid(
            row=0, column=2, padx=6, pady=6, sticky="w"
        )
        self.port_var = tk.IntVar(value=22)
        ttk.Entry(
            self.connection_frame,
            textvariable=self.port_var,
            width=6,
        ).grid(row=0, column=3, padx=6, pady=6)

        ttk.Label(self.connection_frame, text="Username:").grid(
            row=0, column=4, padx=6, pady=6, sticky="w"
        )
        self.user_var = tk.StringVar(value="")
        ttk.Entry(
            self.connection_frame,
            textvariable=self.user_var,
            width=16,
        ).grid(row=0, column=5, padx=6, pady=6)

        ttk.Label(self.connection_frame, text="Password:").grid(
            row=0, column=6, padx=6, pady=6, sticky="w"
        )
        self.pass_var = tk.StringVar()
        ttk.Entry(
            self.connection_frame,
            textvariable=self.pass_var,
            width=16,
            show="*",
        ).grid(row=0, column=7, padx=6, pady=6)

        self.connect_btn = ttk.Button(
            self.connection_frame,
            text="Connect",
            command=self.on_connect,
        )
        self.connect_btn.grid(row=0, column=8, padx=6, pady=6)

        self.disconnect_btn = ttk.Button(
            self.connection_frame,
            text="Disconnect",
            command=self.on_disconnect,
            state="disabled",
        )
        self.disconnect_btn.grid(row=0, column=9, padx=6, pady=6)

        self.status_var = tk.StringVar(value="Disconnected")
        ttk.Label(
            self.connection_frame,
            textvariable=self.status_var,
        ).grid(row=0, column=10, padx=10, pady=6, sticky="e")

        ttk.Label(self.connection_frame, text="Profile Name:").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.profile_name_var = tk.StringVar()
        ttk.Entry(self.connection_frame, textvariable=self.profile_name_var, width=20).grid(row=1, column=1, padx=6, pady=6)

        ttk.Label(self.connection_frame, text="Saved Profiles:").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        self.profile_select_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(
            self.connection_frame,
            textvariable=self.profile_select_var,
            state="readonly",
            width=18,
        )
        self.profile_combo.grid(row=1, column=3, padx=6, pady=6, sticky="w")
        self.profile_combo.bind("<<ComboboxSelected>>", lambda _event: self.load_selected_profile())

        ttk.Button(self.connection_frame, text="Save Profile", command=self.save_profile).grid(row=1, column=4, padx=6, pady=6)
        ttk.Button(self.connection_frame, text="Load Profile", command=self.load_selected_profile).grid(row=1, column=5, padx=6, pady=6)
        ttk.Button(self.connection_frame, text="Delete Profile", command=self.delete_selected_profile).grid(row=1, column=6, padx=6, pady=6)

        # ----- Settings -----
        ttk.Label(self.settings_frame, text="Connection Timeout (s):").grid(
            row=0, column=0, padx=6, pady=6, sticky="w"
        )
        self.timeout_var = tk.IntVar(value=10)
        ttk.Spinbox(
            self.settings_frame,
            from_=5,
            to=60,
            textvariable=self.timeout_var,
            width=6,
        ).grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(self.settings_frame, text="Host Key Policy:").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.host_key_mode_var = tk.StringVar(value="warning")
        self.host_key_mode_combo = ttk.Combobox(
            self.settings_frame,
            textvariable=self.host_key_mode_var,
            state="readonly",
            width=18,
            values=("strict", "warning", "auto"),
        )
        self.host_key_mode_combo.grid(row=0, column=3, padx=6, pady=6, sticky="w")

        self.clear_creds_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.settings_frame, text="Clear credentials on disconnect", variable=self.clear_creds_var).grid(row=0, column=4, padx=6, pady=6, sticky="w")

        ttk.Button(self.settings_frame, text="Test Connection", command=self.test_connection).grid(row=0, column=5, padx=6, pady=6, sticky="w")

        # ----- Output pane -----
        self.output_text = tk.Text(
            self.output_frame,
            wrap="word",
            height=12,
            font=("Courier New", 9),
        )
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)

        scroll = ttk.Scrollbar(self.output_frame, command=self.output_text.yview)
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)
        self.output_text.configure(yscrollcommand=scroll.set)

        # Make output read-only by default
        self.output_text.configure(state="disabled")

        # Optional: clear/copy controls
        controls = ttk.Frame(self.output_frame)
        controls.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))
        controls.columnconfigure(0, weight=1)

        ttk.Button(
            controls,
            text="Clear Output",
            command=self.clear_output,
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            controls,
            text="Copy Output",
            command=self.copy_output,
        ).grid(row=0, column=1, sticky="w", padx=(8, 0))

        ttk.Button(
            controls,
            text="Save Output",
            command=self.save_output,
        ).grid(row=0, column=2, sticky="w", padx=(8, 0))

    # -------------------------
    # Theme Management
    # -------------------------

    def apply_theme(self, theme_name: str):
        theme = self.THEMES.get(theme_name, self.THEMES["Default"])

        # Resolve optional keys with sensible fallbacks
        btn_bg = theme.get("btn_bg", theme["bg"])
        border = theme.get("border", theme["fg"])
        label_fg = theme.get("label_fg", theme["fg"])

        # Configure main window background
        self.configure(bg=theme["bg"])

        # Configure styles for ttk widgets
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            ".",
            background=theme["bg"],
            foreground=theme["fg"],
            fieldbackground=theme["entry_bg"],
            bordercolor=border,
        )
        style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
        style.configure(
            "TButton",
            background=btn_bg,
            foreground=theme["fg"],
            bordercolor=border,
        )
        style.configure(
            "TEntry",
            fieldbackground=theme["entry_bg"],
            foreground=theme["entry_fg"],
            bordercolor=border,
            insertcolor=theme["entry_fg"],
        )
        style.configure(
            "TCombobox",
            fieldbackground=theme["entry_bg"],
            foreground=theme["entry_fg"],
            arrowcolor=theme["fg"],
            bordercolor=border,
        )
        style.configure(
            "TLabelframe",
            background=theme["bg"],
            foreground=label_fg,
            bordercolor=border,
        )
        style.configure(
            "TLabelframe.Label",
            background=theme["bg"],
            foreground=label_fg,
        )
        style.configure(
            "TCheckbutton",
            background=theme["bg"],
            foreground=theme["fg"],
            indicatorcolor=theme["entry_bg"],
        )
        style.configure(
            "TSpinbox",
            fieldbackground=theme["entry_bg"],
            foreground=theme["entry_fg"],
            arrowcolor=theme["fg"],
            bordercolor=border,
        )
        style.configure(
            "TSeparator",
            background=border,
        )

        # Map dynamic states (e.g. hover, active)
        style.map(
            "TButton",
            background=[("active", theme["select_bg"]), ("pressed", theme["select_bg"])],
            foreground=[("active", theme["select_fg"]), ("pressed", theme["select_fg"])],
        )
        style.map(
            "TEntry",
            fieldbackground=[("readonly", theme["bg"])],
            foreground=[("readonly", theme["fg"])],
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", theme["entry_bg"])],
            foreground=[("readonly", theme["entry_fg"])],
            selectbackground=[("readonly", theme["select_bg"])],
            selectforeground=[("readonly", theme["select_fg"])],
        )
        style.map(
            "TCheckbutton",
            background=[("active", theme["bg"])],
            indicatorcolor=[("selected", theme["select_bg"])],
        )

        # Configure standard Tk widgets (Text, etc.)
        self.output_text.configure(
            bg=theme["text_bg"],
            fg=theme["text_fg"],
            insertbackground=theme["fg"],
            selectbackground=theme["select_bg"],
            selectforeground=theme["select_fg"],
        )

        # Update any existing Toplevels or specific widgets if needed
        # (For this template, most are covered by ttk styles or rebuilt on demand)

    # -------------------------
    # Sections loader + integration
    # -------------------------

    def load_sections_from_file(self, path: str) -> List[ButtonSection]:
        """
        Loads section/button definitions from a JSON file.

        Format:
        {
          "sections": [
            {
              "title": "Status",
              "max_buttons": 6,
              "actions": [
                { "label": "Show Version", "enabled": true, "command": "show version", "tooltip": "..." }
              ]
            }
          ]
        }

        Returns built-in definitions on error.
        """

        def resolve_handler(cmd: str) -> Callable[[], None]:
            if not cmd:
                return lambda: self.log("[WARN] No command assigned to this button.")

            # special tokens
            if cmd == "__upload_template__":
                return self.upload_config_template
            if cmd == "__send_file__":
                return self.send_file_scp
            if cmd == "__custom_command__":
                return self.prompt_and_run_custom_command

            # allow "run:actual command" syntax
            if cmd.startswith("run:"):
                command_text = cmd.split(":", 1)[1]
                return lambda c=command_text: self.run_ssh_command(c)

            # default: treat as SSH command string
            return lambda c=cmd: self.run_ssh_command(c)

        try:
            if not os.path.exists(path):
                self.log(
                    f"[INFO] Sections file '{path}' not found. Using built-in sections."
                )
                return self._define_sections()

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            sections: List[ButtonSection] = []

            for s in data.get("sections", []):
                title = str(s.get("title", "")) or "Untitled"
                maxb = int(s.get("max_buttons", 6))
                actions_list = []

                for a in s.get("actions", []):
                    label = str(a.get("label", "Button"))
                    enabled = bool(a.get("enabled", True))
                    cmd = a.get("command", "") or ""
                    tooltip = str(a.get("tooltip", ""))
                    handler = resolve_handler(cmd)

                    actions_list.append(
                        ActionButton(
                            label=label,
                            enabled=enabled,
                            handler=handler,
                            tooltip=tooltip,
                        )
                    )

                sections.append(
                    ButtonSection(
                        title=title,
                        max_buttons=maxb,
                        actions=actions_list,
                    )
                )

            if not sections:
                self.log(
                    "[WARN] Sections file parsed but contained no sections. Using built-in sections."
                )
                return self._define_sections()

            self.log(f"[OK] Loaded sections from '{path}'.")
            return sections

        except Exception as e:
            self.log(f"[ERROR] Failed to load sections from '{path}': {e}")
            return self._define_sections()

    def reload_sections(self, path: str = DEFAULT_SECTIONS_FILE):
        # remember which file we're watching
        self.sections_path = path
        self.log(f"Reloading sections from '{path}'...")
        self.sections = self.load_sections_from_file(path)

        # rebuild UI on main thread
        self._build_button_sections(self.sections)

        # update stored mtime after successful reload
        self._sections_mtime = self._get_mtime(self.sections_path)
        self.log("[OK] Sections reloaded.")

    def open_sections_file(self, default_path: str = DEFAULT_SECTIONS_FILE):
        p = filedialog.askopenfilename(
            initialfile=default_path,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if p:
            self.reload_sections(p)

    # -------------------------
    # Auto-reload watcher
    # -------------------------

    def _get_mtime(self, path: str):
        try:
            return os.path.getmtime(path)
        except Exception:
            return None

    def _start_sections_watcher(self, interval_ms: int = 1000):
        """Periodically checks the mtime of the sections file and reloads on change."""

        def check():
            try:
                current = self._get_mtime(self.sections_path)
                if current != getattr(self, "_sections_mtime", None):
                    # Only reload if the file exists or was changed
                    self.log(
                        f"[INFO] Detected change in sections file '{self.sections_path}', reloading..."
                    )
                    self.reload_sections(self.sections_path)
                # schedule next check
            except Exception as e:
                # don't let watcher crash
                self.log(f"[WARN] sections watcher error: {e}")
            finally:
                self.after(interval_ms, check)

        # start the periodic check
        self.after(interval_ms, check)

    # -------------------------
    # Define Sections / Buttons (fallback)
    # -------------------------

    def _default_app_config(self) -> dict:
        return {"profiles": {}}

    def _load_app_config(self) -> dict:
        if not os.path.exists(self.app_config_path):
            config = self._default_app_config()
            self.app_config = config
            self._save_app_config()
            return config

        try:
            with open(self.app_config_path, "r", encoding="utf-8") as handle:
                loaded = json.load(handle)
        except (OSError, json.JSONDecodeError):
            config = self._default_app_config()
            self.app_config = config
            self._save_app_config()
            return config

        config = self._default_app_config()
        if isinstance(loaded, dict):
            profiles = loaded.get("profiles")
            if isinstance(profiles, dict):
                config["profiles"] = profiles
        return config

    def _save_app_config(self):
        with open(self.app_config_path, "w", encoding="utf-8") as handle:
            json.dump(self.app_config, handle, indent=2)

    def _define_sections(self) -> List[ButtonSection]:
        """
        Define your sections here.

        Rules:
        - max_buttons is a clear LIMIT per section.
        - each ActionButton has enabled=True/False
        - handler points to a function that executes a command or upload.
        """

        # Example "command strings" you can replace later:
        show_version = "show version"
        show_interfaces = "show interfaces"
        reboot = "reload"

        return [
            ButtonSection(
                title="Status",
                max_buttons=6,
                actions=[
                    ActionButton(
                        "Show Version",
                        enabled=True,
                        handler=lambda: self.run_ssh_command(show_version),
                        tooltip="Runs: show version",
                    ),
                    ActionButton(
                        "Show Interfaces",
                        enabled=True,
                        handler=lambda: self.run_ssh_command(show_interfaces),
                        tooltip="Runs: show interfaces",
                    ),
                    ActionButton(
                        "Placeholder A",
                        enabled=False,
                        handler=lambda: self.run_ssh_command("echo Placeholder A"),
                        tooltip="Disabled until you set enabled=True",
                    ),
                ],
            ),
            ButtonSection(
                title="Maintenance",
                max_buttons=6,
                actions=[
                    ActionButton(
                        "Upload Config (Template)",
                        enabled=True,
                        handler=self.upload_config_template,
                        tooltip="Opens a file picker and uploads to a remote path",
                    ),
                    ActionButton(
                        "Send File via SCP",
                        enabled=True,
                        handler=self.send_file_scp,
                        tooltip="Send a file to the remote server via SCP",
                    ),
                    ActionButton(
                        "Reboot Device",
                        enabled=False,
                        handler=lambda: self.run_ssh_command(reboot),
                        tooltip="Dangerous: enable only when ready",
                    ),
                ],
            ),
            ButtonSection(
                title="Custom",
                max_buttons=6,
                actions=[
                    ActionButton(
                        "Run Custom Command...",
                        enabled=True,
                        handler=self.prompt_and_run_custom_command,
                        tooltip="Prompts you for a command string",
                    ),
                ],
            ),
        ]

    def _build_button_sections(self, sections: List[ButtonSection]):
        """
        Builds the 'Actions' area:
        - Each section is a Frame with a title + up to max_buttons buttons
        - Sections are separated by a vertical separator
        """

        # Clear any previous content if rebuilt
        for child in self.commands_frame.winfo_children():
            child.destroy()

        container = ttk.Frame(self.commands_frame)
        container.pack(fill="x", padx=8, pady=8)

        # Configure grid columns to be equal width
        total_columns = len(sections) * 2 - 1  # Sections + Separators
        for i in range(total_columns):
            if i % 2 == 0:  # Section columns
                container.columnconfigure(i, weight=1, uniform="section")
            else:  # Separator columns
                container.columnconfigure(i, weight=0)

        for i, section in enumerate(sections):
            # Section frame
            sec_frame = ttk.Frame(container, padding=(6, 2))
            sec_frame.grid(row=0, column=i * 2, sticky="nsew")

            # Section title
            ttk.Label(
                sec_frame,
                text=section.title,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w", pady=(0, 6))

            # Enforce max buttons visually and logically
            enabled_actions = [a for a in section.actions if a.enabled]
            if len(enabled_actions) > section.max_buttons:
                # Template behavior: warn once in output and truncate
                self.log(
                    f"[WARN] Section '{section.title}' exceeds max_buttons={section.max_buttons}. Truncating."
                )
                enabled_actions = enabled_actions[: section.max_buttons]

            # Create the buttons
            for action in enabled_actions:
                btn = ttk.Button(
                    sec_frame,
                    text=action.label,
                    command=action.handler,
                    width=24,
                )
                btn.pack(fill="x", pady=3)

                # Tooltip (optional)
                ToolTip(btn, action.tooltip)

            # Add a vertical separator between sections (except after last)
            if i < len(sections) - 1:
                sep = ttk.Separator(container, orient="vertical")
                sep.grid(row=0, column=i * 2 + 1, sticky="ns", padx=10)

                # Make separator stretch with height by giving container row weight
                container.grid_rowconfigure(0, weight=1)

    # -------------------------
    # Connection handlers
    # -------------------------
    def on_host_selected(self, _event):
        if self.host_var.get() == "<Clear History>":
            self.host_history.clear()
            self.host_combo["values"] = []
            self.host_var.set("")
            self.log("[INFO] Host history cleared.")
    def _refresh_profile_list(self):
        profile_names = sorted(self.app_config.get("profiles", {}).keys())
        self.profile_combo["values"] = profile_names

        current = self.profile_select_var.get().strip()
        if current in profile_names:
            return
        if profile_names:
            self.profile_select_var.set(profile_names[0])
        else:
            self.profile_select_var.set("")

    def save_profile(self):
        profile_name = self.profile_name_var.get().strip() or self.profile_select_var.get().strip()
        if not profile_name:
            messagebox.showwarning("Missing Profile Name", "Enter a profile name before saving.")
            return

        inputs = self._get_connection_inputs()
        if inputs is None:
            return
        host, port, user, _pw, timeout = inputs

        self.app_config.setdefault("profiles", {})[profile_name] = {
            "host": host,
            "port": port,
            "username": user,
            "timeout": timeout,
            "host_key_mode": self._get_host_key_mode(),
        }
        self._save_app_config()
        self._refresh_profile_list()
        self.profile_select_var.set(profile_name)
        self.profile_name_var.set(profile_name)
        self.log(f"[OK] Saved profile '{profile_name}'.")

    def load_selected_profile(self):
        profile_name = self.profile_select_var.get().strip()
        if not profile_name:
            messagebox.showwarning("No Profile Selected", "Choose a saved profile to load.")
            return

        profile = self.app_config.get("profiles", {}).get(profile_name)
        if not isinstance(profile, dict):
            messagebox.showerror("Missing Profile", f"Profile '{profile_name}' was not found.")
            self._refresh_profile_list()
            return

        host = str(profile.get("host", ""))
        self.profile_name_var.set(profile_name)
        self.host_var.set(host)
        self.port_var.set(int(profile.get("port", 22)))
        self.user_var.set(str(profile.get("username", "")))
        self.timeout_var.set(int(profile.get("timeout", 10)))
        self.host_key_mode_var.set(str(profile.get("host_key_mode", "warning")))
        if host and host not in self.host_history:
            self.host_history.insert(0, host)
            self.host_combo["values"] = self.host_history + ["<Clear History>"]
        self.log(f"[OK] Loaded profile '{profile_name}'.")

    def delete_selected_profile(self):
        profile_name = self.profile_select_var.get().strip()
        if not profile_name:
            messagebox.showwarning("No Profile Selected", "Choose a saved profile to delete.")
            return

        confirmed = messagebox.askyesno("Delete Profile", f"Delete profile '{profile_name}'?")
        if not confirmed:
            return

        profiles = self.app_config.get("profiles", {})
        if profile_name in profiles:
            del profiles[profile_name]
            self._save_app_config()
            self._refresh_profile_list()
            if self.profile_name_var.get().strip() == profile_name:
                self.profile_name_var.set("")
            self.log(f"[OK] Deleted profile '{profile_name}'.")

    def _parse_int_input(self, value: str, label: str, minimum: int = 1, maximum: Optional[int] = None) -> Optional[int]:
        """Parse and validate integer form input, showing a user-facing error on failure."""
        text = value.strip()
        try:
            parsed = int(text)
        except (TypeError, ValueError):
            messagebox.showerror("Invalid Input", f"{label} must be a whole number.")
            return None

        if parsed < minimum or (maximum is not None and parsed > maximum):
            if maximum is None:
                range_text = f"{minimum}+"
            else:
                range_text = f"{minimum}-{maximum}"
            messagebox.showerror("Invalid Input", f"{label} must be in the range {range_text}.")
            return None

        return parsed

    def _get_connection_inputs(self) -> Optional[tuple[str, int, str, str, int]]:
        """Validate the current connection form and return normalized values.

        Each missing or invalid field is reported individually so the user
        knows exactly what to fix.  Returns ``None`` when validation fails.
        """
        errors: List[str] = []

        host = self.host_var.get().strip()
        user = self.user_var.get().strip()
        pw = self.pass_var.get()

        if not host:
            errors.append("Host / IP is empty.")
        if not user:
            errors.append("Username is empty.")
        if not pw:
            errors.append("Password is empty.")

        # --- Port ---
        port: Optional[int] = None
        try:
            port = int(self.port_var.get())
        except (TypeError, ValueError, tk.TclError):
            errors.append("Port is empty or not a valid number.")

        if port is not None and (port < 1 or port > 65535):
            errors.append("Port must be between 1 and 65535.")
            port = None

        # --- Timeout ---
        timeout: Optional[int] = None
        try:
            timeout = int(self.timeout_var.get())
        except (TypeError, ValueError, tk.TclError):
            errors.append("Connection Timeout is empty or not a valid number.")

        if timeout is not None and (timeout < 1 or timeout > 300):
            errors.append("Connection Timeout must be between 1 and 300.")
            timeout = None

        if errors:
            summary = "\n".join(f"  \u2022 {e}" for e in errors)
            self.log(f"[ERROR] Connection form has problems:\n{summary}")
            messagebox.showerror(
                "Invalid Connection Details",
                "Please fix the following:\n\n" + "\n".join(f"\u2022 {e}" for e in errors),
            )
            return None

        return host, port, user, pw, timeout

    def _get_host_key_mode(self) -> str:
        mode = self.host_key_mode_var.get().strip().lower()
        if mode not in {"strict", "warning", "auto"}:
            return "warning"
        return mode

    def _refresh_connection_state(self, *, notify_on_drop: bool = False):
        """Sync UI state with the actual SSH transport state."""
        connected = self.ssh.is_connected()
        was_connecting = self.is_connecting
        self._set_connected_ui(connected)

        if notify_on_drop and not connected and not was_connecting:
            self.log("[WARN] SSH session is no longer active.")

    def _start_connection_monitor(self):
        """Periodically detect dropped SSH sessions and refresh the UI."""
        def poll():
            was_connected = self.status_var.get() == "Connected"
            self._refresh_connection_state(notify_on_drop=was_connected)
            self.after(1500, poll)

        self.after(1500, poll)

    def on_connect(self):
        inputs = self._get_connection_inputs()
        if inputs is None:
            return
        host, port, user, pw, timeout = inputs

        if self.is_connecting:
            messagebox.showwarning(
                "In Progress",
                "Connection attempt already in progress.",
            )
            return

        if host not in self.host_history:
            self.host_history.insert(0, host)
            if len(self.host_history) > 10:
                self.host_history.pop()
            self.host_combo["values"] = self.host_history + ["<Clear History>"]

        host_key_mode = self._get_host_key_mode()
        self.log(f"Connecting to {host}:{port} as {user}...")
        self.is_connecting = True

        def worker():
            try:
                self.ssh.connect(
                    host,
                    port,
                    user,
                    pw,
                    timeout=timeout,
                    host_key_mode=host_key_mode,
                )
                self.log("[OK] Connected.")
                self.log(f"[INFO] Host key policy: {host_key_mode}.")
                self._set_connected_ui(True)
            except paramiko.AuthenticationException:
                self.log(
                    f"[ERROR] Authentication failed for '{user}@{host}:{port}'.\n"
                    f"  \u2022 Double-check your Username and Password.\n"
                    f"  \u2022 The server may not allow password authentication."
                )
                self._set_connected_ui(False)
            except paramiko.SSHException as e:
                self.log(
                    f"[ERROR] SSH error while connecting to {host}:{port}:\n"
                    f"  \u2022 {e}\n"
                    f"  \u2022 Verify the host is reachable and running an SSH server."
                )
                self._set_connected_ui(False)
            except OSError as e:
                self.log(
                    f"[ERROR] Network error connecting to {host}:{port}:\n"
                    f"  \u2022 {e}\n"
                    f"  \u2022 Check the Host/IP and Port, and that the device is online."
                )
                self._set_connected_ui(False)
            except Exception as e:
                self.log(f"[ERROR] Connection failed: {e}")
                self._set_connected_ui(False)
            finally:
                self.is_connecting = False

        threading.Thread(target=worker, daemon=True).start()

    def on_disconnect(self):
        self.log("Disconnecting...")

        try:
            self.ssh.disconnect()
        finally:
            if self.clear_creds_var.get():
                self.pass_var.set("")
                self.log("[INFO] Credentials cleared.")

            self._set_connected_ui(False)
            self.log("[OK] Disconnected.")

    def test_connection(self):
        """Test SSH connectivity without full interaction."""
        self._refresh_connection_state()
        if self.ssh.is_connected():
            messagebox.showinfo("Connected", "Already connected to SSH server.")
            return

        inputs = self._get_connection_inputs()
        if inputs is None:
            return
        host, port, user, pw, timeout = inputs
        host_key_mode = self._get_host_key_mode()

        self.log("Testing connection...")

        def worker():
            try:
                temp_ssh = SSHManager()
                temp_ssh.connect(host, port, user, pw, timeout=timeout, host_key_mode=host_key_mode)
                self.log("[OK] Connection test successful.")
                self.log(f"[INFO] Host key policy: {host_key_mode}.")
                temp_ssh.disconnect()
            except paramiko.AuthenticationException:
                self.log(
                    f"[ERROR] Test failed \u2014 authentication rejected for '{user}@{host}:{port}'.\n"
                    f"  \u2022 Double-check your Username and Password."
                )
            except paramiko.SSHException as e:
                self.log(
                    f"[ERROR] Test failed \u2014 SSH error: {e}\n"
                    f"  \u2022 Verify the host is reachable and running an SSH server."
                )
            except OSError as e:
                self.log(
                    f"[ERROR] Test failed \u2014 network error: {e}\n"
                    f"  \u2022 Check the Host/IP and Port, and that the device is online."
                )
            except Exception as e:
                self.log(f"[ERROR] Connection test failed: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def _set_connected_ui(self, connected: bool):
        """
        UI updates must happen on the Tk main thread.
        We schedule via after().
        """

        def apply():
            self.status_var.set("Connected" if connected else "Disconnected")
            self.connect_btn.configure(state="disabled" if connected else "normal")
            self.disconnect_btn.configure(
                state="normal" if connected else "disabled"
            )

        self.after_idle(apply)

    # -------------------------
    # Action helpers (commands / file upload)
    # -------------------------

    def run_ssh_command(self, command: str):
        """
        Executes a command over SSH and prints output to the terminal pane.
        Uses a background thread so the UI doesn't freeze.
        Maintains command history for recall.
        """
        self._refresh_connection_state()
        if not self.ssh.is_connected():
            messagebox.showwarning(
                "Not Connected",
                "Please connect over SSH first.",
            )
            return

        # Add to history
        if command not in self.command_history or self.command_history[0] != command:
            self.command_history.insert(0, command)
            if len(self.command_history) > COMMAND_HISTORY_LIMIT:
                self.command_history.pop()

        self.history_index = 0
        self.log(f"\n$ {command}")

        def worker():
            try:
                output = self.ssh.run_command(command)
                self.log(output.strip() if output.strip() else "(no output)")
            except Exception as e:
                self.log(f"[ERROR] Command failed: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def prompt_and_run_custom_command(self):
        """
        Small modal dialog that prompts for a command string, then runs it.
        Supports history navigation with Up/Down arrow keys.
        """

        if not self.ssh.is_connected():
            messagebox.showwarning(
                "Not Connected",
                "Please connect over SSH first.",
            )
            return

        dialog = tk.Toplevel(self)
        dialog.title("Run Custom Command")
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("500x100")
        dialog.resizable(False, False)

        ttk.Label(dialog, text="Command:").grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="w",
        )

        cmd_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=cmd_var, width=60)
        entry.grid(row=0, column=1, padx=10, pady=10)
        entry.focus_set()

        # Local history state for this dialog.
        # index=-1 means the user is on their current unsent draft.
        history_state = {"index": -1, "draft": ""}

        def navigate_history(direction: int):
            """Navigate command history with Up (-1) or Down (+1)."""
            if not self.command_history:
                return

            current_index = history_state["index"]

            if current_index == -1:
                history_state["draft"] = cmd_var.get()

            if direction < 0:
                new_index = min(len(self.command_history) - 1, current_index + 1)
            else:
                new_index = current_index - 1

            history_state["index"] = new_index
            if new_index == -1:
                cmd_var.set(history_state["draft"])
            else:
                cmd_var.set(self.command_history[new_index])
            entry.icursor("end")
            return

        def on_key(event):
            if event.keysym == "Up":
                navigate_history(-1)
                return "break"
            elif event.keysym == "Down":
                navigate_history(1)
                return "break"
            elif event.keysym == "Return":
                run_and_close()
                return "break"
            elif event.keysym == "Escape":
                dialog.destroy()
                return "break"

        entry.bind("<Key-Up>", on_key)
        entry.bind("<Key-Down>", on_key)
        entry.bind("<Return>", on_key)
        entry.bind("<Escape>", on_key)

        def run_and_close():
            cmd = cmd_var.get().strip()
            if not cmd:
                messagebox.showwarning("Missing Command", "Enter a command to run.")
                entry.focus_set()
                return

            self.run_ssh_command(cmd)
            dialog.destroy()

        ttk.Button(
            dialog,
            text="Run",
            command=run_and_close,
        ).grid(row=1, column=1, padx=10, pady=(0, 10), sticky="e")

        ttk.Button(
            dialog,
            text="Cancel",
            command=dialog.destroy,
        ).grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

    def upload_config_template(self, remote_path: str = "/tmp/uploaded_config.txt"):
        """
        Template: pick a local file, upload to a remote path.
        You will likely replace remote path rules per device type.
        """
        self._refresh_connection_state()
        if not self.ssh.is_connected():
            messagebox.showwarning(
                "Not Connected",
                "Please connect over SSH first.",
            )
            return

        local_path = filedialog.askopenfilename(title="Select a file to upload")
        if not local_path:
            return

        self.log(f"Uploading:\n  local:  {local_path}\n  remote: {remote_path}")

        def worker():
            try:
                self.ssh.upload_file(local_path, remote_path)
                self.log("[OK] Upload complete.")
            except Exception as e:
                self.log(f"[ERROR] Upload failed: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def send_file_scp(self):
        """
        Prompts for a local file and a remote destination path, then uploads via SFTP.
        """

        if not self.ssh.is_connected():
            messagebox.showwarning(
                "Not Connected",
                "Please connect over SSH first.",
            )
            return

        local_path = filedialog.askopenfilename(title="Select a file to send")
        if not local_path:
            return

        # Ask for remote path
        dialog = tk.Toplevel(self)
        dialog.title("Remote Destination")
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("400x120")

        ttk.Label(
            dialog,
            text="Remote Path (including filename):",
        ).pack(pady=10)

        remote_var = tk.StringVar(value=f"/tmp/{local_path.split('/')[-1]}")
        entry = ttk.Entry(dialog, textvariable=remote_var, width=50)
        entry.pack(pady=5)
        entry.focus_set()
        entry.select_range(0, tk.END)

        def on_confirm():
            remote_path = remote_var.get().strip()
            if remote_path:
                dialog.destroy()
                self._perform_upload(local_path, remote_path)

        ttk.Button(dialog, text="Upload", command=on_confirm).pack(pady=10)

    def _perform_upload(self, local_path: str, remote_path: str):
        self.log(
            f"SCP Upload:\n"
            f"  local:  {local_path}\n"
            f"  remote: {remote_path}"
        )

        def worker():
            try:
                self.ssh.upload_file(local_path, remote_path)
                self.log("[OK] SCP Upload complete.")
            except Exception as e:
                self.log(f"[ERROR] SCP Upload failed: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def show_help_dialog(self):
        """Displays a help dialog with information about the application."""

        help_text = """
SSH Device Manager

Features:
- Connect to remote hosts via SSH.
- Execute predefined and custom commands.
- Upload files via SFTP/SCP.
- View and save terminal output.
- Customize appearance with themes.

Usage:
1. Enter Host/IP, Port, Username, and Password.
2. Click 'Connect'.
3. Use the buttons in the 'Actions' panel to interact with the device.
4. Use 'Run Custom Command...' for specific tasks.
5. Use 'Send File via SCP' to transfer files.

Tips:
- The 'Host / IP' field remembers your recent connections.
- Use the 'Theme' menu to change the application's look.
- Output can be saved to a text file for later analysis.
"""
        messagebox.showinfo("About / Usage", help_text.strip())

    # -------------------------
    # Output helpers
    # -------------------------

    def log(self, text: str):
        """
        Thread-safe log: background threads can call this,
        it queues messages for the UI poller.
        """
        timestamp = time.strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {text}\n")

    def _start_log_poller(self):
        """Poll the queue and append output in the Tk thread."""

        def poll():
            try:
                while True:
                    msg = self.log_queue.get_nowait()
                    self._append_output(msg)
            except queue.Empty:
                pass

            self.after(80, func=poll)

        poll()

    def _append_output(self, msg: str):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", msg)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def clear_output(self):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")

    def copy_output(self):
        text = self.output_text.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
        self.log("[OK] Output copied to clipboard.")

    def save_output(self):
        """Save terminal output to a text file."""
        text = self.output_text.get("1.0", "end-1c")

        if not text.strip():
            messagebox.showwarning("Empty Output", "Nothing to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                self.log(f"[OK] Output saved to {file_path}")
            except Exception as e:
                self.log(f"[ERROR] Failed to save output: {e}")

    # -------------------------
    # File watching / auto-reload
    # -------------------------

    def _get_mtime(self, path: str) -> float:
        """
        Get the last modified time of a file.
        Returns 0 for nonexistent files.
        """
        try:
            return os.path.getmtime(path)
        except Exception:
            return 0

    def _start_sections_watcher(self):
        """
        Start watching the sections file for changes.
        Polls every second (adjustable).
        """

        def poll():
            if os.path.exists(self.sections_path):
                mtime = self._get_mtime(self.sections_path)
                if mtime != self._sections_mtime:
                    # File has been modified; reload sections
                    self.log(
                        f"[INFO] Detected changes in '{self.sections_path}'. Reloading sections..."
                    )
                    self.reload_sections(self.sections_path)
                    self._sections_mtime = mtime

            # Repeat after 1000ms (1 second)
            self.after(1000, poll)

        # Start the polling in the background
        self.after(1000, poll)


# -------------------------
# FUTURE FEATURES / TODO
# -------------------------
"""
Future features and ideas (non-exhaustive):

- Config & UX
  - Integrated Theme Editor inside the `customizer.py` with export/import for `THEMES`.
  - Advanced validation and JSON schema for `sections.json` with user-friendly error messages.
  - Enable/disable auto-reload from the Config menu and show watcher status.
  - Per-host profiles (saved locally, option to encrypt credentials securely).
  - Undo/redo support in the customizer and change history for configs.

- Command & Handler Extensibility
  - Plugin system: a `plugins/` folder with safe, discoverable handlers (load via importlib).
  - More handler tokens (e.g., `__backup_config__`, `__restore_config__`) and mapping file for custom actions.
  - Support for interactive sessions using `invoke_shell()` with paging and prompt handling for network devices.
  - Command batching and scripting: group multiple commands into one button or script file.

- File Transfer & UX
  - Show progress bar and cancel option for uploads/downloads.
  - Support SCP/rsync alternatives and resume capabilities.
  - Preview and validation of uploaded config files before transfer.

- Reliability, Security & Management
  - Host key verification options (load system known_hosts, WarningPolicy, or explicit trust-once flow).
  - Secure storage for credentials (OS keyring integration) and optional MFA hooks.
  - Audit logging: append actions/results to a persistent audit log with timestamps.
  - Role-based access / multi-user scenarios for shared installations.

- Developer & CI
  - Add unit/integration tests covering JSON loader, handler resolution, and UI logic (mocking paramiko/tkinter).
  - Add packaging (PyInstaller) and a simple Dockerfile for headless testing or CI.
  - Add a `watchdog`-based file-watcher as an alternative to polling (optional dependency).

- Accessibility & Internationalization
  - Keyboard-first navigation, ARIA-like support, and screen-reader friendliness.
  - Extract strings for localization and support multiple languages.

- Advanced features
  - CLI mode to run configured actions without launching the GUI.
  - Live preview that simulates command output for common devices, helpful for testing.
  - Web-based remote control front-end (REST API + lightweight web UI) for integration with other systems.

Notes:
- Keep `sections.json` free of credentials - only metadata, labels, and handler tokens/commands.
- Prioritize security for any feature that stores or transmits credentials.
"""

if __name__ == "__main__":
    try:
        app = SSHGuiApp()
        app.mainloop()
    except Exception as e:
        # If something goes wrong during startup, write traceback to a log file for diagnosis
        import traceback

        tb = traceback.format_exc()
        with open(
            "ssh_device_manager_startup_error.log",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(tb)
        raise
