"""Loads button section definitions from a JSON file.

This module provides the logic for parsing a JSON configuration file
into ButtonSection and ActionButton objects, which are then used to
populate the application's Actions panel.
"""

import json
import os
from typing import Callable, List

from .models import ActionButton, ButtonSection


def load_sections_from_file(
    path: str,
    *,
    log: Callable[[str], None],
    run_ssh_command: Callable[[str], None],
    upload_config_template: Callable[[], None],
    send_file_scp: Callable[[], None],
    prompt_and_run_custom_command: Callable[[], None],
    fallback: Callable[[], List[ButtonSection]],
) -> List[ButtonSection]:
    """Load section/button definitions from a JSON file.

    Handler callbacks are injected so this module has no dependency on the
    main application class. If the file is missing or malformed, the
    fallback function is called.

    Args:
        path: Path to the JSON sections file.
        log: Callable for logging messages.
        run_ssh_command: Callable for executing an SSH command.
        upload_config_template: Callable for the upload template workflow.
        send_file_scp: Callable for the SCP file transfer workflow.
        prompt_and_run_custom_command: Callable for the custom command dialog.
        fallback: Callable that returns a default list of ButtonSections.

    Returns:
        A list of loaded ButtonSection objects, or the results of fallback().
    """

    def resolve_handler(cmd: str) -> Callable[[], None]:
        """Map JSON command tokens to callables the Tk button can invoke.

        Args:
            cmd: The command string or reserved token from the JSON.

        Returns:
            A callable that performs the requested action.
        """
        if not cmd:
            return lambda: log("[WARN] No command assigned to this button.")

        # These reserved tokens call UI flows instead of raw SSH commands.
        if cmd == "__upload_template__":
            return upload_config_template
        if cmd == "__send_file__":
            return send_file_scp
        if cmd == "__custom_command__":
            return prompt_and_run_custom_command

        if cmd.startswith("run:"):
            command_text = cmd.split(":", 1)[1]
            return lambda c=command_text: run_ssh_command(c)

        return lambda c=cmd: run_ssh_command(c)

    try:
        if not os.path.exists(path):
            log(f"[INFO] Sections file '{path}' not found. Using built-in sections.")
            return fallback()

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
            log("[WARN] Sections file parsed but contained no sections. Using built-in sections.")
            return fallback()

        log(f"[OK] Loaded sections from '{path}'.")
        return sections

    except Exception as e:
        log(f"[ERROR] Failed to load sections from '{path}': {e}")
        return fallback()
