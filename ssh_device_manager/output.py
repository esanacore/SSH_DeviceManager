"""Output pane helpers: thread-safe logging, append, clear, copy, save.

This module provides the OutputManager class, which handles all interactions
with the terminal output text widget in a thread-safe manner.
"""

import json
import queue
import time
import tkinter as tk
from datetime import datetime, timezone
from tkinter import filedialog, messagebox
from typing import Optional


STRUCTURED_OUTPUT_FORMAT = "ssh-device-manager-output-v1"


def build_structured_output(text: str, exported_at: Optional[str] = None) -> dict:
    """Builds a stable JSON-serializable output export payload."""
    return {
        "format": STRUCTURED_OUTPUT_FORMAT,
        "exported_at": exported_at or datetime.now(timezone.utc).isoformat(),
        "line_count": len(text.splitlines()),
        "lines": text.splitlines(),
        "text": text,
    }


class OutputManager:
    """Manage the output Text widget and queue logs from worker threads.

    Attributes:
        output_text: The Tkinter Text widget used for output display.
        log_queue: A thread-safe queue for storing log messages.
    """

    def __init__(self, output_text: tk.Text):
        """Initializes the OutputManager.

        Args:
            output_text: The Tkinter Text widget to manage.
        """
        self.output_text = output_text
        self.log_queue: "queue.Queue[str]" = queue.Queue()

    def log(self, text: str):
        """Thread-safe log: background threads can safely call this.

        Args:
            text: The message to log.
        """
        timestamp = time.strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {text}\n")

    def start_poller(self, root: tk.Tk):
        """Starts a background poller to process the log queue.

        The poller runs in the main Tkinter thread to safely update the UI.

        Args:
            root: The root Tkinter window or widget used for scheduling 'after' calls.
        """

        def poll():
            try:
                while True:
                    msg = self.log_queue.get_nowait()
                    self._append(msg)
            except queue.Empty:
                pass
            root.after(80, func=poll)

        poll()

    def _append(self, msg: str):
        """Internal helper to unlock the Text widget and append a message.

        Args:
            msg: The message to append.
        """
        self.output_text.configure(state="normal")
        self.output_text.insert("end", msg)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def append(self, msg: str):
        """Public method to append output text directly.

        Args:
            msg: The message to append.
        """
        self._append(msg)

    def clear(self):
        """Clears all content from the output Text widget."""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")

    def copy(self, root: tk.Tk):
        """Copies all text from the output widget to the system clipboard.

        Args:
            root: The root Tkinter window or widget used for clipboard operations.
        """
        text = self.output_text.get("1.0", "end-1c")
        root.clipboard_clear()
        root.clipboard_append(text)
        self.log("[OK] Output copied to clipboard.")

    def save(self):
        """Opens a file dialog to save the output text to a file."""
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

    def export_json(self):
        """Opens a file dialog to export the output text as structured JSON."""
        text = self.output_text.get("1.0", "end-1c")

        if not text.strip():
            messagebox.showwarning("Empty Output", "Nothing to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(build_structured_output(text), f, indent=2)
                    f.write("\n")
                self.log(f"[OK] Output exported to {file_path}")
            except Exception as e:
                self.log(f"[ERROR] Failed to export output: {e}")
