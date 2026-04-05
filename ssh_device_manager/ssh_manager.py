"""
SSH Manager - Wraps Paramiko for SSH connections, command execution, and file transfers.
"""

from contextlib import suppress
from typing import Optional

import paramiko


class SSHManager:
    """
    Wraps Paramiko SSHClient with:
    - connect / disconnect
    - run_command
    - upload_file (SFTP)
    """

    def __init__(self):
        self.client: Optional[paramiko.SSHClient] = None
        self.sftp: Optional[paramiko.SFTPClient] = None
        self.host_key: Optional[str] = None

    def is_connected(self) -> bool:
        if not self.client:
            return False

        transport = self.client.get_transport()
        is_active = bool(transport and transport.is_active())
        if not is_active:
            self.disconnect()
        return is_active

    def connect(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        timeout: int = 10,
        host_key_mode: str = "warning",
    ):
        """
        Connect via SSH.

        SECURITY NOTE:
        - RejectPolicy requires the host key to already exist in known_hosts.
        - WarningPolicy warns and then trusts the presented host key.
        - AutoAddPolicy trusts all host keys silently.
        - This template defaults to WarningPolicy so first-use trust is visible.
        """

        if self.client:
            self.disconnect()

        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()

        policies = {
            "strict": paramiko.RejectPolicy,
            "warning": paramiko.WarningPolicy,
            "auto": paramiko.AutoAddPolicy,
        }
        policy_cls = policies.get(host_key_mode, paramiko.WarningPolicy)
        ssh.set_missing_host_key_policy(policy_cls())
        ssh.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=timeout,
            allow_agent=False,
            look_for_keys=False,
        )

        self.client = ssh
        self.host_key = host
        self.sftp = None

    def disconnect(self):
        """Close SSH and SFTP connections, clear sensitive data."""
        with suppress(OSError, paramiko.SSHException):
            if self.sftp:
                self.sftp.close()

        with suppress(OSError, paramiko.SSHException):
            if self.client:
                self.client.close()

        self.client = None
        self.sftp = None
        self.host_key = None

    def run_command(self, command: str, timeout: int = 30) -> str:
        if not self.client:
            raise RuntimeError("Not connected")

        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        combined = out + (("\n" + err) if err.strip() else "")
        return combined

    def upload_file(self, local_path: str, remote_path: str):
        if not self.client:
            raise RuntimeError("Not connected")

        if not self.sftp:
            self.sftp = self.client.open_sftp()

        self.sftp.put(local_path, remote_path)
