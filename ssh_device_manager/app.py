"""
SSHGuiApp - Main Tkinter application for the SSH Device Manager.

This is the orchestrator: it imports modules for models, SSH, themes,
config, validation, sections loading, and output, then wires them into
the Tkinter UI.
"""

import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable, List, Optional

import paramiko

from .models import ActionButton, ButtonSection, ToolTip
from .ssh_manager import SSHManager
from .themes import THEMES
from . import config as app_config_mod
from . import sections_loader
from .validation import parse_int_input, get_connection_inputs, get_host_key_mode
from .output import OutputManager

COMMAND_HISTORY_LIMIT = 500
APP_CONFIG_FILE = "ssh_device_manager_config.json"
DEFAULT_SECTIONS_FILE = "sections.json"


class SSHGuiApp(tk.Tk):
    """
    Tkinter App:
    - Top: connection fields + connect/disconnect + settings
    - Middle: button sections (with vertical separators)
    - Bottom: terminal output pane
    """

    THEMES = THEMES

    def __init__(self, init_ui: bool = True):
        super().__init__()
        self.app_config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.pardir,
            APP_CONFIG_FILE,
        )
        self.app_config = app_config_mod.load_app_config(self.app_config_path)

        if not init_ui:
            self.log_queue: "queue.Queue[str]" = queue.Queue()

            self.ssh = SSHManager()
            self.command_history: List[str] = []
            self.history_index: int = 0
            self.is_connecting = False
            self.host_history: List[str] = []

            self.current_theme = tk.StringVar(value="Default")

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

            class _ComboPlaceholder:
                def __init__(self):
                    self._items = {}
                def __setitem__(self, k, v):
                    self._items[k] = v
                def __getitem__(self, k):
                    return self._items.get(k)
            self.host_combo = _ComboPlaceholder()
            self.profile_combo = _ComboPlaceholder()

            class _BtnPlaceholder:
                def configure(self, *a, **k):
                    pass
            self.connect_btn = _BtnPlaceholder()
            self.disconnect_btn = _BtnPlaceholder()

            self.output_text = MagicMock()

            self.sections_path = DEFAULT_SECTIONS_FILE
            self.sections = self.load_sections_from_file(self.sections_path)
            return

        self.title("SSH Command Console (Template)")
        self.geometry("1400x900")
        self.minsize(1000, 700)

        try:
            if self.tk.call("tk", "windowingsystem") == "x11":
                self.attributes("-zoomed", True)
            elif self.tk.call("tk", "windowingsystem") == "win32":
                self.state("zoomed")
        except (tk.TclError, Exception):
            pass

        self.log_queue: "queue.Queue[str]" = queue.Queue()

        self.ssh = SSHManager()
        self.command_history: List[str] = []
        self.history_index: int = 0
        self.is_connecting = False
        self.host_history: List[str] = []

        self.current_theme = tk.StringVar(value="Default")

        self._build_menu()
        self._build_ui()

        self._output_mgr = OutputManager(self.output_text)
        self._output_mgr.start_poller(self)

        self._start_connection_monitor()

        self.sections_path = DEFAULT_SECTIONS_FILE
        self.sections = self.load_sections_from_file(self.sections_path)
        self._build_button_sections(self.sections)
        self._refresh_profile_list()

        self._sections_mtime = self._get_mtime(self.sections_path)
        self._start_sections_watcher()

        self.apply_theme("Default")

    # -------------------------
    # UI Construction
    # -------------------------

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About / Usage", command=self.show_help_dialog)

        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="     Theme", menu=theme_menu)
        for theme_name in sorted(self.THEMES.keys()):
            theme_menu.add_radiobutton(
                label=theme_name,
                variable=self.current_theme,
                value=theme_name,
                command=lambda t=theme_name: self.apply_theme(t),
            )

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
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        self.connection_frame = tk.LabelFrame(self, text="SSH Connection")
        self.connection_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        self.connection_frame.columnconfigure(10, weight=1)

        self.commands_frame = tk.LabelFrame(self, text="Actions")
        self.commands_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=8)

        self.settings_frame = tk.LabelFrame(self, text="Settings")
        self.settings_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 8))

        self.output_frame = tk.LabelFrame(self, text="Terminal Output")
        self.output_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.output_frame.rowconfigure(0, weight=1)
        self.output_frame.columnconfigure(0, weight=1)

        # ----- Connection inputs -----
        tk.Label(self.connection_frame, text="Host / IP:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.host_var = tk.StringVar(value="")
        self.host_combo = ttk.Combobox(self.connection_frame, textvariable=self.host_var, width=20)
        self.host_combo.grid(row=0, column=1, padx=6, pady=6)
        self.host_combo.bind("<<ComboboxSelected>>", self.on_host_selected)

        tk.Label(self.connection_frame, text="Port:").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.port_var = tk.IntVar(value=22)
        tk.Entry(self.connection_frame, textvariable=self.port_var, width=6).grid(row=0, column=3, padx=6, pady=6)

        tk.Label(self.connection_frame, text="Username:").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.user_var = tk.StringVar(value="")
        tk.Entry(self.connection_frame, textvariable=self.user_var, width=16).grid(row=0, column=5, padx=6, pady=6)

        tk.Label(self.connection_frame, text="Password:").grid(row=0, column=6, padx=6, pady=6, sticky="w")
        self.pass_var = tk.StringVar()
        tk.Entry(self.connection_frame, textvariable=self.pass_var, width=16, show="*").grid(row=0, column=7, padx=6, pady=6)

        self.connect_btn = tk.Button(self.connection_frame, text="Connect", command=self.on_connect)
        self.connect_btn.grid(row=0, column=8, padx=6, pady=6)

        self.disconnect_btn = tk.Button(self.connection_frame, text="Disconnect", command=self.on_disconnect, state="disabled")
        self.disconnect_btn.grid(row=0, column=9, padx=6, pady=6)

        self.status_var = tk.StringVar(value="Disconnected")
        tk.Label(self.connection_frame, textvariable=self.status_var).grid(row=0, column=10, padx=10, pady=6, sticky="e")

        tk.Label(self.connection_frame, text="Profile Name:").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.profile_name_var = tk.StringVar()
        tk.Entry(self.connection_frame, textvariable=self.profile_name_var, width=20).grid(row=1, column=1, padx=6, pady=6)

        tk.Label(self.connection_frame, text="Saved Profiles:").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        self.profile_select_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(self.connection_frame, textvariable=self.profile_select_var, state="readonly", width=18)
        self.profile_combo.grid(row=1, column=3, padx=6, pady=6, sticky="w")
        self.profile_combo.bind("<<ComboboxSelected>>", lambda _event: self.load_selected_profile())

        tk.Button(self.connection_frame, text="Save Profile", command=self.save_profile).grid(row=1, column=4, padx=6, pady=6)
        tk.Button(self.connection_frame, text="Load Profile", command=self.load_selected_profile).grid(row=1, column=5, padx=6, pady=6)
        tk.Button(self.connection_frame, text="Delete Profile", command=self.delete_selected_profile).grid(row=1, column=6, padx=6, pady=6)

        # ----- Settings -----
        tk.Label(self.settings_frame, text="Connection Timeout (s):").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.timeout_var = tk.IntVar(value=10)
        tk.Spinbox(self.settings_frame, from_=5, to=60, textvariable=self.timeout_var, width=6).grid(row=0, column=1, padx=6, pady=6, sticky="w")

        tk.Label(self.settings_frame, text="Host Key Policy:").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.host_key_mode_var = tk.StringVar(value="warning")
        self.host_key_mode_combo = ttk.Combobox(self.settings_frame, textvariable=self.host_key_mode_var, state="readonly", width=18, values=("strict", "warning", "auto"))
        self.host_key_mode_combo.grid(row=0, column=3, padx=6, pady=6, sticky="w")

        self.clear_creds_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self.settings_frame, text="Clear credentials on disconnect", variable=self.clear_creds_var).grid(row=0, column=4, padx=6, pady=6, sticky="w")

        tk.Button(self.settings_frame, text="Test Connection", command=self.test_connection).grid(row=0, column=5, padx=6, pady=6, sticky="w")

        # ----- Output pane -----
        self.output_text = tk.Text(self.output_frame, wrap="word", height=12, font=("Courier New", 9))
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)

        scroll = ttk.Scrollbar(self.output_frame, command=self.output_text.yview)
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)
        self.output_text.configure(yscrollcommand=scroll.set)
        self.output_text.configure(state="disabled")

        controls = ttk.Frame(self.output_frame)
        controls.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))
        controls.columnconfigure(0, weight=1)

        tk.Button(controls, text="Clear Output", command=self.clear_output).grid(row=0, column=0, sticky="w")
        tk.Button(controls, text="Copy Output", command=self.copy_output).grid(row=0, column=1, sticky="w", padx=(8, 0))
        tk.Button(controls, text="Save Output", command=self.save_output).grid(row=0, column=2, sticky="w", padx=(8, 0))

    # -------------------------
    # Theme Management
    # -------------------------

    def apply_theme(self, theme_name: str):
        theme = self.THEMES.get(theme_name, self.THEMES["Default"])

        btn_bg = theme.get("btn_bg", theme["bg"])
        border = theme.get("border", theme["fg"])
        label_fg = theme.get("label_fg", theme["fg"])

        self.configure(bg=theme["bg"])

        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", background=theme["bg"], foreground=theme["fg"], fieldbackground=theme["entry_bg"], bordercolor=border)
        style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
        style.configure("TButton", background=btn_bg, foreground=theme["fg"], bordercolor=border)
        style.configure("TEntry", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"], bordercolor=border, insertcolor=theme["entry_fg"])
        style.configure("TCombobox", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"], arrowcolor=theme["fg"], bordercolor=border)
        style.configure("TLabelframe", background=theme["bg"], foreground=label_fg, bordercolor=border)
        style.configure("TLabelframe.Label", background=theme["bg"], foreground=label_fg)
        style.configure("TCheckbutton", background=theme["bg"], foreground=theme["fg"], indicatorcolor=theme["entry_bg"])
        style.configure("TSpinbox", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"], arrowcolor=theme["fg"], bordercolor=border)
        style.configure("TSeparator", background=border)

        style.map("TButton", background=[("active", theme["select_bg"]), ("pressed", theme["select_bg"])], foreground=[("active", theme["select_fg"]), ("pressed", theme["select_fg"])])
        style.map("TEntry", fieldbackground=[("readonly", theme["bg"])], foreground=[("readonly", theme["fg"])])
        style.map("TCombobox", fieldbackground=[("readonly", theme["entry_bg"])], foreground=[("readonly", theme["entry_fg"])], selectbackground=[("readonly", theme["select_bg"])], selectforeground=[("readonly", theme["select_fg"])])
        style.map("TCheckbutton", background=[("active", theme["bg"])], indicatorcolor=[("selected", theme["select_bg"])])

        self.output_text.configure(bg=theme["text_bg"], fg=theme["text_fg"], insertbackground=theme["fg"], selectbackground=theme["select_bg"], selectforeground=theme["select_fg"])

        # Apply colors to raw Tk widgets (Label, Button, Entry, etc.)
        self._apply_theme_to_children(self, theme, btn_bg, border, label_fg)

    def _apply_theme_to_children(self, parent, theme, btn_bg, border, label_fg):
        """Recursively configure raw Tk widgets that ttk styles don't reach."""
        for child in parent.winfo_children():
            cls_name = child.winfo_class()
            try:
                if cls_name == "Label":
                    child.configure(bg=theme["bg"], fg=label_fg)
                elif cls_name == "Button":
                    child.configure(
                        bg=btn_bg, fg=theme["fg"],
                        activebackground=theme["select_bg"],
                        activeforeground=theme["select_fg"],
                        highlightbackground=border,
                    )
                elif cls_name == "Entry":
                    child.configure(
                        bg=theme["entry_bg"], fg=theme["entry_fg"],
                        insertbackground=theme["entry_fg"],
                        highlightbackground=border,
                        selectbackground=theme["select_bg"],
                        selectforeground=theme["select_fg"],
                    )
                elif cls_name == "Labelframe":
                    child.configure(bg=theme["bg"], fg=label_fg)
                elif cls_name == "Checkbutton":
                    child.configure(
                        bg=theme["bg"], fg=theme["fg"],
                        activebackground=theme["bg"],
                        activeforeground=theme["fg"],
                        selectcolor=theme["entry_bg"],
                        highlightbackground=border,
                    )
                elif cls_name == "Spinbox":
                    child.configure(
                        bg=theme["entry_bg"], fg=theme["entry_fg"],
                        buttonbackground=btn_bg,
                        insertbackground=theme["entry_fg"],
                        highlightbackground=border,
                        selectbackground=theme["select_bg"],
                        selectforeground=theme["select_fg"],
                    )
                elif cls_name == "Menu":
                    child.configure(
                        bg=theme["bg"], fg=theme["fg"],
                        activebackground=theme["select_bg"],
                        activeforeground=theme["select_fg"],
                    )
                elif cls_name == "Frame":
                    child.configure(bg=theme["bg"])
            except tk.TclError:
                pass
            self._apply_theme_to_children(child, theme, btn_bg, border, label_fg)

    # -------------------------
    # Sections loader + integration
    # -------------------------

    def load_sections_from_file(self, path: str) -> List[ButtonSection]:
        return sections_loader.load_sections_from_file(
            path,
            log=self.log,
            run_ssh_command=self.run_ssh_command,
            upload_config_template=self.upload_config_template,
            send_file_scp=self.send_file_scp,
            prompt_and_run_custom_command=self.prompt_and_run_custom_command,
            fallback=self._define_sections,
        )

    def reload_sections(self, path: str = DEFAULT_SECTIONS_FILE):
        self.sections_path = path
        self.log(f"Reloading sections from '{path}'...")
        self.sections = self.load_sections_from_file(path)
        self._build_button_sections(self.sections)
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
    # Define Sections / Buttons (fallback)
    # -------------------------

    def _define_sections(self) -> List[ButtonSection]:
        show_version = "show version"
        show_interfaces = "show interfaces"
        reboot = "reload"

        return [
            ButtonSection(
                title="Status",
                max_buttons=6,
                actions=[
                    ActionButton("Show Version", enabled=True, handler=lambda: self.run_ssh_command(show_version), tooltip="Runs: show version"),
                    ActionButton("Show Interfaces", enabled=True, handler=lambda: self.run_ssh_command(show_interfaces), tooltip="Runs: show interfaces"),
                    ActionButton("Placeholder A", enabled=False, handler=lambda: self.run_ssh_command("echo Placeholder A"), tooltip="Disabled until you set enabled=True"),
                ],
            ),
            ButtonSection(
                title="Maintenance",
                max_buttons=6,
                actions=[
                    ActionButton("Upload Config (Template)", enabled=True, handler=self.upload_config_template, tooltip="Opens a file picker and uploads to a remote path"),
                    ActionButton("Send File via SCP", enabled=True, handler=self.send_file_scp, tooltip="Send a file to the remote server via SCP"),
                    ActionButton("Reboot Device", enabled=False, handler=lambda: self.run_ssh_command(reboot), tooltip="Dangerous: enable only when ready"),
                ],
            ),
            ButtonSection(
                title="Custom",
                max_buttons=6,
                actions=[
                    ActionButton("Run Custom Command...", enabled=True, handler=self.prompt_and_run_custom_command, tooltip="Prompts you for a command string"),
                ],
            ),
        ]

    def _build_button_sections(self, sections: List[ButtonSection]):
        for child in self.commands_frame.winfo_children():
            child.destroy()

        container = ttk.Frame(self.commands_frame)
        container.pack(fill="x", padx=8, pady=8)

        total_columns = len(sections) * 2 - 1
        for i in range(total_columns):
            if i % 2 == 0:
                container.columnconfigure(i, weight=1, uniform="section")
            else:
                container.columnconfigure(i, weight=0)

        for i, section in enumerate(sections):
            sec_frame = ttk.Frame(container, padding=(6, 2))
            sec_frame.grid(row=0, column=i * 2, sticky="nsew")

            ttk.Label(sec_frame, text=section.title, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))

            enabled_actions = [a for a in section.actions if a.enabled]
            if len(enabled_actions) > section.max_buttons:
                self.log(f"[WARN] Section '{section.title}' exceeds max_buttons={section.max_buttons}. Truncating.")
                enabled_actions = enabled_actions[: section.max_buttons]

            for action in enabled_actions:
                btn = ttk.Button(sec_frame, text=action.label, command=action.handler, width=24)
                btn.pack(fill="x", pady=3)
                ToolTip(btn, action.tooltip)

            if i < len(sections) - 1:
                sep = ttk.Separator(container, orient="vertical")
                sep.grid(row=0, column=i * 2 + 1, sticky="ns", padx=10)
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

    # --- Delegation to validation module ---

    def _parse_int_input(self, value: str, label: str, minimum: int = 1, maximum: Optional[int] = None) -> Optional[int]:
        return parse_int_input(value, label, minimum, maximum)

    def _get_connection_inputs(self):
        return get_connection_inputs(
            self.host_var, self.port_var, self.user_var, self.pass_var, self.timeout_var,
            log=self.log,
        )

    def _get_host_key_mode(self) -> str:
        return get_host_key_mode(self.host_key_mode_var)

    # --- Config persistence delegation ---

    def _load_app_config(self) -> dict:
        return app_config_mod.load_app_config(self.app_config_path)

    def _save_app_config(self):
        app_config_mod.save_app_config(self.app_config_path, self.app_config)

    # --- Connection state ---

    def _refresh_connection_state(self, *, notify_on_drop: bool = False):
        connected = self.ssh.is_connected()
        was_connecting = self.is_connecting
        self._set_connected_ui(connected)
        if notify_on_drop and not connected and not was_connecting:
            self.log("[WARN] SSH session is no longer active.")

    def _start_connection_monitor(self):
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
            messagebox.showwarning("In Progress", "Connection attempt already in progress.")
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
                self.ssh.connect(host, port, user, pw, timeout=timeout, host_key_mode=host_key_mode)
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
        def apply():
            self.status_var.set("Connected" if connected else "Disconnected")
            self.connect_btn.configure(state="disabled" if connected else "normal")
            self.disconnect_btn.configure(state="normal" if connected else "disabled")
        self.after_idle(apply)

    # -------------------------
    # Action helpers
    # -------------------------

    def run_ssh_command(self, command: str):
        self._refresh_connection_state()
        if not self.ssh.is_connected():
            messagebox.showwarning("Not Connected", "Please connect over SSH first.")
            return

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
        if not self.ssh.is_connected():
            messagebox.showwarning("Not Connected", "Please connect over SSH first.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Run Custom Command")
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("500x100")
        dialog.resizable(False, False)

        tk.Label(dialog, text="Command:").grid(row=0, column=0, padx=10, pady=10, sticky="w")

        cmd_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=cmd_var, width=60)
        entry.grid(row=0, column=1, padx=10, pady=10)
        entry.focus_set()

        history_state = {"index": -1, "draft": ""}

        def navigate_history(direction: int):
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

        ttk.Button(dialog, text="Run", command=run_and_close).grid(row=1, column=1, padx=10, pady=(0, 10), sticky="e")
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

    def upload_config_template(self, remote_path: str = "/tmp/uploaded_config.txt"):
        self._refresh_connection_state()
        if not self.ssh.is_connected():
            messagebox.showwarning("Not Connected", "Please connect over SSH first.")
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
        if not self.ssh.is_connected():
            messagebox.showwarning("Not Connected", "Please connect over SSH first.")
            return

        local_path = filedialog.askopenfilename(title="Select a file to send")
        if not local_path:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Remote Destination")
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("400x120")

        tk.Label(dialog, text="Remote Path (including filename):").pack(pady=10)
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

        tk.Button(dialog, text="Upload", command=on_confirm).pack(pady=10)

    def _perform_upload(self, local_path: str, remote_path: str):
        self.log(f"SCP Upload:\n  local:  {local_path}\n  remote: {remote_path}")

        def worker():
            try:
                self.ssh.upload_file(local_path, remote_path)
                self.log("[OK] SCP Upload complete.")
            except Exception as e:
                self.log(f"[ERROR] SCP Upload failed: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def show_help_dialog(self):
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
        import time
        timestamp = time.strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {text}\n")

    def _start_log_poller(self):
        import queue as _q

        def poll():
            try:
                while True:
                    msg = self.log_queue.get_nowait()
                    self._append_output(msg)
            except _q.Empty:
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

    def _get_mtime(self, path: str):
        try:
            return os.path.getmtime(path)
        except Exception:
            return None

    def _start_sections_watcher(self, interval_ms: int = 1000):
        def check():
            try:
                current = self._get_mtime(self.sections_path)
                if current != getattr(self, "_sections_mtime", None):
                    self.log(f"[INFO] Detected change in sections file '{self.sections_path}', reloading...")
                    self.reload_sections(self.sections_path)
            except Exception as e:
                self.log(f"[WARN] sections watcher error: {e}")
            finally:
                self.after(interval_ms, check)
        self.after(interval_ms, check)
