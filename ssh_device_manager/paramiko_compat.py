"""Compatibility import for environments without paramiko installed.

This module allows tests and non-SSH workflows to import the package
without requiring Paramiko to be installed. Actual SSH operations will
fail with clear ModuleNotFoundError exceptions until the dependency is
installed.
"""

try:
    import paramiko as _paramiko
except ModuleNotFoundError:
    # Mirror the small subset of Paramiko symbols the app imports so modules can
    # load in test environments that do not install optional SSH dependencies.
    class _MissingHostKeyPolicy:
        """Mock host key policy for environments without Paramiko."""

    class _SSHClient:
        """Mock SSHClient for environments without Paramiko."""
        def load_system_host_keys(self):
            """Mock loading host keys."""
            return None

        def set_missing_host_key_policy(self, _policy):
            """Mock setting host key policy."""
            return None

        def connect(self, *args, **kwargs):
            """Raises ModuleNotFoundError if connection is attempted."""
            raise ModuleNotFoundError("paramiko is required for SSH connections")

        def get_transport(self):
            """Mock getting transport."""
            return None

        def exec_command(self, *args, **kwargs):
            """Raises ModuleNotFoundError if command execution is attempted."""
            raise ModuleNotFoundError("paramiko is required for SSH connections")

        def open_sftp(self):
            """Raises ModuleNotFoundError if SFTP is attempted."""
            raise ModuleNotFoundError("paramiko is required for SFTP transfers")

        def close(self):
            """Mock closing client."""
            return None

    class _SFTPClient:
        """Mock SFTPClient for environments without Paramiko."""
        def put(self, *args, **kwargs):
            """Raises ModuleNotFoundError if file upload is attempted."""
            raise ModuleNotFoundError("paramiko is required for SFTP transfers")

        def close(self):
            """Mock closing SFTP client."""
            return None

    class _AuthenticationException(Exception):
        """Mock AuthenticationException."""

    class _SSHException(Exception):
        """Mock SSHException."""

    class _ParamikoFallback:
        """Container for mock Paramiko classes."""
        SSHClient = _SSHClient
        SFTPClient = _SFTPClient
        AuthenticationException = _AuthenticationException
        SSHException = _SSHException
        RejectPolicy = _MissingHostKeyPolicy
        WarningPolicy = _MissingHostKeyPolicy
        AutoAddPolicy = _MissingHostKeyPolicy

    _paramiko = _ParamikoFallback()

paramiko = _paramiko

__all__ = ["paramiko"]
