"""Connection-related UI orchestration."""

import threading
from tkinter import messagebox

from ..paramiko_compat import paramiko
from ..ssh_manager import SSHManager


class ConnectionController:
    """Owns connection lifecycle, state refresh, and connection-related UI updates."""

    def __init__(self, app):
        self.app = app

    def on_host_selected(self, _event):
        if self.app.host_var.get() == "<Clear History>":
            self.app.host_history.clear()
            self.app.host_combo["values"] = []
            self.app.host_var.set("")
            self.app.log("[INFO] Host history cleared.")

    def refresh_connection_state(self, *, notify_on_drop: bool = False):
        connected = self.app.ssh.is_connected()
        was_connecting = self.app.is_connecting
        self.app._set_connected_ui(connected)
        if notify_on_drop and not connected and not was_connecting:
            self.app.log("[WARN] SSH session is no longer active.")

    def start_connection_monitor(self):
        def poll():
            was_connected = self.app.status_var.get() == "Connected"
            self.refresh_connection_state(notify_on_drop=was_connected)
            self.app.after(1500, poll)

        self.app.after(1500, poll)

    def connect(self):
        inputs = self.app._get_connection_inputs()
        if inputs is None:
            return
        host, port, user, pw, timeout = inputs

        if self.app.is_connecting:
            messagebox.showwarning("In Progress", "Connection attempt already in progress.")
            return

        if host not in self.app.host_history:
            self.app.host_history.insert(0, host)
            if len(self.app.host_history) > 10:
                self.app.host_history.pop()
            self.app.host_combo["values"] = self.app.host_history + ["<Clear History>"]

        host_key_mode = self.app._get_host_key_mode()
        self.app.log(f"Connecting to {host}:{port} as {user}...")
        self.app.is_connecting = True

        def worker():
            try:
                self.app.ssh.connect(
                    host,
                    port,
                    user,
                    pw,
                    timeout=timeout,
                    host_key_mode=host_key_mode,
                )
                self.app.log("[OK] Connected.")
                self.app.log(f"[INFO] Host key policy: {host_key_mode}.")
                self.app._set_connected_ui(True)
            except paramiko.AuthenticationException:
                self.app.log(
                    f"[ERROR] Authentication failed for '{user}@{host}:{port}'.\n"
                    f"  \u2022 Double-check your Username and Password.\n"
                    f"  \u2022 The server may not allow password authentication."
                )
                self.app._set_connected_ui(False)
            except paramiko.SSHException as exc:
                self.app.log(
                    f"[ERROR] SSH error while connecting to {host}:{port}:\n"
                    f"  \u2022 {exc}\n"
                    f"  \u2022 Verify the host is reachable and running an SSH server."
                )
                self.app._set_connected_ui(False)
            except OSError as exc:
                self.app.log(
                    f"[ERROR] Network error connecting to {host}:{port}:\n"
                    f"  \u2022 {exc}\n"
                    f"  \u2022 Check the Host/IP and Port, and that the device is online."
                )
                self.app._set_connected_ui(False)
            except Exception as exc:
                self.app.log(f"[ERROR] Connection failed: {exc}")
                self.app._set_connected_ui(False)
            finally:
                self.app.is_connecting = False

        threading.Thread(target=worker, daemon=True).start()

    def disconnect(self):
        self.app.log("Disconnecting...")
        try:
            self.app.ssh.disconnect()
        finally:
            if self.app.clear_creds_var.get():
                self.app.pass_var.set("")
                self.app.log("[INFO] Credentials cleared.")
            self.app._set_connected_ui(False)
            self.app.log("[OK] Disconnected.")

    def test_connection(self):
        self.refresh_connection_state()
        if self.app.ssh.is_connected():
            messagebox.showinfo("Connected", "Already connected to SSH server.")
            return

        inputs = self.app._get_connection_inputs()
        if inputs is None:
            return
        host, port, user, pw, timeout = inputs
        host_key_mode = self.app._get_host_key_mode()

        self.app.log("Testing connection...")

        def worker():
            try:
                temp_ssh = self.app._create_temp_ssh_manager()
                temp_ssh.connect(
                    host,
                    port,
                    user,
                    pw,
                    timeout=timeout,
                    host_key_mode=host_key_mode,
                )
                self.app.log("[OK] Connection test successful.")
                self.app.log(f"[INFO] Host key policy: {host_key_mode}.")
                temp_ssh.disconnect()
            except paramiko.AuthenticationException:
                self.app.log(
                    f"[ERROR] Test failed \u2014 authentication rejected for '{user}@{host}:{port}'.\n"
                    f"  \u2022 Double-check your Username and Password."
                )
            except paramiko.SSHException as exc:
                self.app.log(
                    f"[ERROR] Test failed \u2014 SSH error: {exc}\n"
                    f"  \u2022 Verify the host is reachable and running an SSH server."
                )
            except OSError as exc:
                self.app.log(
                    f"[ERROR] Test failed \u2014 network error: {exc}\n"
                    f"  \u2022 Check the Host/IP and Port, and that the device is online."
                )
            except Exception as exc:
                self.app.log(f"[ERROR] Connection test failed: {exc}")

        threading.Thread(target=worker, daemon=True).start()
