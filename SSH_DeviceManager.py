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

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import dataclass
from typing import Callable, Optional, List
import threading
import queue
import time
import json
import os

# Third-party dependency
import paramiko
# Paramiko allows SSH connections and SFTP file transfers.


# Config: command history limit
COMMAND_HISTORY_LIMIT = 50
CONFIG_FILE = "ssh_device_manager_config.json"


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
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
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
        try:
            if self.sftp:
                self.sftp.close()
        except Exception:
            pass

        try:
            if self.client:
                self.client.close()
        except Exception:
            pass

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

    def __init__(self):
        super().__init__()

        self.title("SSH Command Console (Template)")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE)
        self.config_data = self._load_app_config()

        # Thread-safe queue for log messages (background threads -> UI)
        self.log_queue: "queue.Queue[str]" = queue.Queue()

        # Connection state and history
        self.ssh = SSHManager()
        self.command_history: List[str] = []
        self.history_index: int = 0
        self.is_connecting = False

        self._build_ui()
        self._start_log_poller()
        self._start_connection_monitor()

        # Define your sections + buttons here
        self.sections = self._define_sections()
        self._build_button_sections(self.sections)
        self._refresh_profile_list()

    # -------------------------
    # UI Construction
    # -------------------------

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
        ttk.Label(self.connection_frame, text="Host / IP:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.host_var = tk.StringVar(value="")
        ttk.Entry(self.connection_frame, textvariable=self.host_var, width=20).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(self.connection_frame, text="Port:").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.port_var = tk.IntVar(value=22)
        ttk.Entry(self.connection_frame, textvariable=self.port_var, width=6).grid(row=0, column=3, padx=6, pady=6)

        ttk.Label(self.connection_frame, text="Username:").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.user_var = tk.StringVar(value="")
        ttk.Entry(self.connection_frame, textvariable=self.user_var, width=16).grid(row=0, column=5, padx=6, pady=6)

        ttk.Label(self.connection_frame, text="Password:").grid(row=0, column=6, padx=6, pady=6, sticky="w")
        self.pass_var = tk.StringVar()
        ttk.Entry(self.connection_frame, textvariable=self.pass_var, width=16, show="*").grid(row=0, column=7, padx=6, pady=6)

        self.connect_btn = ttk.Button(self.connection_frame, text="Connect", command=self.on_connect)
        self.connect_btn.grid(row=0, column=8, padx=6, pady=6)

        self.disconnect_btn = ttk.Button(self.connection_frame, text="Disconnect", command=self.on_disconnect, state="disabled")
        self.disconnect_btn.grid(row=0, column=9, padx=6, pady=6)

        self.status_var = tk.StringVar(value="Disconnected")
        ttk.Label(self.connection_frame, textvariable=self.status_var).grid(row=0, column=10, padx=10, pady=6, sticky="e")

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
        ttk.Label(self.settings_frame, text="Connection Timeout (s):").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.timeout_var = tk.IntVar(value=10)
        ttk.Spinbox(self.settings_frame, from_=5, to=60, textvariable=self.timeout_var, width=6).grid(row=0, column=1, padx=6, pady=6, sticky="w")

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
        self.output_text = tk.Text(self.output_frame, wrap="word", height=12, font=("Courier New", 9))
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

        ttk.Button(controls, text="Clear Output", command=self.clear_output).grid(row=0, column=0, sticky="w")
        ttk.Button(controls, text="Copy Output", command=self.copy_output).grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Button(controls, text="Save Output", command=self.save_output).grid(row=0, column=2, sticky="w", padx=(8, 0))

    # -------------------------
    # Define Sections / Buttons
    # -------------------------

    def _default_action_config(self) -> list[dict]:
        return [
            {
                "title": "Status",
                "max_buttons": 6,
                "actions": [
                    {
                        "label": "Show Version",
                        "enabled": True,
                        "type": "command",
                        "value": "show version",
                        "tooltip": "Runs: show version",
                    },
                    {
                        "label": "Show Interfaces",
                        "enabled": True,
                        "type": "command",
                        "value": "show interfaces",
                        "tooltip": "Runs: show interfaces",
                    },
                    {
                        "label": "Placeholder A",
                        "enabled": False,
                        "type": "command",
                        "value": "echo Placeholder A",
                        "tooltip": "Disabled until you set enabled=True",
                    },
                ],
            },
            {
                "title": "Maintenance",
                "max_buttons": 6,
                "actions": [
                    {
                        "label": "Upload Config (Template)",
                        "enabled": True,
                        "type": "upload",
                        "value": "/tmp/uploaded_config.txt",
                        "tooltip": "Opens a file picker and uploads to a remote path",
                    },
                    {
                        "label": "Reboot Device",
                        "enabled": False,
                        "type": "command",
                        "value": "reload",
                        "tooltip": "Dangerous: enable only when ready",
                    },
                ],
            },
            {
                "title": "Custom",
                "max_buttons": 6,
                "actions": [
                    {
                        "label": "Run Custom Command...",
                        "enabled": True,
                        "type": "custom_command",
                        "tooltip": "Prompts you for a command string",
                    },
                ],
            },
        ]

    def _default_config_data(self) -> dict:
        return {
            "profiles": {},
            "actions": self._default_action_config(),
        }

    def _load_app_config(self) -> dict:
        if not os.path.exists(self.config_path):
            config = self._default_config_data()
            self.config_data = config
            self._save_app_config()
            return config

        try:
            with open(self.config_path, "r", encoding="utf-8") as handle:
                loaded = json.load(handle)
        except (OSError, json.JSONDecodeError):
            config = self._default_config_data()
            self.config_data = config
            self._save_app_config()
            return config

        config = self._default_config_data()
        if isinstance(loaded, dict):
            profiles = loaded.get("profiles")
            actions = loaded.get("actions")
            if isinstance(profiles, dict):
                config["profiles"] = profiles
            if isinstance(actions, list) and actions:
                config["actions"] = actions
        return config

    def _save_app_config(self):
        with open(self.config_path, "w", encoding="utf-8") as handle:
            json.dump(self.config_data, handle, indent=2)

    def _make_action_handler(self, action_type: str, value: str) -> Callable[[], None]:
        if action_type == "command":
            return lambda command=value: self.run_ssh_command(command)
        if action_type == "upload":
            return lambda remote_path=value: self.upload_config_template(remote_path)
        if action_type == "custom_command":
            return self.prompt_and_run_custom_command
        return lambda: self.log(f"[WARN] Unsupported action type: {action_type}")

    def _define_sections(self) -> List[ButtonSection]:
        """
        Define your sections here.

        Rules:
        - max_buttons is a clear LIMIT per section.
        - each ActionButton has enabled=True/False
        - handler points to a function that executes a command or upload.
        """

        sections: List[ButtonSection] = []

        for raw_section in self.config_data.get("actions", []):
            title = str(raw_section.get("title", "Untitled"))
            max_buttons = raw_section.get("max_buttons", 6)
            if not isinstance(max_buttons, int) or max_buttons < 1:
                max_buttons = 6

            actions: List[ActionButton] = []
            for raw_action in raw_section.get("actions", []):
                label = str(raw_action.get("label", "Unnamed Action"))
                enabled = bool(raw_action.get("enabled", True))
                action_type = str(raw_action.get("type", "command"))
                value = str(raw_action.get("value", ""))
                tooltip = str(raw_action.get("tooltip", ""))
                handler = self._make_action_handler(action_type, value)
                actions.append(
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
                    max_buttons=max_buttons,
                    actions=actions,
                )
            )

        return sections or [
            ButtonSection(title="Custom", max_buttons=6, actions=[
                ActionButton(
                    "Run Custom Command...",
                    enabled=True,
                    handler=self.prompt_and_run_custom_command,
                    tooltip="Prompts you for a command string",
                )
            ])
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

        for i, section in enumerate(sections):
            # Section frame
            sec_frame = ttk.Frame(container, padding=(6, 2))
            sec_frame.grid(row=0, column=i * 2, sticky="n")

            # Section title
            ttk.Label(sec_frame, text=section.title, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))

            # Enforce max buttons visually and logically
            enabled_actions = [a for a in section.actions if a.enabled]
            if len(enabled_actions) > section.max_buttons:
                # Template behavior: warn once in output and truncate
                self.log(f"[WARN] Section '{section.title}' exceeds max_buttons={section.max_buttons}. Truncating.")
                enabled_actions = enabled_actions[:section.max_buttons]

            # Create the buttons
            for action in enabled_actions:
                btn = ttk.Button(sec_frame, text=action.label, command=action.handler, width=24)
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

    def _refresh_profile_list(self):
        profile_names = sorted(self.config_data.get("profiles", {}).keys())
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

        self.config_data.setdefault("profiles", {})[profile_name] = {
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

        profile = self.config_data.get("profiles", {}).get(profile_name)
        if not isinstance(profile, dict):
            messagebox.showerror("Missing Profile", f"Profile '{profile_name}' was not found.")
            self._refresh_profile_list()
            return

        self.profile_name_var.set(profile_name)
        self.host_var.set(str(profile.get("host", "")))
        self.port_var.set(int(profile.get("port", 22)))
        self.user_var.set(str(profile.get("username", "")))
        self.timeout_var.set(int(profile.get("timeout", 10)))
        self.host_key_mode_var.set(str(profile.get("host_key_mode", "warning")))
        self.log(f"[OK] Loaded profile '{profile_name}'.")

    def delete_selected_profile(self):
        profile_name = self.profile_select_var.get().strip()
        if not profile_name:
            messagebox.showwarning("No Profile Selected", "Choose a saved profile to delete.")
            return

        confirmed = messagebox.askyesno("Delete Profile", f"Delete profile '{profile_name}'?")
        if not confirmed:
            return

        profiles = self.config_data.get("profiles", {})
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
        """Validate the current connection form and return normalized values."""
        host = self.host_var.get().strip()
        user = self.user_var.get().strip()
        pw = self.pass_var.get()

        if not host or not user:
            messagebox.showerror("Missing Info", "Please enter Host/IP and Username.")
            return None

        port = self._parse_int_input(str(self.port_var.get()), "Port", minimum=1, maximum=65535)
        if port is None:
            return None

        timeout = self._parse_int_input(str(self.timeout_var.get()), "Connection Timeout", minimum=1, maximum=300)
        if timeout is None:
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
            messagebox.showwarning("In Progress", "Connection attempt already in progress.")
            return

        host_key_mode = self._get_host_key_mode()
        self.log(f"Connecting to {host}:{port} as {user}...")
        self.is_connecting = True

        # Run connect in a thread so UI stays responsive
        def worker():
            try:
                self.ssh.connect(host, port, user, pw, timeout=timeout, host_key_mode=host_key_mode)
                self.log("[OK] Connected.")
                self.log(f"[INFO] Host key policy: {host_key_mode}.")
                self._set_connected_ui(True)
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
            self.disconnect_btn.configure(state="normal" if connected else "disabled")
        self.after(0, apply)

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
            messagebox.showwarning("Not Connected", "Please connect over SSH first.")
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
            messagebox.showwarning("Not Connected", "Please connect over SSH first.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Run Custom Command")
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("500x100")
        dialog.resizable(False, False)

        ttk.Label(dialog, text="Command:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
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
        """
        Template: pick a local file, upload to a remote path.
        You will likely replace remote path rules per device type.
        """
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
            self.after(80, poll)
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
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                self.log(f"[OK] Output saved to {file_path}")
            except Exception as e:
                self.log(f"[ERROR] Failed to save output: {e}")


if __name__ == "__main__":
    app = SSHGuiApp()
    app.mainloop()
