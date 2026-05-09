"""
SSHGuiApp - Main Tkinter application for the SSH Device Manager.

This is the orchestrator: it imports modules for models, SSH, themes,
config, validation, sections loading, and output, then wires them into
the Tkinter UI.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

from .models import ButtonSection
from .ssh_manager import SSHManager
from .themes import THEMES
from . import config as app_config_mod
from .controllers import (
    ActionController,
    ConnectionController,
    ProfileController,
    SectionsController,
)
from .constants import COMMAND_HISTORY_LIMIT, APP_CONFIG_FILE, DEFAULT_SECTIONS_FILE
from .output import OutputManager
from .validation import parse_int_input, get_connection_inputs, get_host_key_mode


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

        self.ssh = SSHManager()
        self.command_history: List[str] = []
        self.history_index: int = 0
        self.is_connecting = False
        self.host_history: List[str] = []
        self.current_theme = tk.StringVar(value="Default")

        self.connection_controller = ConnectionController(self)
        self.action_controller = ActionController(self)
        self.profile_controller = ProfileController(self)
        self.sections_controller = SectionsController(self)

        if not init_ui:
            self._init_headless_state()
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

        self._build_menu()
        self._build_ui()
        self._initialize_output_manager()

        self._start_log_poller()
        self._start_connection_monitor()

        self.sections_path = DEFAULT_SECTIONS_FILE
        self.sections = self.load_sections_from_file(self.sections_path)
        self._build_button_sections(self.sections)
        self._refresh_profile_list()

        self._sections_mtime = self._get_mtime(self.sections_path)
        self._start_sections_watcher()

        self.apply_theme("Default")

    def _init_headless_state(self):
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
        self.status_var = MagicMock()
        self.status_var.get.return_value = "Disconnected"

        class _ComboPlaceholder:
            def __init__(self):
                self._items = {}
            def __setitem__(self, key, value):
                self._items[key] = value
            def __getitem__(self, key):
                return self._items.get(key)

        self.host_combo = _ComboPlaceholder()
        self.profile_combo = _ComboPlaceholder()

        class _BtnPlaceholder:
            def configure(self, *a, **k):
                pass

        self.connect_btn = _BtnPlaceholder()
        self.disconnect_btn = _BtnPlaceholder()

        self.output_text = MagicMock()
        self._initialize_output_manager()

        self.sections_path = DEFAULT_SECTIONS_FILE
        self.sections = self.load_sections_from_file(self.sections_path)

    def _initialize_output_manager(self):
        self.output_manager = OutputManager(self.output_text)
        self.log_queue = self.output_manager.log_queue

    def _sync_output_manager_widget(self):
        self.output_manager.output_text = self.output_text

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
        return self.sections_controller.load_sections_from_file(path)

    def reload_sections(self, path: str = DEFAULT_SECTIONS_FILE):
        self.sections_controller.reload_sections(path)

    def open_sections_file(self, default_path: str = DEFAULT_SECTIONS_FILE):
        self.sections_controller.open_sections_file(default_path)

    # -------------------------
    # Define Sections / Buttons (fallback)
    # -------------------------

    def _define_sections(self) -> List[ButtonSection]:
        return self.sections_controller.define_sections()

    def _build_button_sections(self, sections: List[ButtonSection]):
        self.sections_controller.build_button_sections(sections)

    # -------------------------
    # Connection handlers
    # -------------------------

    def on_host_selected(self, _event):
        self.connection_controller.on_host_selected(_event)

    def _refresh_profile_list(self):
        self.profile_controller.refresh_profile_list()

    def save_profile(self):
        self.profile_controller.save_profile()

    def load_selected_profile(self):
        self.profile_controller.load_selected_profile()

    def delete_selected_profile(self):
        self.profile_controller.delete_selected_profile()

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

    def _create_temp_ssh_manager(self):
        return SSHManager()

    # --- Connection state ---

    def _refresh_connection_state(self, *, notify_on_drop: bool = False):
        self.connection_controller.refresh_connection_state(notify_on_drop=notify_on_drop)

    def _start_connection_monitor(self):
        self.connection_controller.start_connection_monitor()

    def on_connect(self):
        self.connection_controller.connect()

    def on_disconnect(self):
        self.connection_controller.disconnect()

    def test_connection(self):
        self.connection_controller.test_connection()

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
        self.action_controller.run_ssh_command(command)

    def prompt_and_run_custom_command(self):
        self.action_controller.prompt_and_run_custom_command()

    def upload_config_template(self, remote_path: str = "/tmp/uploaded_config.txt"):
        self.action_controller.upload_config_template(remote_path)

    def send_file_scp(self):
        self.action_controller.send_file_scp()

    def _perform_upload(self, local_path: str, remote_path: str):
        self.action_controller.perform_upload(local_path, remote_path)

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
        self.output_manager.log(text)

    def _start_log_poller(self):
        self._sync_output_manager_widget()
        self.output_manager.start_poller(self)

    def _append_output(self, msg: str):
        self._sync_output_manager_widget()
        self.output_manager._append(msg)

    def clear_output(self):
        self._sync_output_manager_widget()
        self.output_manager.clear()

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
                with open(file_path, "w", encoding="utf-8") as handle:
                    handle.write(text)
                self.log(f"[OK] Output saved to {file_path}")
            except Exception as exc:
                self.log(f"[ERROR] Failed to save output: {exc}")

    # -------------------------
    # File watching / auto-reload
    # -------------------------

    def _get_mtime(self, path: str):
        return self.sections_controller.get_mtime(path)

    def _start_sections_watcher(self, interval_ms: int = 1000):
        self.sections_controller.start_sections_watcher(interval_ms)
