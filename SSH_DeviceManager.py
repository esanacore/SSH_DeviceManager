
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
- For "network devices", you may need to tweak prompt handling, paging, etc.'
- Paramiko is a third-party library; install via `pip install paramiko`
- This code is modular and can be extended with more features as needed.
- Designed for clarity and ease of modification.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import dataclass
from typing import Callable, Optional, List
import threading
import queue
import time

# Third-party dependency
import paramiko
# Paramiko allows SSH connections and SFTP file transfers.



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

    def is_connected(self) -> bool:
        return self.client is not None

    def connect(self, host: str, port: int, username: str, password: str, timeout: int = 10):
        if self.client:
            self.disconnect()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # template behavior
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
        # SFTP is optional; only created when needed, but you can also open it here.
        self.sftp = None

    def disconnect(self):
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
    - Top: connection fields + connect/disconnect
    - Middle: button sections (with vertical separators)
    - Bottom: terminal output pane
    """

    def __init__(self):
        super().__init__()

        self.title("SSH Command Console (Template)")
        self.geometry("1100x650")
        self.minsize(900, 550)

        # Thread-safe queue for log messages (background threads -> UI)
        self.log_queue: "queue.Queue[str]" = queue.Queue()

        self.ssh = SSHManager()

        self._build_ui()
        self._start_log_poller()

        # Define your sections + buttons here (drag/drop later)
        self.sections = self._define_sections()
        self._build_button_sections(self.sections)

    # -------------------------
    # UI Construction
    # -------------------------

    def _build_ui(self):
        # Main layout: connection frame, command frame, output frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.connection_frame = ttk.LabelFrame(self, text="SSH Connection")
        self.connection_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        self.connection_frame.columnconfigure(10, weight=1)

        self.commands_frame = ttk.LabelFrame(self, text="Actions")
        self.commands_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=8)

        self.output_frame = ttk.LabelFrame(self, text="Terminal Output")
        self.output_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.output_frame.rowconfigure(0, weight=1)
        self.output_frame.columnconfigure(0, weight=1)

        # ----- Connection inputs -----
        ttk.Label(self.connection_frame, text="Host / IP:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.host_var = tk.StringVar(value="192.168.1.10")
        ttk.Entry(self.connection_frame, textvariable=self.host_var, width=20).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(self.connection_frame, text="Port:").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.port_var = tk.IntVar(value=22)
        ttk.Entry(self.connection_frame, textvariable=self.port_var, width=6).grid(row=0, column=3, padx=6, pady=6)

        ttk.Label(self.connection_frame, text="Username:").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.user_var = tk.StringVar(value="admin")
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

        # ----- Output pane -----
        self.output_text = tk.Text(self.output_frame, wrap="word", height=12)
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

    # -------------------------
    # Define Sections / Buttons
    # -------------------------

    def _define_sections(self) -> List[ButtonSection]:
        """
        Define your sections here.

        Rules:
        - max_buttons is a clear LIMIT per section.
        - each ActionButton has enabled=True/False
        - handler points to a function that executes a command or upload.
        """

        # Example "command strings" you can replace later:
        SHOW_VERSION = "show version"
        SHOW_INTERFACES = "show interfaces"
        REBOOT = "reload"

        return [
            ButtonSection(
                title="Status",
                max_buttons=6,
                actions=[
                    ActionButton("Show Version", enabled=True,
                                 handler=lambda: self.run_ssh_command(SHOW_VERSION),
                                 tooltip="Runs: show version"),
                    ActionButton("Show Interfaces", enabled=True,
                                 handler=lambda: self.run_ssh_command(SHOW_INTERFACES),
                                 tooltip="Runs: show interfaces"),
                    ActionButton("Placeholder A", enabled=False,
                                 handler=lambda: self.run_ssh_command("echo Placeholder A"),
                                 tooltip="Disabled until you set enabled=True"),
                ],
            ),
            ButtonSection(
                title="Maintenance",
                max_buttons=6,
                actions=[
                    ActionButton("Upload Config (Template)", enabled=True,
                                 handler=self.upload_config_template,
                                 tooltip="Opens a file picker and uploads to a remote path"),
                    ActionButton("Reboot Device", enabled=False,
                                 handler=lambda: self.run_ssh_command(REBOOT),
                                 tooltip="Dangerous: enable only when ready"),
                ],
            ),
            ButtonSection(
                title="Custom",
                max_buttons=6,
                actions=[
                    ActionButton("Run Custom Command...", enabled=True,
                                 handler=self.prompt_and_run_custom_command,
                                 tooltip="Prompts you for a command string"),
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

    def on_connect(self):
        host = self.host_var.get().strip()
        port = int(self.port_var.get())
        user = self.user_var.get().strip()
        pw = self.pass_var.get()

        if not host or not user:
            messagebox.showerror("Missing Info", "Please enter Host/IP and Username.")
            return

        self.log(f"Connecting to {host}:{port} as {user}...")

        # Run connect in a thread so UI stays responsive
        def worker():
            try:
                self.ssh.connect(host, port, user, pw)
                self.log("[OK] Connected.")
                self._set_connected_ui(True)
            except Exception as e:
                self.log(f"[ERROR] Connection failed: {e}")
                self._set_connected_ui(False)

        threading.Thread(target=worker, daemon=True).start()

    def on_disconnect(self):
        self.log("Disconnecting...")
        try:
            self.ssh.disconnect()
        finally:
            self._set_connected_ui(False)
            self.log("[OK] Disconnected.")

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
        """
        if not self.ssh.is_connected():
            messagebox.showwarning("Not Connected", "Please connect over SSH first.")
            return

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
        """
        if not self.ssh.is_connected():
            messagebox.showwarning("Not Connected", "Please connect over SSH first.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Run Custom Command")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Command:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        cmd_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=cmd_var, width=60)
        entry.grid(row=0, column=1, padx=10, pady=10)
        entry.focus_set()

        def run_and_close():
            cmd = cmd_var.get().strip()
            if cmd:
                self.run_ssh_command(cmd)
            dialog.destroy()

        ttk.Button(dialog, text="Run", command=run_and_close).grid(row=1, column=1, padx=10, pady=(0, 10), sticky="e")
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

    def upload_config_template(self):
        """
        Template: pick a local file, upload to a remote path.
        You will likely replace remote path rules per device type.
        """
        if not self.ssh.is_connected():
            messagebox.showwarning("Not Connected", "Please connect over SSH first.")
            return

        local_path = filedialog.askopenfilename(title="Select a file to upload")
        if not local_path:
            return

        # Template remote path. Change this later.
        remote_path = "/tmp/uploaded_config.txt"

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


if __name__ == "__main__":
    app = SSHGuiApp()
    app.mainloop()
