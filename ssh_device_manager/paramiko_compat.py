"""Compatibility import for environments without paramiko installed."""

try:
    import paramiko as _paramiko
except ModuleNotFoundError:
    class _MissingHostKeyPolicy:
        pass

    class _SSHClient:
        def load_system_host_keys(self):
            pass

        def set_missing_host_key_policy(self, _policy):
            pass

        def connect(self, *args, **kwargs):
            raise ModuleNotFoundError("paramiko is required for SSH connections")

        def get_transport(self):
            return None

        def exec_command(self, *args, **kwargs):
            raise ModuleNotFoundError("paramiko is required for SSH connections")

        def open_sftp(self):
            raise ModuleNotFoundError("paramiko is required for SFTP transfers")

        def close(self):
            pass

    class _SFTPClient:
        def put(self, *args, **kwargs):
            raise ModuleNotFoundError("paramiko is required for SFTP transfers")

        def close(self):
            pass

    class _AuthenticationException(Exception):
        pass

    class _SSHException(Exception):
        pass

    class _ParamikoFallback:
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
