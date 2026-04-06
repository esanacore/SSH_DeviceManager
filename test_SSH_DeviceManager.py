import json
import os
import unittest
from unittest.mock import MagicMock, patch
import sys
import types

# Create a lightweight tkinter stub module before importing the application
tk = types.ModuleType('tkinter')
ttk = types.ModuleType('tkinter.ttk')
messagebox = types.ModuleType('tkinter.messagebox')
filedialog = types.ModuleType('tkinter.filedialog')

# Simple dummy widget used for many ttk/tk widgets
class DummyWidget:
    def __init__(self, *a, **k):
        self._items = {}
    def pack(self, *a, **k):
        pass
    def grid(self, *a, **k):
        pass
    def configure(self, *a, **k):
        pass
    def bind(self, *a, **k):
        pass
    def insert(self, *a, **k):
        pass
    def delete(self, *a, **k):
        pass
    def see(self, *a, **k):
        pass
    def columnconfigure(self, *a, **k):
        pass
    def rowconfigure(self, *a, **k):
        pass
    def pack_forget(self, *a, **k):
        pass
    def winfo_children(self, *a, **k):
        return []
    def yview(self, *a, **k):
        pass
    def get(self, *a, **k):
        return ""
    def set(self, *a, **k):
        pass
    def grid_rowconfigure(self, *a, **k):
        pass
    def __setitem__(self, key, value):
        self._items[key] = value
    def __getitem__(self, key):
        return self._items.get(key)

# Ensure tkinter TclError exists on the stub
setattr(tk, 'TclError', Exception)

# Update DummyTkBase to have a .tk attribute providing a .call() method used by the app
class DummyTkBase:
    def __init__(self, *a, **k):
        # Provide a minimal 'tk' attribute with a 'call' method used in SSHGuiApp
        class _TK:
            @staticmethod
            def call(*args, **kwargs):
                # Return a non-'x11' windowing system to avoid X11-specific code path
                return 'win32'
        self.tk = _TK()
        # clipboard methods expected to be MagicMocks in tests
        self.clipboard_clear = MagicMock()
        self.clipboard_append = MagicMock()
    def title(self, *a, **k):
        pass
    def geometry(self, *a, **k):
        pass
    def minsize(self, *a, **k):
        pass
    def config(self, *a, **k):
        pass
    def configure(self, *a, **k):
        return self.config(*a, **k)
    def columnconfigure(self, *a, **k):
        pass
    def rowconfigure(self, *a, **k):
        pass
    def after(self, *a, **k):
        pass
    def after_idle(self, *a, **k):
        pass
    def mainloop(self, *a, **k):
        pass

# StringVar/IntVar/BooleanVar should be MagicMocks so tests can set .get.return_value
tk.Tk = DummyTkBase
tk.Toplevel = DummyWidget
tk.Label = DummyWidget
tk.Frame = DummyWidget
tk.Text = DummyWidget
tk.StringVar = lambda *a, **k: MagicMock()
tk.IntVar = lambda *a, **k: MagicMock()
tk.BooleanVar = lambda *a, **k: MagicMock()

# Minimal ttk
setattr(ttk, 'Frame', lambda *a, **k: DummyWidget())
setattr(ttk, 'Button', lambda *a, **k: DummyWidget())
setattr(ttk, 'Label', lambda *a, **k: DummyWidget())
setattr(ttk, 'LabelFrame', lambda *a, **k: DummyWidget())
setattr(ttk, 'Entry', lambda *a, **k: DummyWidget())
setattr(ttk, 'Scrollbar', lambda *a, **k: DummyWidget())
setattr(ttk, 'Separator', lambda *a, **k: DummyWidget())
setattr(ttk, 'Combobox', lambda *a, **k: DummyWidget())
setattr(ttk, 'Spinbox', lambda *a, **k: DummyWidget())
setattr(ttk, 'Checkbutton', lambda *a, **k: DummyWidget())

class DummyStyle:
    def __init__(self, *a, **k):
        pass
    def theme_use(self, *a, **k):
        pass
    def configure(self, *a, **k):
        pass
    def map(self, *a, **k):
        pass

setattr(ttk, 'Style', lambda *a, **k: DummyStyle())

# messagebox/filedialog functions
messagebox.showinfo = lambda *a, **k: None
messagebox.showerror = lambda *a, **k: None
messagebox.showwarning = lambda *a, **k: None
messagebox.askyesno = lambda *a, **k: False

# Make filedialog functions assignable in tests
filedialog.askopenfilename = MagicMock(return_value='')
filedialog.asksaveasfilename = MagicMock(return_value='')

# Minimal Menu stub for menubar operations
class DummyMenu:
    def __init__(self, *a, **k):
        pass
    def add_cascade(self, *a, **k):
        pass
    def add_command(self, *a, **k):
        pass
    def add_radiobutton(self, *a, **k):
        pass
    def add_separator(self, *a, **k):
        pass

setattr(tk, 'Menu', lambda *a, **k: DummyMenu())

# Re-insert modules in sys.modules
sys.modules['tkinter'] = tk
sys.modules['tkinter.ttk'] = ttk
sys.modules['tkinter.messagebox'] = messagebox
sys.modules['tkinter.filedialog'] = filedialog

# Clear any ssh_device_manager modules that test discovery may have pre-imported
# with the real tkinter (before our mock was set up). This forces a fresh import
# of SSHGuiApp so it inherits from our DummyTkBase mock, not the real tkinter.Tk.
for _key in list(sys.modules.keys()):
    if _key == 'ssh_device_manager' or _key.startswith('ssh_device_manager.') \
            or _key == 'SSH_DeviceManager':
        del sys.modules[_key]

import SSH_DeviceManager

class TestShimExports(unittest.TestCase):
    """Tests that the SSH_DeviceManager.py shim correctly re-exports expected names."""

    def test_expected_exports(self):
        expected_names = [
            "ActionButton", "ButtonSection", "ToolTip",
            "SSHManager", "SSHGuiApp", "THEMES",
            "COMMAND_HISTORY_LIMIT", "APP_CONFIG_FILE", "DEFAULT_SECTIONS_FILE",
            "paramiko", "threading", "filedialog", "messagebox"
        ]
        for name in expected_names:
            self.assertTrue(
                hasattr(SSH_DeviceManager, name),
                f"Expected '{name}' to be exported by SSH_DeviceManager.py shim"
            )

    @patch("SSH_DeviceManager.SSHGuiApp")
    def test_main_execution(self, mock_app):
        SSH_DeviceManager.main()
        mock_app.assert_called_once()
        mock_app.return_value.mainloop.assert_called_once()

