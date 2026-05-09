"""Action-related UI orchestration."""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ..constants import COMMAND_HISTORY_LIMIT


class ActionController:
    """Owns SSH command execution and file-transfer flows."""

    def __init__(self, app):
        self.app = app

    def run_ssh_command(self, command: str):
        self.app._refresh_connection_state()
        if not self.app.ssh.is_connected():
            messagebox.showwarning("Not Connected", "Please connect over SSH first.")
            return

        if command in self.app.command_history:
            self.app.command_history.remove(command)
        self.app.command_history.insert(0, command)
        if len(self.app.command_history) > COMMAND_HISTORY_LIMIT:
            self.app.command_history.pop()

        self.app.history_index = 0
        self.app.log(f"\n$ {command}")

        def worker():
            try:
                output = self.app.ssh.run_command(command)
                self.app.log(output.strip() if output.strip() else "(no output)")
            except Exception as exc:
                self.app.log(f"[ERROR] Command failed: {exc}")

        threading.Thread(target=worker, daemon=True).start()

    def prompt_and_run_custom_command(self):
        if not self.app.ssh.is_connected():
            messagebox.showwarning("Not Connected", "Please connect over SSH first.")
            return

        dialog = tk.Toplevel(self.app)
        dialog.title("Run Custom Command")
        dialog.transient(self.app)
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
            if not self.app.command_history:
                return
            current_index = history_state["index"]
            if current_index == -1:
                history_state["draft"] = cmd_var.get()
            if direction < 0:
                new_index = min(len(self.app.command_history) - 1, current_index + 1)
            else:
                new_index = current_index - 1
            history_state["index"] = new_index
            if new_index == -1:
                cmd_var.set(history_state["draft"])
            else:
                cmd_var.set(self.app.command_history[new_index])
            entry.icursor("end")

        def on_key(event):
            if event.keysym == "Up":
                navigate_history(-1)
                return "break"
            if event.keysym == "Down":
                navigate_history(1)
                return "break"
            if event.keysym == "Return":
                run_and_close()
                return "break"
            if event.keysym == "Escape":
                dialog.destroy()
                return "break"
            return None

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

        ttk.Button(dialog, text="Run", command=run_and_close).grid(
            row=1, column=1, padx=10, pady=(0, 10), sticky="e"
        )
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(
            row=1, column=0, padx=10, pady=(0, 10), sticky="w"
        )

    def upload_config_template(self, remote_path: str = "/tmp/uploaded_config.txt"):
        self.app._refresh_connection_state()
        if not self.app.ssh.is_connected():
            messagebox.showwarning("Not Connected", "Please connect over SSH first.")
            return

        local_path = filedialog.askopenfilename(title="Select a file to upload")
        if not local_path:
            return

        self.app.log(f"Uploading:\n  local:  {local_path}\n  remote: {remote_path}")

        def worker():
            try:
                self.app.ssh.upload_file(local_path, remote_path)
                self.app.log("[OK] Upload complete.")
            except Exception as exc:
                self.app.log(f"[ERROR] Upload failed: {exc}")

        threading.Thread(target=worker, daemon=True).start()

    def send_file_scp(self):
        if not self.app.ssh.is_connected():
            messagebox.showwarning("Not Connected", "Please connect over SSH first.")
            return

        local_path = filedialog.askopenfilename(title="Select a file to send")
        if not local_path:
            return

        dialog = tk.Toplevel(self.app)
        dialog.title("Remote Destination")
        dialog.transient(self.app)
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
                self.perform_upload(local_path, remote_path)

        tk.Button(dialog, text="Upload", command=on_confirm).pack(pady=10)

    def perform_upload(self, local_path: str, remote_path: str):
        self.app.log(f"SCP Upload:\n  local:  {local_path}\n  remote: {remote_path}")

        def worker():
            try:
                self.app.ssh.upload_file(local_path, remote_path)
                self.app.log("[OK] SCP Upload complete.")
            except Exception as exc:
                self.app.log(f"[ERROR] SCP Upload failed: {exc}")

        threading.Thread(target=worker, daemon=True).start()
