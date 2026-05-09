"""Application configuration persistence (profiles, settings).

This module handles loading and saving the application's persistent
configuration, including connection profiles.
"""

import json
import os
from typing import Optional


def default_app_config() -> dict:
    """Return the persisted config shape expected by the rest of the app.

    Returns:
        A dictionary with default configuration values (e.g., empty profiles).
    """
    return {"profiles": {}}


def load_app_config(path: str) -> dict:
    """Load app config from a file, returning a sanitized default-compatible dict.

    If the file does not exist or is malformed, a default configuration is
    created and saved.

    Args:
        path: Path to the configuration JSON file.

    Returns:
        A dictionary containing the loaded and sanitized configuration.
    """
    if not os.path.exists(path):
        config = default_app_config()
        save_app_config(path, config)
        return config

    try:
        with open(path, "r", encoding="utf-8") as handle:
            loaded = json.load(handle)
    except (OSError, json.JSONDecodeError):
        config = default_app_config()
        save_app_config(path, config)
        return config

    # Keep only keys the application understands so a malformed file cannot leak
    # unexpected structure into profile handling.
    config = default_app_config()
    if isinstance(loaded, dict):
        profiles = loaded.get("profiles")
        if isinstance(profiles, dict):
            config["profiles"] = profiles
    return config


def save_app_config(path: str, config: dict):
    """Persist the configuration dictionary as JSON to the specified path.

    Args:
        path: Path where the configuration should be saved.
        config: The configuration dictionary to persist.
    """
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