class TestDataModels(unittest.TestCase):
    def test_action_button(self):
        handler = MagicMock()
        btn = SSH_DeviceManager.ActionButton("Label", True, handler, "Tooltip")
        self.assertEqual(btn.label, "Label")
        self.assertTrue(btn.enabled)
        self.assertEqual(btn.handler, handler)
        self.assertEqual(btn.tooltip, "Tooltip")

    def test_button_section(self):
        handler = MagicMock()
        btn = SSH_DeviceManager.ActionButton("Label", True, handler)
        section = SSH_DeviceManager.ButtonSection("Title", 5, [btn])
        self.assertEqual(section.title, "Title")
        self.assertEqual(section.max_buttons, 5)
        self.assertEqual(section.actions, [btn])

class TestSSHManager(unittest.TestCase):
    def setUp(self):
        self.ssh_manager = SSH_DeviceManager.SSHManager()

    def test_is_connected_no_client(self):
        self.assertFalse(self.ssh_manager.is_connected())

    def test_is_connected_active_transport(self):
        mock_client = MagicMock()
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        mock_client.get_transport.return_value = mock_transport
        self.ssh_manager.client = mock_client
        self.assertTrue(self.ssh_manager.is_connected())

    def test_is_connected_dead_transport(self):
        mock_client = MagicMock()
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = False
        mock_client.get_transport.return_value = mock_transport
        self.ssh_manager.client = mock_client
        self.assertFalse(self.ssh_manager.is_connected())
        # Should have cleaned up
        self.assertIsNone(self.ssh_manager.client)

    def test_is_connected_no_transport(self):
        mock_client = MagicMock()
        mock_client.get_transport.return_value = None
        self.ssh_manager.client = mock_client
        self.assertFalse(self.ssh_manager.is_connected())
        self.assertIsNone(self.ssh_manager.client)

    @patch('SSH_DeviceManager.paramiko.SSHClient')
    def test_connect(self, mock_ssh_client):
        mock_client_instance = mock_ssh_client.return_value
        
        self.ssh_manager.connect("host", 22, "user", "pass")
        
        self.assertIsNotNone(self.ssh_manager.client)
        self.assertEqual(self.ssh_manager.host_key, "host")
        mock_client_instance.set_missing_host_key_policy.assert_called()
        mock_client_instance.connect.assert_called_with(
            hostname="host", port=22, username="user", password="pass",
            timeout=10, allow_agent=False, look_for_keys=False
        )

    @patch('SSH_DeviceManager.paramiko.SSHClient')
    def test_disconnect(self, mock_ssh_client):
        self.ssh_manager.client = mock_ssh_client.return_value
        self.ssh_manager.sftp = MagicMock()
        
        self.ssh_manager.disconnect()
        
        self.assertIsNone(self.ssh_manager.client)
        self.assertIsNone(self.ssh_manager.sftp)
        self.assertIsNone(self.ssh_manager.host_key)
        mock_ssh_client.return_value.close.assert_called()

    @patch('SSH_DeviceManager.paramiko.SSHClient')
    def test_disconnect_with_error(self, mock_ssh_client):
        # Test that disconnect handles exceptions gracefully (suppress)
        mock_client_instance = mock_ssh_client.return_value
        self.ssh_manager.client = mock_client_instance
        mock_client_instance.close.side_effect = OSError("Mock error")
        
        try:
            self.ssh_manager.disconnect()
        except Exception as e:
            self.fail(f"disconnect raised {e} unexpectedly!")
            
        self.assertIsNone(self.ssh_manager.client)

    def test_run_command_not_connected(self):
        with self.assertRaises(RuntimeError):
            self.ssh_manager.run_command("ls")

    @patch('SSH_DeviceManager.paramiko.SSHClient')
    def test_run_command(self, mock_ssh_client):
        mock_client_instance = mock_ssh_client.return_value
        self.ssh_manager.client = mock_client_instance
        
        # Mock stdout and stderr
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"output"
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""
        
        mock_client_instance.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        result = self.ssh_manager.run_command("ls")
        
        self.assertEqual(result, "output")
        mock_client_instance.exec_command.assert_called_with("ls", timeout=30)

    @patch('SSH_DeviceManager.paramiko.SSHClient')
    def test_run_command_decoding(self, mock_ssh_client):
        mock_client_instance = mock_ssh_client.return_value
        self.ssh_manager.client = mock_client_instance
        
        mock_stdout = MagicMock()
        # Invalid utf-8 byte to test error handling
        mock_stdout.read.return_value = b"\x80" 
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""
        
        mock_client_instance.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        result = self.ssh_manager.run_command("ls")
        
        # Should not raise UnicodeDecodeError and contain replacement char
        self.assertIsInstance(result, str)
        self.assertIn("\ufffd", result)

    @patch('SSH_DeviceManager.paramiko.SSHClient')
    def test_run_command_with_stderr(self, mock_ssh_client):
        mock_client_instance = mock_ssh_client.return_value
        self.ssh_manager.client = mock_client_instance

        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"normal output"
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b"error output"

        mock_client_instance.exec_command.return_value = (None, mock_stdout, mock_stderr)

        result = self.ssh_manager.run_command("bad_cmd")

        self.assertIn("normal output", result)
        self.assertIn("error output", result)

    @patch('SSH_DeviceManager.paramiko.SSHClient')
    def test_connect_host_key_policies(self, mock_ssh_client):
        mock_client_instance = mock_ssh_client.return_value

        for mode, expected_policy in [
            ("strict", SSH_DeviceManager.paramiko.RejectPolicy),
            ("warning", SSH_DeviceManager.paramiko.WarningPolicy),
            ("auto", SSH_DeviceManager.paramiko.AutoAddPolicy),
        ]:
            mock_client_instance.reset_mock()
            self.ssh_manager.client = None
            self.ssh_manager.connect("host", 22, "user", "pass", host_key_mode=mode)
            policy_arg = mock_client_instance.set_missing_host_key_policy.call_args[0][0]
            self.assertIsInstance(policy_arg, expected_policy,
                f"Mode '{mode}' should use {expected_policy.__name__}")

    @patch('SSH_DeviceManager.paramiko.SSHClient')
    def test_upload_file(self, mock_ssh_client):
        mock_client_instance = mock_ssh_client.return_value
        self.ssh_manager.client = mock_client_instance
        mock_sftp = MagicMock()
        mock_client_instance.open_sftp.return_value = mock_sftp
        
        self.ssh_manager.upload_file("local", "remote")
        
        self.assertIsNotNone(self.ssh_manager.sftp)
        mock_sftp.put.assert_called_with("local", "remote")

    def test_upload_file_not_connected(self):
        with self.assertRaises(RuntimeError):
            self.ssh_manager.upload_file("local", "remote")

    @patch('SSH_DeviceManager.paramiko.SSHClient')
    def test_upload_file_reuses_sftp(self, mock_ssh_client):
        mock_client_instance = mock_ssh_client.return_value
        self.ssh_manager.client = mock_client_instance
        mock_sftp = MagicMock()
        mock_client_instance.open_sftp.return_value = mock_sftp

        self.ssh_manager.upload_file("local1", "remote1")
        self.ssh_manager.upload_file("local2", "remote2")

        # open_sftp should only be called once; second upload reuses it
        mock_client_instance.open_sftp.assert_called_once()
        self.assertEqual(mock_sftp.put.call_count, 2)

