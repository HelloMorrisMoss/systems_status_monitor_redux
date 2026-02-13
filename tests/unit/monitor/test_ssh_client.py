from unittest.mock import MagicMock, patch
from systems_status_monitor_redux.monitor.ssh_client import SSHClientWrapper
from systems_status_monitor_redux.models.entities import FailureCategory
import paramiko
import socket

def test_ssh_client_connect_success():
    with patch("paramiko.SSHClient") as mock_ssh:
        client_instance = mock_ssh.return_value
        client_instance.connect.return_value = None
        
        wrapper = SSHClientWrapper("1.2.3.4", "user", "pass")
        success, category, msg = wrapper.connect()
        
        assert success is True
        assert category is None
        client_instance.connect.assert_called_once()

def test_ssh_client_connect_auth_failed():
    with patch("paramiko.SSHClient") as mock_ssh:
        client_instance = mock_ssh.return_value
        client_instance.connect.side_effect = paramiko.AuthenticationException("Auth failed")
        
        wrapper = SSHClientWrapper("1.2.3.4", "user", "pass")
        success, category, msg = wrapper.connect()
        
        assert success is False
        assert category == FailureCategory.AUTH_FAILED

def test_ssh_client_connect_timeout():
    with patch("paramiko.SSHClient") as mock_ssh:
        client_instance = mock_ssh.return_value
        client_instance.connect.side_effect = socket.timeout("timed out")
        
        wrapper = SSHClientWrapper("1.2.3.4", "user", "pass")
        success, category, msg = wrapper.connect()
        
        assert success is False
        assert category == FailureCategory.TIMEOUT

def test_ssh_client_execute():
    with patch("paramiko.SSHClient") as mock_ssh:
        client_instance = mock_ssh.return_value
        wrapper = SSHClientWrapper("1.2.3.4", "user", "pass")
        wrapper.client = client_instance
        
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"output"
        mock_stdout.channel.recv_exit_status.return_value = 0
        
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""
        
        client_instance.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        exit_status, stdout, stderr = wrapper.execute("echo test")
        
        assert exit_status == 0
        assert stdout == "output"
        assert stderr == ""
