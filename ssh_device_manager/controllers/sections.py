"""Section loading and Actions-panel orchestration.

This module contains the SectionsController which manages the loading,
reloading, and UI rendering of button sections.
"""

import os
from tkinter import filedialog, ttk

from .. import sections_loader
from ..models import ActionButton, ButtonSection, ToolTip


class SectionsController:
    """Owns section definitions, loading, rendering, and file watching.

    Attributes:
        app: The main application instance (SSHGuiApp).
    """

    def __init__(self, app):
        """Initializes the SectionsController.

        Args:
            app: The main application instance.
        """
        self.app = app

    def load_sections_from_file(self, path: str):
        """Loads button section definitions from a JSON file.

        Args:
            path: Path to the JSON sections file.

        Returns:
            A list of ButtonSection objects.
        """
        return sections_loader.load_sections_from_file(
            path,
            log=self.app.log,
            run_ssh_command=self.app.run_ssh_command,
            upload_config_template=self.app.upload_config_template,
            send_file_scp=self.app.send_file_scp,
            prompt_and_run_custom_command=self.app.prompt_and_run_custom_command,
            fallback=self.define_sections,
        )

    def reload_sections(self, path: str):
        """Reloads sections from a file and rebuilds the Actions panel.

        Args:
            path: Path to the JSON sections file.
        """
        self.app.sections_path = path
        self.app.log(f"Reloading sections from '{path}'...")
        self.app.sections = self.load_sections_from_file(path)
        self.build_button_sections(self.app.sections)
        self.app._sections_mtime = self.get_mtime(self.app.sections_path)
        self.app.log("[OK] Sections reloaded.")

    def open_sections_file(self, default_path: str):
        """Opens a file picker to select and load a sections file.

        Args:
            default_path: The initial file path to show in the picker.
        """
        path = filedialog.askopenfilename(
            initialfile=default_path,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            self.reload_sections(path)

    def define_sections(self):
        """Returns the default/fallback button sections for the UI.

        Returns:
            A list of hardcoded ButtonSection objects.
        """
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
                        handler=lambda: self.app.run_ssh_command(show_version),
                        tooltip="Runs: show version",
                    ),
                    ActionButton(
                        "Show Interfaces",
                        enabled=True,
                        handler=lambda: self.app.run_ssh_command(show_interfaces),
                        tooltip="Runs: show interfaces",
                    ),
                    ActionButton(
                        "Placeholder A",
                        enabled=False,
                        handler=lambda: self.app.run_ssh_command("echo Placeholder A"),
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
                        handler=self.app.upload_config_template,
                        tooltip="Opens a file picker and uploads to a remote path",
                    ),
                    ActionButton(
                        "Send File via SCP",
                        enabled=True,
                        handler=self.app.send_file_scp,
                        tooltip="Send a file to the remote server via SCP",
                    ),
                    ActionButton(
                        "Reboot Device",
                        enabled=False,
                        handler=lambda: self.app.run_ssh_command(reboot),
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
                        handler=self.app.prompt_and_run_custom_command,
                        tooltip="Prompts you for a command string",
                    ),
                ],
            ),
        ]

    def build_button_sections(self, sections):
        """Constructs the UI widgets for the provided button sections.

        Args:
            sections: A list of ButtonSection objects to render.
        """
        for child in self.app.commands_frame.winfo_children():
            child.destroy()

        container = ttk.Frame(self.app.commands_frame)
        container.pack(fill="x", padx=8, pady=8)

        total_columns = len(sections) * 2 - 1
        for index in range(total_columns):
            if index % 2 == 0:
                container.columnconfigure(index, weight=1, uniform="section")
            else:
                container.columnconfigure(index, weight=0)

        for index, section in enumerate(sections):
            sec_frame = ttk.Frame(container, padding=(6, 2))
            sec_frame.grid(row=0, column=index * 2, sticky="nsew")

            ttk.Label(
                sec_frame,
                text=section.title,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w", pady=(0, 6))

            enabled_actions = [action for action in section.actions if action.enabled]
            if len(enabled_actions) > section.max_buttons:
                self.app.log(
                    f"[WARN] Section '{section.title}' exceeds max_buttons={section.max_buttons}. Truncating."
                )
                enabled_actions = enabled_actions[: section.max_buttons]

            for action in enabled_actions:
                btn = ttk.Button(
                    sec_frame,
                    text=action.label,
                    command=action.handler,
                    width=24,
                )
                btn.pack(fill="x", pady=3)
                ToolTip(btn, action.tooltip)

            if index < len(sections) - 1:
                sep = ttk.Separator(container, orient="vertical")
                sep.grid(row=0, column=index * 2 + 1, sticky="ns", padx=10)
                container.grid_rowconfigure(0, weight=1)

    def get_mtime(self, path: str):
        """Returns the modification time of a file.

        Args:
            path: Path to the file.

        Returns:
            The modification time as a float, or None if the file is missing or inaccessible.
        """
        try:
            return os.path.getmtime(path)
        except Exception:
            return None

    def start_sections_watcher(self, interval_ms: int = 1000):
        """Starts a background poller to watch for changes in the sections file.

        Args:
            interval_ms: Polling interval in milliseconds. Defaults to 1000.
        """
        def check():
            try:
                current = self.get_mtime(self.app.sections_path)
                if current != getattr(self.app, "_sections_mtime", None):
                    self.app.log(
                        f"[INFO] Detected change in sections file '{self.app.sections_path}', reloading..."
                    )
                    self.reload_sections(self.app.sections_path)
            except Exception as exc:
                self.app.log(f"[WARN] sections watcher error: {exc}")
            finally:
                self.app.after(interval_ms, check)

        self.app.after(interval_ms, check)