class TestSSHGuiApp(unittest.TestCase):
    @patch('ssh_device_manager.app.SSHManager')
    def test_app_initialization(self, mock_ssh_manager):
        # Since we mocked tkinter, we can instantiate the app
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        self.assertIsNotNone(app.ssh)
        self.assertIsInstance(app.sections, list)
        self.assertTrue(len(app.sections) > 0)
        
        # Check if sections are valid
        for section in app.sections:
            self.assertIsInstance(section, SSH_DeviceManager.ButtonSection)
            self.assertTrue(len(section.actions) > 0)

    @patch('SSH_DeviceManager.threading.Thread')
    def test_on_connect(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        
        # Configure mocks for UI variables
        app.host_var.get.return_value = "192.168.1.1"
        app.user_var.get.return_value = "admin"
        app.port_var.get.return_value = 22
        app.pass_var.get.return_value = "password"
        app.timeout_var.get.return_value = 10

        app.ssh = MagicMock()
        app.log = MagicMock()

        app.on_connect()

        # Verify thread started
        mock_thread.assert_called()
        args, kwargs = mock_thread.call_args
        target = kwargs.get('target')

        # Execute the worker function
        target()

        app.ssh.connect.assert_called_with(
            "192.168.1.1",
            22,
            "admin",
            "password",
            timeout=10,
            host_key_mode="warning",
        )

    def test_on_disconnect(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.log = MagicMock()
        app.clear_creds_var.get.return_value = True
        app.pass_var.set = MagicMock()
        app._set_connected_ui = MagicMock()
        
        app.on_disconnect()
        
        app.ssh.disconnect.assert_called()
        app.pass_var.set.assert_called_with("")
        app._set_connected_ui.assert_called_with(False)

    @patch('SSH_DeviceManager.threading.Thread')
    def test_test_connection(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = False # Not connected
        app.log = MagicMock()
        
        app.host_var.get.return_value = "192.168.1.1"
        app.user_var.get.return_value = "admin"
        app.port_var.get.return_value = 22
        app.pass_var.get.return_value = "password"
        app.timeout_var.get.return_value = 10

        app.test_connection()

        mock_thread.assert_called()
        args, kwargs = mock_thread.call_args
        target = kwargs.get('target')

        # We need to mock SSHManager inside the worker
        with patch('ssh_device_manager.app.SSHManager') as MockSSHManager:
            mock_temp_ssh = MockSSHManager.return_value
            target()
            mock_temp_ssh.connect.assert_called_with(
                "192.168.1.1",
                22,
                "admin",
                "password",
                timeout=10,
                host_key_mode="warning",
            )
            mock_temp_ssh.disconnect.assert_called()

    @patch('SSH_DeviceManager.threading.Thread')
    def test_run_ssh_command(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = True
        app.log = MagicMock()
        
        app.run_ssh_command("show version")
        
        # Check history update
        self.assertEqual(app.command_history[0], "show version")
        
        # Check thread start
        mock_thread.assert_called()
        args, kwargs = mock_thread.call_args
        target = kwargs.get('target')
        
        # Run the worker
        target()
        
        # Check if ssh command was called
        app.ssh.run_command.assert_called_with("show version")

    @patch('SSH_DeviceManager.threading.Thread')
    def test_upload_config_template(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = True
        app.log = MagicMock()
        
        # Mock file dialog
        SSH_DeviceManager.filedialog.askopenfilename.return_value = "/path/to/file"
        
        app.upload_config_template()
        
        mock_thread.assert_called()
        args, kwargs = mock_thread.call_args
        target = kwargs.get('target')
        
        # Run worker
        target()
        
        app.ssh.upload_file.assert_called_with("/path/to/file", "/tmp/uploaded_config.txt")

    def test_copy_output(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.output_text = MagicMock()
        app.output_text.get.return_value = "some output"
        app.log = MagicMock()
        
        app.copy_output()
        
        app.clipboard_clear.assert_called()
        app.clipboard_append.assert_called_with("some output")

    def test_log(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        
        # Drain the log_queue if needed (not relevant to the test itself)
        while not app.log_queue.empty():
            app.log_queue.get()
        
        app.log("test message")
        
        # Check if message was put in queue
        self.assertFalse(app.log_queue.empty())
        msg = app.log_queue.get()
        self.assertIn("test message", msg)

    def test_save_output(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.output_text = MagicMock()
        app.output_text.get.return_value = "some output"
        app.log = MagicMock()
        
        # Mock file dialog
        SSH_DeviceManager.filedialog.asksaveasfilename.return_value = "/tmp/saved_output.txt"
        
        # Mock open
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            app.save_output()
            mock_file.assert_called_with("/tmp/saved_output.txt", "w", encoding="utf-8")
            mock_file().write.assert_called_with("some output")

    def test_save_output_empty(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.output_text = MagicMock()
        app.output_text.get.return_value = "   "  # whitespace only
        app.log = MagicMock()

        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            app.save_output()
            # Should NOT open a file when output is blank
            mock_file.assert_not_called()

    def test_save_output_write_error(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.output_text = MagicMock()
        app.output_text.get.return_value = "some output"
        app.log = MagicMock()

        SSH_DeviceManager.filedialog.asksaveasfilename.return_value = "/tmp/fail.txt"

        with patch("builtins.open", side_effect=IOError("disk full")):
            app.save_output()
            log_messages = [c[0][0] for c in app.log.call_args_list]
            self.assertTrue(any("ERROR" in m and "disk full" in m for m in log_messages))

    def test_clear_output(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.output_text = MagicMock()

        app.clear_output()

        # Should enable, delete all, then re-disable the text widget
        app.output_text.configure.assert_any_call(state="normal")
        app.output_text.delete.assert_called_with("1.0", "end")
        app.output_text.configure.assert_any_call(state="disabled")

    @patch('SSH_DeviceManager.threading.Thread')
    def test_on_connect_double_click_guard(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_var.get.return_value = "192.168.1.1"
        app.user_var.get.return_value = "admin"
        app.port_var.get.return_value = 22
        app.pass_var.get.return_value = "password"
        app.timeout_var.get.return_value = 10
        app.ssh = MagicMock()
        app.log = MagicMock()

        # Simulate an in-progress connection
        app.is_connecting = True

        app.on_connect()

        # Thread should NOT be spawned when already connecting
        mock_thread.assert_not_called()

    def test_run_ssh_command_not_connected(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = False
        app.log = MagicMock()

        app.run_ssh_command("show version")

        # Should not add to command history if not connected
        self.assertEqual(len(app.command_history), 0)

    def test_upload_config_template_not_connected(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = False
        app.log = MagicMock()

        app.upload_config_template()

        # Should not attempt upload
        app.ssh.upload_file.assert_not_called()

    def test_upload_config_template_cancelled(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = True
        app.log = MagicMock()

        SSH_DeviceManager.filedialog.askopenfilename.return_value = ""

        app.upload_config_template()

        # Should not attempt upload when dialog is cancelled
        app.ssh.upload_file.assert_not_called()

    def test_log_message_has_timestamp(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)

        while not app.log_queue.empty():
            app.log_queue.get()

        app.log("hello")
        msg = app.log_queue.get()

        # Timestamp format [HH:MM:SS]
        import re
        self.assertRegex(msg, r"\[\d{2}:\d{2}:\d{2}\]")


class TestGetConnectionInputs(unittest.TestCase):
    """Tests for the _get_connection_inputs validation method."""

    def _make_app(self, host="192.168.1.1", port=22, user="admin", pw="secret", timeout=10):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_var.get.return_value = host
        app.port_var.get.return_value = port
        app.user_var.get.return_value = user
        app.pass_var.get.return_value = pw
        app.timeout_var.get.return_value = timeout
        app.log = MagicMock()
        return app

    def test_valid_inputs(self):
        app = self._make_app()
        result = app._get_connection_inputs()
        self.assertIsNotNone(result)
        host, port, user, pw, timeout = result
        self.assertEqual(host, "192.168.1.1")
        self.assertEqual(port, 22)
        self.assertEqual(user, "admin")
        self.assertEqual(pw, "secret")
        self.assertEqual(timeout, 10)

    def test_empty_host(self):
        app = self._make_app(host="")
        self.assertIsNone(app._get_connection_inputs())
        app.log.assert_called()
        logged = app.log.call_args[0][0]
        self.assertIn("Host / IP is empty", logged)

    def test_empty_username(self):
        app = self._make_app(user="")
        self.assertIsNone(app._get_connection_inputs())
        logged = app.log.call_args[0][0]
        self.assertIn("Username is empty", logged)

    def test_empty_password(self):
        app = self._make_app(pw="")
        self.assertIsNone(app._get_connection_inputs())
        logged = app.log.call_args[0][0]
        self.assertIn("Password is empty", logged)

    def test_multiple_empty_fields(self):
        app = self._make_app(host="", user="", pw="")
        self.assertIsNone(app._get_connection_inputs())
        logged = app.log.call_args[0][0]
        self.assertIn("Host / IP is empty", logged)
        self.assertIn("Username is empty", logged)
        self.assertIn("Password is empty", logged)

    def test_port_tcl_error(self):
        app = self._make_app()
        app.port_var.get.side_effect = Exception("can't read: no value")
        self.assertIsNone(app._get_connection_inputs())
        logged = app.log.call_args[0][0]
        self.assertIn("Port", logged)

    def test_port_out_of_range(self):
        app = self._make_app(port=99999)
        self.assertIsNone(app._get_connection_inputs())
        logged = app.log.call_args[0][0]
        self.assertIn("Port must be between", logged)

    def test_port_zero(self):
        app = self._make_app(port=0)
        self.assertIsNone(app._get_connection_inputs())

    def test_timeout_tcl_error(self):
        app = self._make_app()
        app.timeout_var.get.side_effect = Exception("can't read: no value")
        self.assertIsNone(app._get_connection_inputs())
        logged = app.log.call_args[0][0]
        self.assertIn("Connection Timeout", logged)

    def test_timeout_out_of_range(self):
        app = self._make_app(timeout=999)
        self.assertIsNone(app._get_connection_inputs())
        logged = app.log.call_args[0][0]
        self.assertIn("Connection Timeout must be between", logged)


class TestOnConnectErrors(unittest.TestCase):
    """Tests for specific exception handling in on_connect worker."""

    def _make_app(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_var.get.return_value = "192.168.1.1"
        app.user_var.get.return_value = "admin"
        app.port_var.get.return_value = 22
        app.pass_var.get.return_value = "password"
        app.timeout_var.get.return_value = 10
        app.ssh = MagicMock()
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()
        return app

    @patch('SSH_DeviceManager.threading.Thread')
    def test_auth_exception(self, mock_thread):
        app = self._make_app()
        app.ssh.connect.side_effect = SSH_DeviceManager.paramiko.AuthenticationException("bad creds")
        app.on_connect()
        target = mock_thread.call_args[1]['target']
        target()
        logged = [c[0][0] for c in app.log.call_args_list]
        auth_msg = [m for m in logged if "Authentication failed" in m]
        self.assertTrue(len(auth_msg) > 0)
        self.assertIn("Username and Password", auth_msg[0])
        app._set_connected_ui.assert_called_with(False)

    @patch('SSH_DeviceManager.threading.Thread')
    def test_ssh_exception(self, mock_thread):
        app = self._make_app()
        app.ssh.connect.side_effect = SSH_DeviceManager.paramiko.SSHException("protocol error")
        app.on_connect()
        target = mock_thread.call_args[1]['target']
        target()
        logged = [c[0][0] for c in app.log.call_args_list]
        ssh_msg = [m for m in logged if "SSH error" in m]
        self.assertTrue(len(ssh_msg) > 0)
        app._set_connected_ui.assert_called_with(False)

    @patch('SSH_DeviceManager.threading.Thread')
    def test_os_error(self, mock_thread):
        app = self._make_app()
        app.ssh.connect.side_effect = OSError("No route to host")
        app.on_connect()
        target = mock_thread.call_args[1]['target']
        target()
        logged = [c[0][0] for c in app.log.call_args_list]
        net_msg = [m for m in logged if "Network error" in m]
        self.assertTrue(len(net_msg) > 0)
        app._set_connected_ui.assert_called_with(False)

    @patch('SSH_DeviceManager.threading.Thread')
    def test_generic_exception(self, mock_thread):
        app = self._make_app()
        app.ssh.connect.side_effect = RuntimeError("unexpected")
        app.on_connect()
        target = mock_thread.call_args[1]['target']
        target()
        logged = [c[0][0] for c in app.log.call_args_list]
        err_msg = [m for m in logged if "Connection failed" in m]
        self.assertTrue(len(err_msg) > 0)


class TestTestConnectionErrors(unittest.TestCase):
    """Tests for specific exception handling in test_connection worker."""

    def _make_app(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_var.get.return_value = "192.168.1.1"
        app.user_var.get.return_value = "admin"
        app.port_var.get.return_value = 22
        app.pass_var.get.return_value = "password"
        app.timeout_var.get.return_value = 10
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = False
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()
        return app

    @patch('ssh_device_manager.app.SSHManager')
    @patch('SSH_DeviceManager.threading.Thread')
    def test_test_connection_auth_error(self, mock_thread, MockSSHManager):
        app = self._make_app()
        app.test_connection()
        target = mock_thread.call_args[1]['target']
        MockSSHManager.return_value.connect.side_effect = (
            SSH_DeviceManager.paramiko.AuthenticationException("bad creds")
        )
        target()
        logged = [c[0][0] for c in app.log.call_args_list]
        auth_msg = [m for m in logged if "authentication rejected" in m]
        self.assertTrue(len(auth_msg) > 0)

    @patch('ssh_device_manager.app.SSHManager')
    @patch('SSH_DeviceManager.threading.Thread')
    def test_test_connection_os_error(self, mock_thread, MockSSHManager):
        app = self._make_app()
        app.test_connection()
        target = mock_thread.call_args[1]['target']
        MockSSHManager.return_value.connect.side_effect = OSError("timeout")
        target()
        logged = [c[0][0] for c in app.log.call_args_list]
        net_msg = [m for m in logged if "network error" in m]
        self.assertTrue(len(net_msg) > 0)


class TestGetHostKeyMode(unittest.TestCase):
    """Tests for _get_host_key_mode."""

    def test_valid_modes(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        for mode in ("strict", "warning", "auto"):
            app.host_key_mode_var.get.return_value = mode
            self.assertEqual(app._get_host_key_mode(), mode)

    def test_invalid_mode_defaults_to_warning(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_key_mode_var.get.return_value = "nonsense"
        self.assertEqual(app._get_host_key_mode(), "warning")

    def test_empty_mode_defaults_to_warning(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_key_mode_var.get.return_value = ""
        self.assertEqual(app._get_host_key_mode(), "warning")


class TestParseIntInput(unittest.TestCase):
    """Tests for _parse_int_input."""

    def setUp(self):
        self.app = SSH_DeviceManager.SSHGuiApp(init_ui=False)

    def test_valid_int(self):
        self.assertEqual(self.app._parse_int_input("22", "Port", 1, 65535), 22)

    def test_non_numeric(self):
        self.assertIsNone(self.app._parse_int_input("abc", "Port", 1, 65535))

    def test_empty_string(self):
        self.assertIsNone(self.app._parse_int_input("", "Port", 1, 65535))

    def test_below_minimum(self):
        self.assertIsNone(self.app._parse_int_input("0", "Port", 1, 65535))

    def test_above_maximum(self):
        self.assertIsNone(self.app._parse_int_input("99999", "Port", 1, 65535))

    def test_no_maximum(self):
        self.assertEqual(self.app._parse_int_input("999999", "Count", 1), 999999)


class TestThemes(unittest.TestCase):
    """Tests that all themes have required keys and apply_theme does not crash."""

    REQUIRED_KEYS = {"bg", "fg", "text_bg", "text_fg", "entry_bg", "entry_fg",
                     "select_bg", "select_fg"}

    def test_all_themes_have_required_keys(self):
        for name, theme in SSH_DeviceManager.SSHGuiApp.THEMES.items():
            for key in self.REQUIRED_KEYS:
                self.assertIn(key, theme, f"Theme '{name}' missing key '{key}'")

    def test_all_themes_have_optional_keys(self):
        optional = {"btn_bg", "border", "label_fg"}
        for name, theme in SSH_DeviceManager.SSHGuiApp.THEMES.items():
            for key in optional:
                self.assertIn(key, theme, f"Theme '{name}' missing optional key '{key}'")

    def test_solarized_dark_uses_canonical_palette(self):
        sd = SSH_DeviceManager.SSHGuiApp.THEMES["Solarized Dark"]
        self.assertEqual(sd["bg"], "#002b36")         # base03
        self.assertEqual(sd["entry_bg"], "#073642")   # base02
        self.assertEqual(sd["select_bg"], "#268bd2")  # blue
        self.assertEqual(sd["border"], "#586e75")     # base01


class TestProfiles(unittest.TestCase):
    """Tests for profile save/load/delete."""

    def _make_app(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_var.get.return_value = "10.0.0.1"
        app.port_var.get.return_value = 22
        app.user_var.get.return_value = "root"
        app.pass_var.get.return_value = "password"
        app.timeout_var.get.return_value = 10
        app.log = MagicMock()
        app._save_app_config = MagicMock()
        app._refresh_profile_list = MagicMock()
        return app

    def test_save_profile(self):
        app = self._make_app()
        app.profile_name_var.get.return_value = "MyProfile"
        app.profile_select_var.get.return_value = ""
        app.save_profile()
        self.assertIn("MyProfile", app.app_config["profiles"])
        saved = app.app_config["profiles"]["MyProfile"]
        self.assertEqual(saved["host"], "10.0.0.1")
        self.assertEqual(saved["port"], 22)
        self.assertEqual(saved["username"], "root")
        app._save_app_config.assert_called()

    def test_save_profile_no_name(self):
        app = self._make_app()
        app.profile_name_var.get.return_value = ""
        app.profile_select_var.get.return_value = ""
        # _get_connection_inputs should never be reached
        app._get_connection_inputs = MagicMock()
        app.save_profile()
        app._get_connection_inputs.assert_not_called()
        app._save_app_config.assert_not_called()

    def test_load_selected_profile(self):
        app = self._make_app()
        app.app_config["profiles"] = {
            "TestProf": {
                "host": "1.2.3.4",
                "port": 2222,
                "username": "testuser",
                "timeout": 30,
                "host_key_mode": "auto",
            }
        }
        app.profile_select_var.get.return_value = "TestProf"
        app.load_selected_profile()
        app.host_var.set.assert_called_with("1.2.3.4")
        app.port_var.set.assert_called_with(2222)
        app.user_var.set.assert_called_with("testuser")
        app.timeout_var.set.assert_called_with(30)

    def test_load_missing_profile(self):
        app = self._make_app()
        app.profile_select_var.get.return_value = "DoesNotExist"
        app.load_selected_profile()
        # Should not crash; host_var.set should not be called
        app.host_var.set.assert_not_called()

    def test_delete_selected_profile(self):
        app = self._make_app()
        app.app_config["profiles"] = {"ToDelete": {"host": "x"}}
        app.profile_select_var.get.return_value = "ToDelete"
        app.profile_name_var.get.return_value = "ToDelete"
        # Patch askyesno to return True for this test
        original = messagebox.askyesno
        messagebox.askyesno = lambda *a, **k: True
        try:
            app.delete_selected_profile()
        finally:
            messagebox.askyesno = original
        self.assertNotIn("ToDelete", app.app_config["profiles"])
        app._save_app_config.assert_called()

    def test_delete_profile_cancelled(self):
        app = self._make_app()
        app.app_config["profiles"] = {"KeepMe": {"host": "x"}}
        app.profile_select_var.get.return_value = "KeepMe"
        # askyesno returns False by default in our stub
        app.delete_selected_profile()
        self.assertIn("KeepMe", app.app_config["profiles"])

    def test_load_missing_profile_shows_error(self):
        app = self._make_app()
        app._refresh_profile_list = MagicMock()
        app.profile_select_var.get.return_value = "DoesNotExist"
        app.load_selected_profile()
        # Should not populate fields
        app.host_var.set.assert_not_called()
        # Should trigger profile list refresh (cleanup stale list)
        app._refresh_profile_list.assert_called()

    def test_save_profile_via_dropdown_name(self):
        """When profile_name_var is empty, use profile_select_var instead."""
        app = self._make_app()
        app.profile_name_var.get.return_value = ""
        app.profile_select_var.get.return_value = "FromDropdown"
        app._save_app_config = MagicMock()
        app._refresh_profile_list = MagicMock()

        app.save_profile()

        self.assertIn("FromDropdown", app.app_config["profiles"])


class TestConnectionStateMonitor(unittest.TestCase):
    """Tests for _refresh_connection_state."""

    def test_detects_dropped_connection(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = False
        app.is_connecting = False
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()
        app.status_var = MagicMock()
        app.status_var.get.return_value = "Connected"  # was connected

        app._refresh_connection_state(notify_on_drop=True)

        app._set_connected_ui.assert_called_with(False)
        log_messages = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("no longer active" in m for m in log_messages))

    def test_no_false_alarm_when_disconnected(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = False
        app.is_connecting = False
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()
        app.status_var = MagicMock()
        app.status_var.get.return_value = "Disconnected"

        app._refresh_connection_state(notify_on_drop=False)

        app._set_connected_ui.assert_called_with(False)
        # Should NOT warn about dropped connection
        log_messages = [c[0][0] for c in app.log.call_args_list]
        self.assertFalse(any("no longer active" in m for m in log_messages))


class TestHostHistory(unittest.TestCase):
    """Tests for host combobox history."""

    def test_on_host_selected_clear(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_history = ["10.0.0.1", "10.0.0.2"]
        app.host_var.get.return_value = "<Clear History>"
        app.host_var.set = MagicMock()
        app.log = MagicMock()
        app.on_host_selected(None)
        self.assertEqual(len(app.host_history), 0)
        app.host_var.set.assert_called_with("")

    @patch('SSH_DeviceManager.threading.Thread')
    def test_connect_adds_to_host_history(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_var.get.return_value = "newhost.example.com"
        app.user_var.get.return_value = "admin"
        app.port_var.get.return_value = 22
        app.pass_var.get.return_value = "password"
        app.timeout_var.get.return_value = 10
        app.ssh = MagicMock()
        app.log = MagicMock()
        app.on_connect()
        self.assertIn("newhost.example.com", app.host_history)


# =========================================================================
# Integration Tests
# =========================================================================


class TestConnectRunDisconnectLifecycle(unittest.TestCase):
    """Full connect -> run command -> disconnect lifecycle."""

    @patch('SSH_DeviceManager.threading.Thread')
    def test_full_lifecycle(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_var.get.return_value = "10.0.0.1"
        app.user_var.get.return_value = "admin"
        app.port_var.get.return_value = 22
        app.pass_var.get.return_value = "secret"
        app.timeout_var.get.return_value = 10
        app.ssh = MagicMock()
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()
        app.clear_creds_var.get.return_value = False

        # --- Step 1: Connect ---
        app.on_connect()
        connect_target = mock_thread.call_args[1]["target"]
        connect_target()
        app.ssh.connect.assert_called_once_with(
            "10.0.0.1", 22, "admin", "secret",
            timeout=10, host_key_mode="warning",
        )
        app._set_connected_ui.assert_called_with(True)

        # --- Step 2: Run a command ---
        mock_thread.reset_mock()
        app.ssh.is_connected.return_value = True
        app.run_ssh_command("show version")
        cmd_target = mock_thread.call_args[1]["target"]
        app.ssh.run_command.return_value = "Version 1.0"
        cmd_target()
        app.ssh.run_command.assert_called_with("show version")
        self.assertEqual(app.command_history[0], "show version")

        # --- Step 3: Run a second command ---
        mock_thread.reset_mock()
        app.run_ssh_command("show interfaces")
        cmd_target2 = mock_thread.call_args[1]["target"]
        app.ssh.run_command.return_value = "eth0: UP"
        cmd_target2()
        app.ssh.run_command.assert_called_with("show interfaces")
        self.assertEqual(app.command_history[0], "show interfaces")
        self.assertEqual(app.command_history[1], "show version")

        # --- Step 4: Disconnect ---
        app._set_connected_ui.reset_mock()
        app.on_disconnect()
        app.ssh.disconnect.assert_called()
        app._set_connected_ui.assert_called_with(False)

        # Verify log captured key events
        log_messages = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("Connecting" in m for m in log_messages))
        self.assertTrue(any("[OK] Connected" in m for m in log_messages))
        self.assertTrue(any("show version" in m for m in log_messages))
        self.assertTrue(any("Disconnecting" in m for m in log_messages))


class TestConnectAuthFailureRetry(unittest.TestCase):
    """Connect fails with auth error, then retry succeeds."""

    @patch('SSH_DeviceManager.threading.Thread')
    def test_auth_failure_then_success(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_var.get.return_value = "10.0.0.1"
        app.user_var.get.return_value = "admin"
        app.port_var.get.return_value = 22
        app.pass_var.get.return_value = "wrong_password"
        app.timeout_var.get.return_value = 10
        app.ssh = MagicMock()
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()

        # --- Attempt 1: Wrong password ---
        app.ssh.connect.side_effect = SSH_DeviceManager.paramiko.AuthenticationException("bad")
        app.on_connect()
        target1 = mock_thread.call_args[1]["target"]
        target1()

        log_messages = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("Authentication failed" in m for m in log_messages))
        app._set_connected_ui.assert_called_with(False)

        # --- Attempt 2: Correct password ---
        mock_thread.reset_mock()
        app.log.reset_mock()
        app._set_connected_ui.reset_mock()
        app.pass_var.get.return_value = "correct_password"
        app.ssh.connect.side_effect = None
        app.ssh.connect.reset_mock()
        app.is_connecting = False

        app.on_connect()
        target2 = mock_thread.call_args[1]["target"]
        target2()

        app.ssh.connect.assert_called_once()
        call_kwargs = app.ssh.connect.call_args
        self.assertEqual(call_kwargs[0][3], "correct_password")
        app._set_connected_ui.assert_called_with(True)


class TestValidationBlocksConnect(unittest.TestCase):
    """Validation errors prevent connect; fixing fields allows it."""

    @patch('SSH_DeviceManager.threading.Thread')
    def test_empty_fields_block_then_succeed(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()

        # --- All fields empty: connect should not spawn a thread ---
        app.host_var.get.return_value = ""
        app.user_var.get.return_value = ""
        app.pass_var.get.return_value = ""
        app.port_var.get.return_value = 22
        app.timeout_var.get.return_value = 10

        app.on_connect()
        mock_thread.assert_not_called()

        log_messages = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("Host / IP is empty" in m for m in log_messages))
        self.assertTrue(any("Username is empty" in m for m in log_messages))
        self.assertTrue(any("Password is empty" in m for m in log_messages))

        # --- Fix fields: connect should proceed ---
        mock_thread.reset_mock()
        app.log.reset_mock()
        app.host_var.get.return_value = "10.0.0.1"
        app.user_var.get.return_value = "admin"
        app.pass_var.get.return_value = "secret"

        app.on_connect()
        mock_thread.assert_called_once()


class TestProfileWorkflow(unittest.TestCase):
    """Save profile -> load profile -> connect using loaded values."""

    @patch('SSH_DeviceManager.threading.Thread')
    def test_save_load_connect(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()
        app._save_app_config = MagicMock()
        app._refresh_profile_list = MagicMock()

        # --- Step 1: Fill in connection fields and save profile ---
        app.host_var.get.return_value = "router.local"
        app.port_var.get.return_value = 2222
        app.user_var.get.return_value = "netadmin"
        app.pass_var.get.return_value = "s3cret"
        app.timeout_var.get.return_value = 15
        app.profile_name_var.get.return_value = "RouterProfile"
        app.profile_select_var.get.return_value = ""

        app.save_profile()

        self.assertIn("RouterProfile", app.app_config["profiles"])
        saved = app.app_config["profiles"]["RouterProfile"]
        self.assertEqual(saved["host"], "router.local")
        self.assertEqual(saved["port"], 2222)
        self.assertEqual(saved["username"], "netadmin")
        self.assertEqual(saved["timeout"], 15)

        # --- Step 2: Clear fields then load profile ---
        app.host_var.set.reset_mock()
        app.port_var.set.reset_mock()
        app.user_var.set.reset_mock()
        app.timeout_var.set.reset_mock()

        app.profile_select_var.get.return_value = "RouterProfile"
        app.load_selected_profile()

        app.host_var.set.assert_called_with("router.local")
        app.port_var.set.assert_called_with(2222)
        app.user_var.set.assert_called_with("netadmin")
        app.timeout_var.set.assert_called_with(15)

        # --- Step 3: Connect using loaded values ---
        app.host_var.get.return_value = "router.local"
        app.port_var.get.return_value = 2222
        app.user_var.get.return_value = "netadmin"
        app.pass_var.get.return_value = "s3cret"
        app.timeout_var.get.return_value = 15

        app.on_connect()
        target = mock_thread.call_args[1]["target"]
        target()

        app.ssh.connect.assert_called_once_with(
            "router.local", 2222, "netadmin", "s3cret",
            timeout=15, host_key_mode="warning",
        )


class TestSectionsJsonLoading(unittest.TestCase):
    """Load sections from a JSON file and verify structure/handlers."""

    def test_load_valid_sections_json(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.log = MagicMock()

        json_data = json.dumps({
            "sections": [
                {
                    "title": "Diagnostics",
                    "max_buttons": 4,
                    "actions": [
                        {"label": "Ping", "enabled": True, "command": "ping -c 4 8.8.8.8", "tooltip": "Ping Google"},
                        {"label": "Disk", "enabled": True, "command": "run:df -h", "tooltip": "Check disk"},
                        {"label": "Upload", "enabled": True, "command": "__upload_template__", "tooltip": "Upload file"},
                        {"label": "Custom", "enabled": True, "command": "__custom_command__", "tooltip": "Custom cmd"},
                        {"label": "SCP", "enabled": True, "command": "__send_file__", "tooltip": "SCP file"},
                        {"label": "Disabled", "enabled": False, "command": "hostname", "tooltip": "Hidden"},
                    ],
                },
                {
                    "title": "Empty Section",
                    "max_buttons": 2,
                    "actions": [],
                },
            ]
        })

        with patch("builtins.open", unittest.mock.mock_open(read_data=json_data)):
            with patch("os.path.exists", return_value=True):
                sections = app.load_sections_from_file("test_sections.json")

        self.assertEqual(len(sections), 2)

        diag = sections[0]
        self.assertEqual(diag.title, "Diagnostics")
        self.assertEqual(diag.max_buttons, 4)
        self.assertEqual(len(diag.actions), 6)

        # Verify enabled/disabled
        self.assertTrue(diag.actions[0].enabled)
        self.assertFalse(diag.actions[5].enabled)

        # Verify labels
        self.assertEqual(diag.actions[0].label, "Ping")
        self.assertEqual(diag.actions[2].label, "Upload")
        self.assertEqual(diag.actions[4].label, "SCP")

        # Verify special handler tokens resolve to methods
        self.assertEqual(diag.actions[2].handler, app.upload_config_template)
        self.assertEqual(diag.actions[3].handler, app.prompt_and_run_custom_command)
        self.assertEqual(diag.actions[4].handler, app.send_file_scp)

        # Verify all handlers are callable
        for action in diag.actions:
            self.assertTrue(callable(action.handler))

    def test_load_missing_file_falls_back(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.log = MagicMock()

        with patch("os.path.exists", return_value=False):
            sections = app.load_sections_from_file("nonexistent.json")

        # Should fall back to built-in sections
        self.assertTrue(len(sections) > 0)
        log_messages = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("not found" in m for m in log_messages))

    def test_load_invalid_json_falls_back(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.log = MagicMock()

        with patch("builtins.open", unittest.mock.mock_open(read_data="NOT JSON")):
            with patch("os.path.exists", return_value=True):
                sections = app.load_sections_from_file("bad.json")

        self.assertTrue(len(sections) > 0)
        log_messages = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("ERROR" in m for m in log_messages))

    def test_load_empty_sections_falls_back(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.log = MagicMock()

        json_data = json.dumps({"sections": []})
        with patch("builtins.open", unittest.mock.mock_open(read_data=json_data)):
            with patch("os.path.exists", return_value=True):
                sections = app.load_sections_from_file("empty.json")

        self.assertTrue(len(sections) > 0)
        log_messages = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("no sections" in m.lower() for m in log_messages))


class TestCommandHistoryIntegration(unittest.TestCase):
    """Command history accumulates correctly across multiple commands."""

    @patch('SSH_DeviceManager.threading.Thread')
    def test_history_ordering_and_dedup(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = True
        app.log = MagicMock()

        # Run several commands
        app.run_ssh_command("cmd_a")
        app.run_ssh_command("cmd_b")
        app.run_ssh_command("cmd_c")

        # Most recent first
        self.assertEqual(app.command_history[0], "cmd_c")
        self.assertEqual(app.command_history[1], "cmd_b")
        self.assertEqual(app.command_history[2], "cmd_a")

        # Running a duplicate should move it to front
        app.run_ssh_command("cmd_a")
        self.assertEqual(app.command_history[0], "cmd_a")

        # Verify no duplicate entries remain
        self.assertEqual(app.command_history.count("cmd_a"), 1,
            "Duplicate command should be removed from its old position")

    @patch('SSH_DeviceManager.threading.Thread')
    def test_history_limit(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = True
        app.log = MagicMock()

        limit = SSH_DeviceManager.COMMAND_HISTORY_LIMIT
        for i in range(limit + 50):
            app.run_ssh_command(f"cmd_{i}")

        self.assertLessEqual(len(app.command_history), limit)


class TestCommandFailureHandling(unittest.TestCase):
    """Connect -> command fails -> error logged -> disconnect clean."""

    @patch('SSH_DeviceManager.threading.Thread')
    def test_command_error_then_disconnect(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_var.get.return_value = "10.0.0.1"
        app.user_var.get.return_value = "admin"
        app.port_var.get.return_value = 22
        app.pass_var.get.return_value = "secret"
        app.timeout_var.get.return_value = 10
        app.ssh = MagicMock()
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()
        app.clear_creds_var.get.return_value = False

        # --- Connect ---
        app.on_connect()
        connect_target = mock_thread.call_args[1]["target"]
        connect_target()
        app._set_connected_ui.assert_called_with(True)

        # --- Run command that fails ---
        mock_thread.reset_mock()
        app.log.reset_mock()
        app.ssh.is_connected.return_value = True
        app.ssh.run_command.side_effect = RuntimeError("channel closed")

        app.run_ssh_command("bad_command")
        cmd_target = mock_thread.call_args[1]["target"]
        cmd_target()

        log_messages = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("ERROR" in m and "channel closed" in m for m in log_messages))

        # --- Disconnect should still work gracefully ---
        app._set_connected_ui.reset_mock()
        app.on_disconnect()
        app.ssh.disconnect.assert_called()
        app._set_connected_ui.assert_called_with(False)


class TestAppConfigRoundTrip(unittest.TestCase):
    """Save config to disk -> reload from disk -> data intact."""

    def test_config_round_trip(self):
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            tmp_path = f.name

        try:
            app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
            app.app_config_path = tmp_path

            # Write profiles
            app.app_config = {
                "profiles": {
                    "Server1": {"host": "1.1.1.1", "port": 22, "username": "root", "timeout": 10, "host_key_mode": "auto"},
                    "Server2": {"host": "2.2.2.2", "port": 2222, "username": "admin", "timeout": 30, "host_key_mode": "strict"},
                }
            }
            app._save_app_config()

            # Re-read from disk
            loaded = app._load_app_config()
            self.assertIn("Server1", loaded["profiles"])
            self.assertIn("Server2", loaded["profiles"])
            self.assertEqual(loaded["profiles"]["Server1"]["host"], "1.1.1.1")
            self.assertEqual(loaded["profiles"]["Server2"]["port"], 2222)
            self.assertEqual(loaded["profiles"]["Server2"]["host_key_mode"], "strict")
        finally:
            os.unlink(tmp_path)

    def test_corrupt_config_returns_default(self):
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("NOT VALID JSON {{{")
            tmp_path = f.name

        try:
            app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
            app.app_config_path = tmp_path
            loaded = app._load_app_config()
            self.assertIn("profiles", loaded)
            self.assertEqual(loaded["profiles"], {})
        finally:
            os.unlink(tmp_path)


class TestHostHistoryLimit(unittest.TestCase):
    """Host history stays within the 10-entry limit."""

    @patch('SSH_DeviceManager.threading.Thread')
    def test_history_capped_at_10(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()
        app.pass_var.get.return_value = "pw"
        app.user_var.get.return_value = "user"
        app.port_var.get.return_value = 22
        app.timeout_var.get.return_value = 10

        for i in range(15):
            app.is_connecting = False
            app.host_var.get.return_value = f"host-{i}.example.com"
            mock_thread.reset_mock()
            app.on_connect()

        self.assertLessEqual(len(app.host_history), 10)
        # Most recent should be first
        self.assertEqual(app.host_history[0], "host-14.example.com")


class TestDisconnectClearsCredentials(unittest.TestCase):
    """Disconnect clears password when option is enabled."""

    def test_creds_cleared_on_disconnect(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()
        app.clear_creds_var.get.return_value = True
        app.pass_var.set = MagicMock()

        app.on_disconnect()

        app.pass_var.set.assert_called_with("")
        log_messages = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("Credentials cleared" in m for m in log_messages))

    def test_creds_preserved_on_disconnect(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()
        app.clear_creds_var.get.return_value = False
        app.pass_var.set = MagicMock()

        app.on_disconnect()

        app.pass_var.set.assert_not_called()


if __name__ == '__main__':
    unittest.main()
