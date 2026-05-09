"""Connection form validation helpers.

This module provides functions to validate and normalize user inputs
from the connection configuration form.
"""

import tkinter as tk
from tkinter import messagebox
from typing import List, Optional, Tuple


def parse_int_input(
    value: str, label: str, minimum: int = 1, maximum: Optional[int] = None
) -> Optional[int]:
    """Parse and validate integer form input, showing a user-facing error on failure.

    Args:
        value: The raw string value from the entry field.
        label: A descriptive name for the field (e.g., "Port").
        minimum: The minimum allowed integer value. Defaults to 1.
        maximum: The maximum allowed integer value. Defaults to None.

    Returns:
        The parsed integer if valid, otherwise None.
    """
    text = value.strip()
    try:
        parsed = int(text)
    except (TypeError, ValueError):
        messagebox.showerror("Invalid Input", f"{label} must be a whole number.")
        return None

    if parsed < minimum or (maximum is not None and parsed > maximum):
        if maximum is None:
            range_text = f"{minimum}+"
        else:
            range_text = f"{minimum}-{maximum}"
        messagebox.showerror("Invalid Input", f"{label} must be in the range {range_text}.")
        return None

    return parsed


def get_connection_inputs(
    host_var, port_var, user_var, pass_var, timeout_var,
    *, log
) -> Optional[Tuple[str, int, str, str, int]]:
    """Validate the current connection form and return normalized values.

    Each missing or invalid field is reported individually so the user
    knows exactly what to fix.

    Args:
        host_var: Tkinter Variable for the host field.
        port_var: Tkinter Variable for the port field.
        user_var: Tkinter Variable for the username field.
        pass_var: Tkinter Variable for the password field.
        timeout_var: Tkinter Variable for the timeout field.
        log: A callable that accepts a string to log messages.

    Returns:
        A tuple of (host, port, user, password, timeout) if all inputs are valid,
        otherwise None.
    """
    errors: List[str] = []

    host = host_var.get().strip()
    user = user_var.get().strip()
    pw = pass_var.get()

    if not host:
        errors.append("Host / IP is empty.")
    if not user:
        errors.append("Username is empty.")
    if not pw:
        errors.append("Password is empty.")

    # --- Port ---
    port: Optional[int] = None
    try:
        port = int(port_var.get())
    except (TypeError, ValueError, tk.TclError):
        errors.append("Port is empty or not a valid number.")

    if port is not None and (port < 1 or port > 65535):
        errors.append("Port must be between 1 and 65535.")
        port = None

    # --- Timeout ---
    timeout: Optional[int] = None
    try:
        timeout = int(timeout_var.get())
    except (TypeError, ValueError, tk.TclError):
        errors.append("Connection Timeout is empty or not a valid number.")

    if timeout is not None and (timeout < 1 or timeout > 300):
        errors.append("Connection Timeout must be between 1 and 300.")
        timeout = None

    if errors:
        summary = "\n".join(f"  \u2022 {e}" for e in errors)
        log(f"[ERROR] Connection form has problems:\n{summary}")
        messagebox.showerror(
            "Invalid Connection Details",
            "Please fix the following:\n\n" + "\n".join(f"\u2022 {e}" for e in errors),
        )
        return None

    return host, port, user, pw, timeout


def get_host_key_mode(host_key_mode_var) -> str:
    """Normalize and validate the host key verification mode.

    Args:
        host_key_mode_var: Tkinter Variable for the host key mode field.

    Returns:
        The normalized mode string ('strict', 'warning', or 'auto').
        Defaults to 'warning' if the input is invalid.
    """
    mode = host_key_mode_var.get().strip().lower()
    if mode not in {"strict", "warning", "auto"}:
        return "warning"
    return mode
