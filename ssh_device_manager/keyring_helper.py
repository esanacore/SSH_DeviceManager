"""OS Keyring integration helper.

Provides safe wrapper functions for storing, loading, and deleting SSH
credentials using the operating system's native credential manager (Keyring).
Degrades gracefully when the `keyring` package is missing or when the
underlying OS keyring service is unavailable (e.g., headless environments).
"""

from functools import lru_cache
from typing import Optional

SERVICE_NAME = "SSH_DeviceManager"


@lru_cache(maxsize=None)
def _get_keyring():
    """Dynamically attempt to import the keyring module.

    The import is attempted once and its outcome cached, so a missing or
    broken keyring package costs one failed import rather than one per call.

    Returns:
        The keyring module if available and functional, otherwise None.
    """
    try:
        import keyring  # pylint: disable=import-outside-toplevel
        return keyring
    except ImportError:
        return None


def is_keyring_available() -> bool:
    """Check if the OS keyring library is installed and responsive.

    Returns:
        True if keyring is available, False otherwise.
    """
    kr = _get_keyring()
    if kr is None:
        return False
    try:
        # Test backend access without modifying keyring data
        _ = kr.get_keyring()
        return True
    except Exception:  # pylint: disable=broad-exception-caught
        return False


def get_keyring_password(account_key: str, service: str = SERVICE_NAME) -> Optional[str]:
    """Retrieve a stored password from the OS keyring.

    Args:
        account_key: Unique identifier for the entry (e.g. "username@host" or profile name).
        service: Service namespace for the keyring. Defaults to SERVICE_NAME.

    Returns:
        The stored password string if found, otherwise None.
    """
    kr = _get_keyring()
    if not kr or not account_key:
        return None
    try:
        return kr.get_password(service, account_key)
    except Exception:  # pylint: disable=broad-exception-caught
        return None


def set_keyring_password(account_key: str, password: str, service: str = SERVICE_NAME) -> bool:
    """Store a password securely in the OS keyring.

    Args:
        account_key: Unique identifier for the entry (e.g. "username@host" or profile name).
        password: Password string to store.
        service: Service namespace for the keyring. Defaults to SERVICE_NAME.

    Returns:
        True if successfully saved, False otherwise.
    """
    kr = _get_keyring()
    if not kr or not account_key:
        return False
    try:
        kr.set_password(service, account_key, password)
        return True
    except Exception:  # pylint: disable=broad-exception-caught
        return False


def delete_keyring_password(account_key: str, service: str = SERVICE_NAME) -> bool:
    """Remove a password entry from the OS keyring.

    Args:
        account_key: Unique identifier for the entry.
        service: Service namespace for the keyring. Defaults to SERVICE_NAME.

    Returns:
        True if successfully deleted, False otherwise.
    """
    kr = _get_keyring()
    if not kr or not account_key:
        return False
    try:
        kr.delete_password(service, account_key)
        return True
    except Exception:  # pylint: disable=broad-exception-caught
        return False
