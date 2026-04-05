"""
Loads button section definitions from a JSON file.
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
    """
    Loads section/button definitions from a JSON file.

    Handler callbacks are injected so this module has no dependency on the app class.
    Returns *fallback()* on any error.
    """

    def resolve_handler(cmd: str) -> Callable[[], None]:
        if not cmd:
            return lambda: log("[WARN] No command assigned to this button.")

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
