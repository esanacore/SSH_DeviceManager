"""
Application configuration persistence (profiles, settings).
"""

import json
import os
from typing import Optional


def default_app_config() -> dict:
    """Return the persisted config shape expected by the rest of the app."""
    return {"profiles": {}}


def load_app_config(path: str) -> dict:
    """Load app config from *path*, returning a sanitized default-compatible dict."""
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
    """Persist *config* as JSON to *path*."""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
