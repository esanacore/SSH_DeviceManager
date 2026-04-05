"""
Output pane helpers: thread-safe logging, append, clear, copy, save.
"""

import queue
import time
import tkinter as tk
from tkinter import filedialog, messagebox


class OutputManager:
    """Manages the terminal output Text widget and thread-safe log queue."""

    def __init__(self, output_text: tk.Text):
        self.output_text = output_text
        self.log_queue: "queue.Queue[str]" = queue.Queue()

    def log(self, text: str):
        """Thread-safe log: background threads can call this."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {text}\n")

    def start_poller(self, root: tk.Tk):
        """Poll the queue every 80ms and append output in the Tk thread."""

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
        self.output_text.configure(state="normal")
        self.output_text.insert("end", msg)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def clear(self):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")

    def copy(self, root: tk.Tk):
        text = self.output_text.get("1.0", "end-1c")
        root.clipboard_clear()
        root.clipboard_append(text)
        self.log("[OK] Output copied to clipboard.")

    def save(self):
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
