"""
Data models for the SSH Device Manager UI.

- ActionButton: Represents one button/action in the UI.
- ButtonSection: Represents a vertical group of buttons.
- ToolTip: Minimal tooltip implementation for Tkinter widgets.
"""

import tkinter as tk
from typing import Callable, List


class ActionButton:
    """
    Represents one button/action in the UI.
    - label: text on the button
    - enabled: whether it should appear / be clickable
    - handler: function called when clicked
    - tooltip: optional help text (simple hover tooltip added below)
    """

    def __init__(self, label: str, enabled: bool, handler: Callable[[], None], tooltip: str = ""):
        self.label = label
        self.enabled = enabled
        self.handler = handler
        self.tooltip = tooltip


class ButtonSection:
    """
    Represents a 'section' (a vertical group) of buttons.
    - title: shown at top of section
    - max_buttons: hard limit to keep layout consistent
    - actions: list of ActionButton items
    """

    def __init__(self, title: str, max_buttons: int, actions: List[ActionButton]):
        self.title = title
        self.max_buttons = max_buttons
        self.actions = actions


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
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
        )
        label.pack(ipadx=6, ipady=4)

    def hide_tip(self, _event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None
