import paramiko
import logging
import socket
from typing import Tuple, Optional
from src.models.entities import FailureCategory

logger = logging.getLogger(__name__)

class SSHClientWrapper:
    def __init__(self, host: str, username: str, password: str, timeout: int = 10):
        self.host = host
        self.username = username
        self.password = password
        self.timeout = timeout
        self.client: Optional[paramiko.SSHClient] = None

    def connect(self) -> Tuple[bool, Optional[FailureCategory], str]:
        """
        Connect to the remote host.
        Returns: (success, failure_category, error_message)
        """
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Redact password in logs if needed, but here we just log host
            logger.info(f"Connecting to {self.host} as {self.username}")
            self.client.connect(
                hostname=self.host,
                username=self.username,
                password=self.password,
                timeout=self.timeout,
                allow_agent=False,
                look_for_keys=False
            )
            return True, None, ""
        except paramiko.AuthenticationException:
            logger.error(f"Authentication failed for {self.host}")
            return False, FailureCategory.AUTH_FAILED, "Authentication failed"
        except (paramiko.SSHException, socket.timeout, socket.error) as e:
            error_str = str(e)
            if "timed out" in error_str.lower():
                logger.error(f"Connection timeout for {self.host}")
                return False, FailureCategory.TIMEOUT, "Connection timed out"
            logger.error(f"Connection failed for {self.host}: {error_str}")
            return False, FailureCategory.UNREACHABLE, f"Connection failed: {error_str}"
        except Exception as e:
            logger.error(f"Unexpected error connecting to {self.host}: {str(e)}")
            return False, FailureCategory.CHECK_FAILED, f"Unexpected error: {str(e)}"

    def execute(self, command: str) -> Tuple[int, str, str]:
        """
        Execute a command and return (exit_status, stdout, stderr).
        """
        if not self.client:
            raise RuntimeError("SSH client not connected")

        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=self.timeout)
            exit_status = stdout.channel.recv_exit_status()
            return exit_status, stdout.read().decode('utf-8', errors='replace'), stderr.read().decode('utf-8', errors='replace')
        except Exception as e:
            logger.error(f"Error executing command '{command}' on {self.host}: {str(e)}")
            return -1, "", str(e)

    def close(self):
        if self.client:
            self.client.close()
            self.client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
