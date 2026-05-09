"""Data models for the SSH Device Manager UI.

Contains classes representing UI components such as buttons and tooltips.
"""

import tkinter as tk
from typing import Callable, List


class ActionButton:
    """Represents one action rendered as a button in an Actions section.

    The handler is already resolved to a callable by the sections loader or the
    fallback section builder, so rendering code does not need to know whether an
    action came from JSON or from built-in defaults.

    Attributes:
        label: Text displayed on the button.
        enabled: Whether the button should appear and be clickable.
        handler: Function called when the button is clicked.
        tooltip: Optional help text to display on hover.
    """

    def __init__(self, label: str, enabled: bool, handler: Callable[[], None], tooltip: str = ""):
        """Initializes the ActionButton.

        Args:
            label: Text displayed on the button.
            enabled: Whether the button should appear and be clickable.
            handler: Function called when the button is clicked.
            tooltip: Optional help text to display on hover. Defaults to "".
        """
        self.label = label
        self.enabled = enabled
        self.handler = handler
        self.tooltip = tooltip


class ButtonSection:
    """Represents a 'section' (a vertical group) of buttons.

    Attributes:
        title: The title shown at the top of the section.
        max_buttons: The hard limit of buttons to keep layout consistent.
        actions: A list of ActionButton items in the section.
    """

    def __init__(self, title: str, max_buttons: int, actions: List[ActionButton]):
        """Initializes the ButtonSection.

        Args:
            title: The title shown at the top of the section.
            max_buttons: The hard limit of buttons to keep layout consistent.
            actions: A list of ActionButton items in the section.
        """
        self.title = title
        self.max_buttons = max_buttons
        self.actions = actions


class ToolTip:
    """Minimal tooltip implementation for Tkinter widgets.

    Attributes:
        widget: The Tkinter widget this tooltip is attached to.
        text: The text to display in the tooltip.
        tipwindow: The top-level window containing the tooltip.
    """

    def __init__(self, widget, text: str):
        """Initializes the ToolTip.

        Args:
            widget: The Tkinter widget this tooltip is attached to.
            text: The text to display in the tooltip.
        """
        self.widget = widget
        self.text = text
        self.tipwindow = None

        if text:
            widget.bind("<Enter>", self.show_tip)
            widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, _event=None):
        """Shows the tooltip if it is not already visible and has text.

        Args:
            _event: The Tkinter event that triggered the tooltip. Defaults to None.
        """
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
        """Hides the tooltip if it is currently visible.

        Args:
            _event: The Tkinter event that triggered the hiding. Defaults to None.
        """
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None
