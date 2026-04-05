"""
Application configuration persistence (profiles, settings).
"""

import json
import os
from typing import Optional


def default_app_config() -> dict:
    return {"profiles": {}}


def load_app_config(path: str) -> dict:
    """Load app config from *path*, returning defaults on any error."""
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
