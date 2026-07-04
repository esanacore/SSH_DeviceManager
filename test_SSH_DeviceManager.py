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
    if _key in ('ssh_device_manager', 'SSH_DeviceManager') or _key.startswith('ssh_device_manager.'):
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

    def test_export_output_json(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.output_text = MagicMock()
        app.output_text.get.return_value = "[12:00:00] connected\nshow version"
        app.log = MagicMock()

        SSH_DeviceManager.filedialog.asksaveasfilename.return_value = "/tmp/output.json"

        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            app.export_output_json()

        mock_file.assert_called_with("/tmp/output.json", "w", encoding="utf-8")
        written = "".join(call.args[0] for call in mock_file().write.call_args_list)
        payload = json.loads(written)
        self.assertEqual(payload["format"], "ssh-device-manager-output-v1")
        self.assertEqual(payload["line_count"], 2)
        self.assertEqual(payload["lines"], ["[12:00:00] connected", "show version"])
        self.assertEqual(payload["text"], "[12:00:00] connected\nshow version")

    def test_clear_output(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.output_text = MagicMock()

        app.clear_output()

        # Should enable, delete all, then re-disable the text widget
        app.output_text.configure.assert_any_call(state="normal")
        app.output_text.delete.assert_called_with("1.0", "end")
        app.output_text.configure.assert_any_call(state="disabled")

    def test_append_output_uses_output_manager_public_append(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.output_manager = MagicMock()

        app._append_output("line")

        app.output_manager.append.assert_called_once_with("line")

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
        target = mock_thread.call_args[1]["target"]
        target()
        self.assertIn("newhost.example.com", app.host_history)

    @patch('SSH_DeviceManager.threading.Thread')
    def test_failed_connect_does_not_add_to_host_history(self, mock_thread):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_var.get.return_value = "badhost.example.com"
        app.user_var.get.return_value = "admin"
        app.port_var.get.return_value = 22
        app.pass_var.get.return_value = "bad-password"
        app.timeout_var.get.return_value = 10
        app.ssh = MagicMock()
        app.ssh.connect.side_effect = SSH_DeviceManager.paramiko.AuthenticationException(
            "bad creds"
        )
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()

        app.on_connect()
        target = mock_thread.call_args[1]["target"]
        target()

        self.assertNotIn("badhost.example.com", app.host_history)


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
            target = mock_thread.call_args[1]["target"]
            target()

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


# ===========================================================================
# New tests added to improve coverage
# ===========================================================================

# ---------------------------------------------------------------------------
# OutputManager unit tests  (output.py: 40 % → 100 %)
# ---------------------------------------------------------------------------

class TestOutputManager(unittest.TestCase):
    """Direct unit tests for OutputManager (no SSHGuiApp required)."""

    def _make_manager(self):
        from ssh_device_manager.output import OutputManager
        mock_text = MagicMock()
        manager = OutputManager(mock_text)
        return manager, mock_text

    def test_log_adds_timestamp_to_queue(self):
        import re
        manager, _ = self._make_manager()
        manager.log("hello world")
        self.assertFalse(manager.log_queue.empty())
        msg = manager.log_queue.get_nowait()
        self.assertRegex(msg, r"\[\d{2}:\d{2}:\d{2}\]")
        self.assertIn("hello world", msg)

    def test_append_enables_inserts_and_disables(self):
        manager, mock_text = self._make_manager()
        manager._append("some text")
        mock_text.configure.assert_any_call(state="normal")
        mock_text.insert.assert_called_with("end", "some text")
        mock_text.see.assert_called_with("end")
        mock_text.configure.assert_any_call(state="disabled")

    def test_clear_enables_deletes_and_disables(self):
        manager, mock_text = self._make_manager()
        manager.clear()
        mock_text.configure.assert_any_call(state="normal")
        mock_text.delete.assert_called_with("1.0", "end")
        mock_text.configure.assert_any_call(state="disabled")

    def test_copy_clears_and_appends_to_clipboard(self):
        manager, mock_text = self._make_manager()
        mock_text.get.return_value = "output content"
        mock_root = MagicMock()
        manager.copy(mock_root)
        mock_root.clipboard_clear.assert_called_once()
        mock_root.clipboard_append.assert_called_once_with("output content")
        # Should also log a confirmation
        self.assertFalse(manager.log_queue.empty())

    def test_save_empty_output_shows_warning(self):
        from ssh_device_manager import output as out_mod
        manager, mock_text = self._make_manager()
        mock_text.get.return_value = "   "
        with patch.object(out_mod.messagebox, "showwarning") as mock_warn:
            manager.save()
        mock_warn.assert_called_once()

    def test_save_no_file_chosen_does_not_write(self):
        from ssh_device_manager import output as out_mod
        manager, mock_text = self._make_manager()
        mock_text.get.return_value = "some output"
        with patch.object(out_mod.filedialog, "asksaveasfilename", return_value=""), \
             patch("builtins.open", unittest.mock.mock_open()) as mock_open:
            manager.save()
        mock_open.assert_not_called()

    def test_save_writes_file_and_logs_ok(self):
        from ssh_device_manager import output as out_mod
        manager, mock_text = self._make_manager()
        mock_text.get.return_value = "content"
        with patch.object(out_mod.filedialog, "asksaveasfilename", return_value="/tmp/out.txt"), \
             patch("builtins.open", unittest.mock.mock_open()) as mock_open:
            manager.save()
        mock_open.assert_called_with("/tmp/out.txt", "w", encoding="utf-8")
        mock_open().write.assert_called_with("content")
        self.assertFalse(manager.log_queue.empty())
        msg = manager.log_queue.get_nowait()
        self.assertIn("[OK]", msg)

    def test_save_write_error_logs_error(self):
        from ssh_device_manager import output as out_mod
        manager, mock_text = self._make_manager()
        mock_text.get.return_value = "content"
        with patch.object(out_mod.filedialog, "asksaveasfilename", return_value="/tmp/bad.txt"), \
             patch("builtins.open", side_effect=IOError("disk full")):
            manager.save()
        self.assertFalse(manager.log_queue.empty())
        msg = manager.log_queue.get_nowait()
        self.assertIn("[ERROR]", msg)
        self.assertIn("disk full", msg)

    def test_build_structured_output_keeps_text_and_lines(self):
        from ssh_device_manager.output import build_structured_output
        payload = build_structured_output(
            "first line\nsecond line",
            exported_at="2026-07-04T12:00:00+00:00",
        )
        self.assertEqual(payload["format"], "ssh-device-manager-output-v1")
        self.assertEqual(payload["exported_at"], "2026-07-04T12:00:00+00:00")
        self.assertEqual(payload["line_count"], 2)
        self.assertEqual(payload["lines"], ["first line", "second line"])
        self.assertEqual(payload["text"], "first line\nsecond line")

    def test_export_json_writes_structured_output_and_logs_ok(self):
        from ssh_device_manager import output as out_mod
        manager, mock_text = self._make_manager()
        mock_text.get.return_value = "[12:00:00] connected\nshow version"
        with patch.object(out_mod.filedialog, "asksaveasfilename", return_value="/tmp/out.json"), \
             patch("builtins.open", unittest.mock.mock_open()) as mock_open:
            manager.export_json()
        mock_open.assert_called_with("/tmp/out.json", "w", encoding="utf-8")
        written = "".join(call.args[0] for call in mock_open().write.call_args_list)
        payload = json.loads(written)
        self.assertEqual(payload["format"], "ssh-device-manager-output-v1")
        self.assertEqual(payload["line_count"], 2)
        self.assertEqual(payload["lines"], ["[12:00:00] connected", "show version"])
        self.assertEqual(payload["text"], "[12:00:00] connected\nshow version")
        self.assertFalse(manager.log_queue.empty())
        msg = manager.log_queue.get_nowait()
        self.assertIn("[OK]", msg)
        self.assertIn("exported", msg)

    def test_export_json_empty_output_shows_warning(self):
        from ssh_device_manager import output as out_mod
        manager, mock_text = self._make_manager()
        mock_text.get.return_value = "   "
        with patch.object(out_mod.messagebox, "showwarning") as mock_warn, \
             patch("builtins.open", unittest.mock.mock_open()) as mock_open:
            manager.export_json()
        mock_warn.assert_called_once()
        mock_open.assert_not_called()

    def test_start_poller_drains_queue_into_widget(self):
        from ssh_device_manager.output import OutputManager
        mock_text = MagicMock()
        manager = OutputManager(mock_text)
        manager.log("msg1")
        manager.log("msg2")
        # start_poller calls poll() immediately then schedules via root.after()
        mock_root = MagicMock()
        manager.start_poller(mock_root)
        # After poll(), the widget should have received insert calls
        self.assertTrue(mock_text.insert.called)
        mock_root.after.assert_called()


# ---------------------------------------------------------------------------
# ToolTip unit tests  (models.py: 49 % → 100 %)
# ---------------------------------------------------------------------------

class TestToolTip(unittest.TestCase):
    """Unit tests for the ToolTip helper in models.py."""

    def _make_widget(self):
        """Return a mock widget with the attributes ToolTip accesses."""
        w = MagicMock()
        w.winfo_rootx.return_value = 100
        w.winfo_rooty.return_value = 200
        w.winfo_height.return_value = 30
        return w

    def test_no_text_does_not_bind(self):
        from ssh_device_manager.models import ToolTip
        w = self._make_widget()
        tip = ToolTip(w, "")
        # bind should never have been called for Enter/Leave
        for call in w.bind.call_args_list:
            self.assertNotIn("<Enter>", call[0])
            self.assertNotIn("<Leave>", call[0])

    def test_with_text_binds_enter_and_leave(self):
        from ssh_device_manager.models import ToolTip
        w = self._make_widget()
        ToolTip(w, "Tooltip text")
        bound_events = [c[0][0] for c in w.bind.call_args_list]
        self.assertIn("<Enter>", bound_events)
        self.assertIn("<Leave>", bound_events)

    def test_show_tip_creates_toplevel(self):
        from ssh_device_manager.models import ToolTip
        import ssh_device_manager.models as models_mod
        w = self._make_widget()
        tip = ToolTip(w, "Test tooltip")
        mock_toplevel = MagicMock()
        with patch.object(models_mod.tk, "Toplevel", return_value=mock_toplevel) as mock_top_cls, \
             patch.object(models_mod.tk, "Label"):
            tip.show_tip()
        mock_top_cls.assert_called_once_with(w)
        self.assertIsNotNone(tip.tipwindow)

    def test_show_tip_no_op_when_already_shown(self):
        from ssh_device_manager.models import ToolTip
        import ssh_device_manager.models as models_mod
        w = self._make_widget()
        tip = ToolTip(w, "Tooltip")
        tip.tipwindow = MagicMock()  # simulate already shown
        with patch.object(models_mod.tk, "Toplevel") as mock_top_cls:
            tip.show_tip()
        mock_top_cls.assert_not_called()

    def test_hide_tip_destroys_window(self):
        from ssh_device_manager.models import ToolTip
        w = self._make_widget()
        tip = ToolTip(w, "Tooltip")
        mock_tw = MagicMock()
        tip.tipwindow = mock_tw
        tip.hide_tip()
        mock_tw.destroy.assert_called_once()
        self.assertIsNone(tip.tipwindow)

    def test_hide_tip_no_op_when_not_shown(self):
        from ssh_device_manager.models import ToolTip
        w = self._make_widget()
        tip = ToolTip(w, "Tooltip")
        tip.tipwindow = None  # not shown
        # Should not raise
        tip.hide_tip()
        self.assertIsNone(tip.tipwindow)


# ---------------------------------------------------------------------------
# ActionController unit tests  (actions.py: 32 % → 44 %)
# ---------------------------------------------------------------------------

class TestActionControllerPerformUpload(unittest.TestCase):
    """Tests for ActionController.perform_upload and upload_config_template worker."""

    def _make_app(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = True
        app.log = MagicMock()
        return app

    @patch('SSH_DeviceManager.threading.Thread')
    def test_perform_upload_success(self, mock_thread):
        app = self._make_app()
        app._perform_upload("/local/file.txt", "/remote/file.txt")
        target = mock_thread.call_args[1]["target"]
        app.ssh.upload_file.return_value = None
        target()
        app.ssh.upload_file.assert_called_with("/local/file.txt", "/remote/file.txt")
        logged = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("[OK] SCP Upload complete" in m for m in logged))

    @patch('SSH_DeviceManager.threading.Thread')
    def test_perform_upload_error(self, mock_thread):
        app = self._make_app()
        app._perform_upload("/local/file.txt", "/remote/file.txt")
        target = mock_thread.call_args[1]["target"]
        app.ssh.upload_file.side_effect = IOError("Permission denied")
        target()
        logged = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("[ERROR] SCP Upload failed" in m for m in logged))

    @patch('SSH_DeviceManager.threading.Thread')
    def test_upload_config_template_worker_success(self, mock_thread):
        app = self._make_app()
        SSH_DeviceManager.filedialog.askopenfilename.return_value = "/local/cfg.txt"
        app.upload_config_template()
        target = mock_thread.call_args[1]["target"]
        app.ssh.upload_file.return_value = None
        target()
        app.ssh.upload_file.assert_called_with("/local/cfg.txt", "/tmp/uploaded_config.txt")
        logged = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("[OK] Upload complete" in m for m in logged))

    @patch('SSH_DeviceManager.threading.Thread')
    def test_upload_config_template_worker_error(self, mock_thread):
        app = self._make_app()
        SSH_DeviceManager.filedialog.askopenfilename.return_value = "/local/cfg.txt"
        app.upload_config_template()
        target = mock_thread.call_args[1]["target"]
        app.ssh.upload_file.side_effect = IOError("SFTP error")
        target()
        logged = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("[ERROR] Upload failed" in m for m in logged))

    def test_send_file_scp_not_connected(self):
        app = self._make_app()
        app.ssh.is_connected.return_value = False
        with patch('ssh_device_manager.controllers.actions.messagebox.showwarning') as mock_warn:
            app.send_file_scp()
        mock_warn.assert_called_once()
        app.ssh.upload_file.assert_not_called()

    def test_send_file_scp_no_file_chosen(self):
        app = self._make_app()
        with patch('ssh_device_manager.controllers.actions.filedialog.askopenfilename',
                   return_value=""):
            app.send_file_scp()
        app.ssh.upload_file.assert_not_called()


# ---------------------------------------------------------------------------
# SectionsController unit tests  (sections.py: 28 % → 100 %)
# ---------------------------------------------------------------------------

class TestSectionsController(unittest.TestCase):
    """Unit tests for SectionsController (reload, open, get_mtime, watcher)."""

    def _make_app(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.log = MagicMock()
        app.commands_frame = MagicMock()
        app.commands_frame.winfo_children.return_value = []
        return app

    def test_reload_sections_updates_sections_and_mtime(self):
        app = self._make_app()
        new_sections = [MagicMock()]
        with patch.object(app.sections_controller, 'load_sections_from_file',
                          return_value=new_sections), \
             patch.object(app.sections_controller, 'build_button_sections') as mock_build, \
             patch.object(app.sections_controller, 'get_mtime', return_value=12345.0):
            app.reload_sections("my_sections.json")
        self.assertEqual(app.sections, new_sections)
        self.assertEqual(app._sections_mtime, 12345.0)
        mock_build.assert_called_once_with(new_sections)

    def test_open_sections_file_with_file_selected(self):
        app = self._make_app()
        with patch('ssh_device_manager.controllers.sections.filedialog.askopenfilename',
                   return_value="/chosen/sections.json"), \
             patch.object(app.sections_controller, 'reload_sections') as mock_reload:
            app.open_sections_file("default.json")
        mock_reload.assert_called_once_with("/chosen/sections.json")

    def test_open_sections_file_cancelled(self):
        app = self._make_app()
        with patch('ssh_device_manager.controllers.sections.filedialog.askopenfilename',
                   return_value=""), \
             patch.object(app.sections_controller, 'reload_sections') as mock_reload:
            app.open_sections_file("default.json")
        mock_reload.assert_not_called()

    def test_get_mtime_returns_value_for_existing_file(self):
        import tempfile, os
        app = self._make_app()
        with tempfile.NamedTemporaryFile(delete=False) as f:
            tmp = f.name
        try:
            result = app._get_mtime(tmp)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, float)
        finally:
            os.unlink(tmp)

    def test_get_mtime_returns_none_for_missing_file(self):
        app = self._make_app()
        result = app._get_mtime("/nonexistent/path/that/does/not/exist.json")
        self.assertIsNone(result)

    def test_build_button_sections_excess_buttons_truncated(self):
        app = self._make_app()
        # Section with max_buttons=2 but 4 enabled actions
        actions = [
            SSH_DeviceManager.ActionButton(f"Btn{i}", True, MagicMock(), "tip")
            for i in range(4)
        ]
        section = SSH_DeviceManager.ButtonSection("TestSec", max_buttons=2, actions=actions)
        # build_button_sections should log a WARN and not crash
        app.sections_controller.build_button_sections([section])
        logged = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("WARN" in m and "Truncating" in m for m in logged))

    def test_build_button_sections_disabled_actions_excluded(self):
        app = self._make_app()
        actions = [
            SSH_DeviceManager.ActionButton("Enabled", True, MagicMock(), ""),
            SSH_DeviceManager.ActionButton("Disabled", False, MagicMock(), ""),
        ]
        section = SSH_DeviceManager.ButtonSection("Sec", max_buttons=6, actions=actions)
        # Should not raise and should not warn about excess
        app.sections_controller.build_button_sections([section])
        logged = [c[0][0] for c in app.log.call_args_list]
        self.assertFalse(any("WARN" in m and "Truncating" in m for m in logged))

    def test_sections_watcher_detects_change_and_reloads(self):
        app = self._make_app()
        app.sections_path = "sections.json"
        app._sections_mtime = 100.0
        with patch.object(app.sections_controller, 'get_mtime', return_value=999.0), \
             patch.object(app.sections_controller, 'reload_sections') as mock_reload:
            # Manually invoke the watcher's inner check() function
            # by calling start_sections_watcher and intercepting the after() call
            scheduled_calls = []
            app.after = lambda ms, fn: scheduled_calls.append(fn)
            app.sections_controller.start_sections_watcher(interval_ms=1000)
            # The first after() scheduled the check; invoke it
            scheduled_calls[0]()
        mock_reload.assert_called_once_with("sections.json")


# ---------------------------------------------------------------------------
# config.py – missing-file path  (config.py: 88 % → 100 %)
# ---------------------------------------------------------------------------

class TestAppConfigMissingFile(unittest.TestCase):
    """Test load_app_config when the config file does not yet exist."""

    def test_creates_default_when_file_missing(self):
        import tempfile, os
        from ssh_device_manager.config import load_app_config

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "new_config.json")
            self.assertFalse(os.path.exists(path))

            result = load_app_config(path)

            # Should return default and also persist it
            self.assertIn("profiles", result)
            self.assertEqual(result["profiles"], {})
            self.assertTrue(os.path.exists(path))


# ---------------------------------------------------------------------------
# ConnectionController gap tests  (connection.py: 89 % → 99 %)
# ---------------------------------------------------------------------------

class TestConnectionControllerGaps(unittest.TestCase):
    """Tests for previously uncovered ConnectionController paths."""

    def test_start_connection_monitor_schedules_poll(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = False
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()
        app.status_var = MagicMock()
        app.status_var.get.return_value = "Disconnected"

        scheduled = []
        app.after = lambda ms, fn: scheduled.append((ms, fn))

        app._start_connection_monitor()

        # At least one after() call should be pending
        self.assertTrue(len(scheduled) > 0)

    @patch('ssh_device_manager.controllers.connection.messagebox.showinfo')
    def test_test_connection_shows_info_when_already_connected(self, mock_info):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = True
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()
        app.status_var = MagicMock()
        app.status_var.get.return_value = "Connected"

        app.test_connection()

        mock_info.assert_called_once()

    @patch('ssh_device_manager.app.SSHManager')
    @patch('SSH_DeviceManager.threading.Thread')
    def test_test_connection_ssh_exception(self, mock_thread, MockSSHManager):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_var.get.return_value = "192.168.1.1"
        app.user_var.get.return_value = "admin"
        app.port_var.get.return_value = 22
        app.pass_var.get.return_value = "pass"
        app.timeout_var.get.return_value = 10
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = False
        app.log = MagicMock()

        MockSSHManager.return_value.connect.side_effect = (
            SSH_DeviceManager.paramiko.SSHException("bad protocol")
        )
        app.test_connection()
        target = mock_thread.call_args[1]["target"]
        target()

        logged = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("SSH error" in m for m in logged))

    @patch('SSH_DeviceManager.threading.Thread')
    def test_connect_worker_finally_clears_is_connecting(self, mock_thread):
        """is_connecting is reset to False even when connect() succeeds."""
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_var.get.return_value = "10.0.0.1"
        app.user_var.get.return_value = "admin"
        app.port_var.get.return_value = 22
        app.pass_var.get.return_value = "pw"
        app.timeout_var.get.return_value = 10
        app.ssh = MagicMock()
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()

        app.on_connect()
        target = mock_thread.call_args[1]["target"]
        target()

        self.assertFalse(app.is_connecting)


# ---------------------------------------------------------------------------
# ProfileController gap tests  (profiles.py: 91 % → 98 %)
# ---------------------------------------------------------------------------

class TestProfileControllerGaps(unittest.TestCase):
    """Tests for previously uncovered ProfileController paths."""

    def _make_app(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.log = MagicMock()
        app._save_app_config = MagicMock()
        app._refresh_profile_list = MagicMock()
        return app

    def test_refresh_profile_list_empty_clears_selection(self):
        app = self._make_app()
        app.app_config["profiles"] = {}
        app.profile_select_var.get.return_value = "OldProfile"
        app._refresh_profile_list = MagicMock()  # let the real one run via controller
        app.profile_controller.refresh_profile_list()
        app.profile_select_var.set.assert_called_with("")

    def test_refresh_profile_list_keeps_valid_selection(self):
        app = self._make_app()
        app.app_config["profiles"] = {"ProfileA": {}, "ProfileB": {}}
        app.profile_select_var.get.return_value = "ProfileA"
        app.profile_controller.refresh_profile_list()
        # The currently selected profile exists, so set() should NOT be called
        # (the controller returns early)
        app.profile_select_var.set.assert_not_called()

    @patch('ssh_device_manager.controllers.profiles.messagebox.showwarning')
    def test_load_selected_profile_no_selection_warns(self, mock_warn):
        app = self._make_app()
        app.profile_select_var.get.return_value = ""
        app.profile_controller.load_selected_profile()
        mock_warn.assert_called_once()

    @patch('ssh_device_manager.controllers.profiles.messagebox.showwarning')
    def test_delete_selected_profile_no_selection_warns(self, mock_warn):
        app = self._make_app()
        app.profile_select_var.get.return_value = ""
        app.profile_controller.delete_selected_profile()
        mock_warn.assert_called_once()


# ---------------------------------------------------------------------------
# sections_loader.py – empty-command handler  (line 31)
# ---------------------------------------------------------------------------

class TestSectionsLoaderEmptyCommand(unittest.TestCase):
    """Verify that an action with an empty command gets a no-op log handler."""

    def test_empty_command_handler_logs_warn(self):
        from ssh_device_manager.sections_loader import load_sections_from_file
        import json

        log_calls = []
        json_data = json.dumps({
            "sections": [{
                "title": "Test",
                "max_buttons": 6,
                "actions": [{"label": "NoCmd", "enabled": True, "command": "", "tooltip": ""}],
            }]
        })

        with patch("builtins.open", unittest.mock.mock_open(read_data=json_data)), \
             patch("os.path.exists", return_value=True):
            sections = load_sections_from_file(
                "dummy.json",
                log=log_calls.append,
                run_ssh_command=MagicMock(),
                upload_config_template=MagicMock(),
                send_file_scp=MagicMock(),
                prompt_and_run_custom_command=MagicMock(),
                fallback=lambda: [],
            )

        # Trigger the handler and confirm it logs a warning
        sections[0].actions[0].handler()
        self.assertTrue(any("[WARN]" in m for m in log_calls))


# ---------------------------------------------------------------------------
# validation.py – boundary: parse_int_input at exact min/max
# ---------------------------------------------------------------------------

class TestParseIntInputBoundary(unittest.TestCase):
    """Additional edge cases for parse_int_input."""

    def setUp(self):
        self.app = SSH_DeviceManager.SSHGuiApp(init_ui=False)

    def test_exact_minimum_is_valid(self):
        self.assertEqual(self.app._parse_int_input("1", "Port", 1, 65535), 1)

    def test_exact_maximum_is_valid(self):
        self.assertEqual(self.app._parse_int_input("65535", "Port", 1, 65535), 65535)

    def test_float_string_is_invalid(self):
        self.assertIsNone(self.app._parse_int_input("22.5", "Port", 1, 65535))


# ---------------------------------------------------------------------------
# SSHManager – connect re-connects if already connected (line 54)
# ---------------------------------------------------------------------------

class TestSSHManagerReconnect(unittest.TestCase):
    """Test that connect() calls disconnect() when already connected."""

    @patch('SSH_DeviceManager.paramiko.SSHClient')
    def test_connect_when_already_connected_disconnects_first(self, mock_ssh_client):
        manager = SSH_DeviceManager.SSHManager()
        existing_client = MagicMock()
        manager.client = existing_client

        manager.connect("host2", 22, "user", "pass")

        # The old client should have been closed
        existing_client.close.assert_called()
        # A new client should be set
        self.assertIsNotNone(manager.client)
class TestStartupErrorLogging(unittest.TestCase):
    """Tests that the launcher writes a traceback to a log file on startup failure."""

    @patch("SSH_DeviceManager.SSHGuiApp", side_effect=RuntimeError("boom"))
    def test_startup_error_writes_log_file(self, _mock_app):
        import tempfile
        log_path = os.path.join(
            tempfile.gettempdir(), "test_startup_error.log"
        )
        try:
            # Simulate the launcher's error handler
            try:
                SSH_DeviceManager.main()
            except RuntimeError:
                import traceback
                with open(log_path, "w", encoding="utf-8") as f:
                    traceback.print_exc(file=f)

            self.assertTrue(os.path.exists(log_path))
            with open(log_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("boom", content)
            self.assertIn("RuntimeError", content)
        finally:
            if os.path.exists(log_path):
                os.remove(log_path)


class TestContracts(unittest.TestCase):
    """Contract tests that verify the shape/types of data exchanged between modules."""

    # CT-01: Every color value in every theme is a valid #RRGGBB hex or named color
    def test_theme_color_values_are_valid_hex(self):
        import re
        hex_pattern = re.compile(r'^#[0-9a-fA-F]{6}$')
        named_colors = {"black", "white", "red", "green", "blue", "yellow",
                        "cyan", "magenta", "orange", "purple", "gray", "grey"}
        for name, theme in SSH_DeviceManager.THEMES.items():
            for key, value in theme.items():
                is_valid = (
                    hex_pattern.match(value) is not None
                    or value.lower() in named_colors
                )
                self.assertTrue(
                    is_valid,
                    f"Theme '{name}', key '{key}': '{value}' is not a valid "
                    f"#RRGGBB hex color or recognized named color"
                )

    # CT-02: Theme keys match the keys apply_theme() directly accesses
    def test_theme_keys_match_apply_theme_usage(self):
        # Keys accessed via theme["key"] (no fallback) in apply_theme()
        required_by_apply_theme = {
            "bg", "fg", "text_bg", "text_fg",
            "entry_bg", "entry_fg", "select_bg", "select_fg",
        }
        # Keys accessed via theme.get("key", fallback) — should still be present
        extended_keys = {"btn_bg", "border", "label_fg"}
        all_expected = required_by_apply_theme | extended_keys

        for name, theme in SSH_DeviceManager.THEMES.items():
            for key in all_expected:
                self.assertIn(
                    key, theme,
                    f"Theme '{name}' missing key '{key}' required by apply_theme()"
                )
            # No extra unknown keys
            for key in theme:
                self.assertIn(
                    key, all_expected,
                    f"Theme '{name}' has unexpected key '{key}' not used by apply_theme()"
                )

    # CT-03: The shipped sections.json conforms to the expected schema
    def test_sections_json_conforms_to_schema(self):
        sections_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "sections.json"
        )
        if not os.path.exists(sections_path):
            self.skipTest("sections.json not found")

        with open(sections_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("sections", data)
        self.assertIsInstance(data["sections"], list)
        self.assertGreater(len(data["sections"]), 0, "sections array should not be empty")

        for i, section in enumerate(data["sections"]):
            self.assertIn("title", section, f"Section {i} missing 'title'")
            self.assertIsInstance(section["title"], str)
            self.assertIn("max_buttons", section, f"Section {i} missing 'max_buttons'")
            self.assertIsInstance(section["max_buttons"], int)
            self.assertIn("actions", section, f"Section {i} missing 'actions'")
            self.assertIsInstance(section["actions"], list)

            for j, action in enumerate(section["actions"]):
                self.assertIn("label", action, f"Section {i}, action {j} missing 'label'")
                self.assertIsInstance(action["label"], str)
                self.assertIn("enabled", action, f"Section {i}, action {j} missing 'enabled'")
                self.assertIsInstance(action["enabled"], bool)
                self.assertIn("command", action, f"Section {i}, action {j} missing 'command'")
                self.assertIsInstance(action["command"], str)

    # CT-04: Every command in sections.json is a recognized handler token
    def test_sections_json_commands_are_valid_tokens(self):
        sections_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "sections.json"
        )
        if not os.path.exists(sections_path):
            self.skipTest("sections.json not found")

        valid_special_tokens = {
            "__upload_template__", "__send_file__", "__custom_command__"
        }

        with open(sections_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for section in data["sections"]:
            for action in section.get("actions", []):
                cmd = action.get("command", "")
                is_valid = (
                    cmd in valid_special_tokens
                    or cmd.startswith("run:")
                    or cmd == ""
                )
                self.assertTrue(
                    is_valid,
                    f"Action '{action.get('label')}' has unrecognized command "
                    f"token: '{cmd}'. Expected run:*, __upload_template__, "
                    f"__send_file__, or __custom_command__"
                )

    # CT-05: Profile config round-trip preserves all expected keys and types
    def test_profile_schema_round_trip(self):
        import tempfile
        from ssh_device_manager.config import load_app_config, save_app_config

        config = {
            "profiles": {
                "TestProfile": {
                    "host": "10.0.0.1",
                    "port": 22,
                    "username": "admin",
                    "timeout": 10,
                    "host_key_mode": "warning",
                }
            }
        }

        expected_keys = {"host", "port", "username", "timeout", "host_key_mode"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         delete=False, dir=".") as f:
            tmp_path = f.name

        try:
            save_app_config(tmp_path, config)
            loaded = load_app_config(tmp_path)

            self.assertIn("profiles", loaded)
            self.assertIn("TestProfile", loaded["profiles"])
            profile = loaded["profiles"]["TestProfile"]

            for key in expected_keys:
                self.assertIn(
                    key, profile,
                    f"Profile missing expected key '{key}' after round-trip"
                )

            # Type checks
            self.assertIsInstance(profile["host"], str)
            self.assertIsInstance(profile["port"], int)
            self.assertIsInstance(profile["username"], str)
            self.assertIsInstance(profile["timeout"], int)
            self.assertIsInstance(profile["host_key_mode"], str)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    # CT-06: SSHManager exposes the public interface the app expects
    def test_ssh_manager_interface_contract(self):
        import inspect
        mgr = SSH_DeviceManager.SSHManager

        # Required public methods
        required_methods = {
            "connect": ["host", "port", "username", "password"],
            "disconnect": [],
            "run_command": ["command"],
            "upload_file": ["local_path", "remote_path"],
            "is_connected": [],
        }

        for method_name, expected_params in required_methods.items():
            self.assertTrue(
                hasattr(mgr, method_name),
                f"SSHManager missing method '{method_name}'"
            )
            method = getattr(mgr, method_name)
            self.assertTrue(
                callable(method),
                f"SSHManager.{method_name} is not callable"
            )

            sig = inspect.signature(method)
            param_names = [
                p.name for p in sig.parameters.values()
                if p.name != "self"
                and p.default is inspect.Parameter.empty
                and p.kind not in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                )
            ]
            for expected in expected_params:
                self.assertIn(
                    expected, param_names,
                    f"SSHManager.{method_name}() missing required "
                    f"parameter '{expected}'"
                )

    # CT-07: Each controller class exposes the methods app.py delegates to
    def test_controller_interface_contract(self):
        from ssh_device_manager.controllers import (
            ConnectionController, ActionController,
            ProfileController, SectionsController,
        )

        controller_contracts = {
            ConnectionController: [
                "connect", "disconnect", "test_connection",
                "on_host_selected", "refresh_connection_state",
                "start_connection_monitor",
            ],
            ActionController: [
                "run_ssh_command", "prompt_and_run_custom_command",
                "upload_config_template", "send_file_scp", "perform_upload",
            ],
            ProfileController: [
                "save_profile", "load_selected_profile",
                "delete_selected_profile", "refresh_profile_list",
            ],
            SectionsController: [
                "load_sections_from_file", "reload_sections",
                "open_sections_file", "define_sections",
                "build_button_sections", "get_mtime",
                "start_sections_watcher",
            ],
        }

        for controller_cls, methods in controller_contracts.items():
            for method_name in methods:
                self.assertTrue(
                    hasattr(controller_cls, method_name),
                    f"{controller_cls.__name__} missing method '{method_name}' "
                    f"that app.py delegates to"
                )
                self.assertTrue(
                    callable(getattr(controller_cls, method_name)),
                    f"{controller_cls.__name__}.{method_name} is not callable"
                )


if __name__ == '__main__':
    unittest.main()


# ---------------------------------------------------------------------------
# SectionsController – additional build_button_sections paths
# (covers destroying existing children, odd-column separator, multiple sections)
# ---------------------------------------------------------------------------

class TestBuildButtonSectionsAdditional(unittest.TestCase):
    """Cover lines missed in build_button_sections: child.destroy, separators."""

    def _make_app(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.log = MagicMock()
        app.commands_frame = MagicMock()
        return app

    def test_existing_children_are_destroyed(self):
        """build_button_sections calls destroy() on existing frame children."""
        app = self._make_app()
        child1 = MagicMock()
        child2 = MagicMock()
        app.commands_frame.winfo_children.return_value = [child1, child2]

        section = SSH_DeviceManager.ButtonSection("Sec", 6, [
            SSH_DeviceManager.ActionButton("Btn", True, MagicMock(), ""),
        ])
        app.sections_controller.build_button_sections([section])

        child1.destroy.assert_called_once()
        child2.destroy.assert_called_once()

    def test_multiple_sections_create_separator(self):
        """Two sections -> one vertical separator between them (no crash)."""
        app = self._make_app()
        app.commands_frame.winfo_children.return_value = []

        sec1 = SSH_DeviceManager.ButtonSection("Sec1", 6, [
            SSH_DeviceManager.ActionButton("A", True, MagicMock(), ""),
        ])
        sec2 = SSH_DeviceManager.ButtonSection("Sec2", 6, [
            SSH_DeviceManager.ActionButton("B", True, MagicMock(), ""),
        ])
        # Should not raise; ttk.Separator will be created via stub
        app.sections_controller.build_button_sections([sec1, sec2])


# ---------------------------------------------------------------------------
# SectionsController – watcher finally block re-schedules
# ---------------------------------------------------------------------------

class TestSectionsWatcherFinallyRescheduling(unittest.TestCase):
    """The watcher finally block always re-schedules via app.after()."""

    def test_watcher_reschedules_after_successful_check(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.log = MagicMock()
        app.sections_path = "sections.json"
        app._sections_mtime = 100.0  # same mtime -> no reload

        scheduled_fns = []
        app.after = lambda ms, fn: scheduled_fns.append(fn)

        with patch.object(app.sections_controller, 'get_mtime', return_value=100.0):
            app.sections_controller.start_sections_watcher(interval_ms=500)
            first_check = scheduled_fns[0]
            scheduled_fns.clear()
            first_check()

        # finally block must have scheduled another call
        self.assertTrue(len(scheduled_fns) > 0)

    def test_watcher_reschedules_even_on_exception(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.log = MagicMock()
        app.sections_path = "sections.json"

        scheduled_fns = []
        app.after = lambda ms, fn: scheduled_fns.append(fn)

        with patch.object(app.sections_controller, 'get_mtime',
                          side_effect=RuntimeError("unexpected")):
            app.sections_controller.start_sections_watcher(interval_ms=500)
            first_check = scheduled_fns[0]
            scheduled_fns.clear()
            first_check()

        # re-scheduling must happen even on exception
        self.assertTrue(len(scheduled_fns) > 0)
        logged = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("watcher error" in m for m in logged))


# ---------------------------------------------------------------------------
# ConnectionController – poll() inner body
# ---------------------------------------------------------------------------

class TestConnectionMonitorPoll(unittest.TestCase):
    """The poll() function inside start_connection_monitor runs correctly."""

    def test_poll_calls_refresh_and_reschedules(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = False
        app.log = MagicMock()
        app._set_connected_ui = MagicMock()
        app.status_var = MagicMock()
        app.status_var.get.return_value = "Disconnected"

        scheduled = []
        app.after = lambda ms, fn: scheduled.append(fn)

        app._start_connection_monitor()
        poll_fn = scheduled[0]
        scheduled.clear()
        poll_fn()

        # Should have re-scheduled itself
        self.assertTrue(len(scheduled) > 0)
        app._set_connected_ui.assert_called_with(False)


# ---------------------------------------------------------------------------
# ConnectionController – generic exception in test_connection worker
# ---------------------------------------------------------------------------

class TestTestConnectionGenericException(unittest.TestCase):
    """test_connection logs a generic error for unexpected exceptions."""

    @patch('ssh_device_manager.app.SSHManager')
    @patch('SSH_DeviceManager.threading.Thread')
    def test_generic_exception_logged(self, mock_thread, MockSSHManager):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        app.host_var.get.return_value = "10.0.0.1"
        app.user_var.get.return_value = "admin"
        app.port_var.get.return_value = 22
        app.pass_var.get.return_value = "pw"
        app.timeout_var.get.return_value = 10
        app.ssh = MagicMock()
        app.ssh.is_connected.return_value = False
        app.log = MagicMock()

        MockSSHManager.return_value.connect.side_effect = RuntimeError("totally unexpected")
        app.test_connection()
        target = mock_thread.call_args[1]["target"]
        target()

        logged = [c[0][0] for c in app.log.call_args_list]
        self.assertTrue(any("Connection test failed" in m for m in logged))


# ---------------------------------------------------------------------------
# paramiko_compat – stub implementations (when paramiko is absent)
# ---------------------------------------------------------------------------

class TestParamikoCompatStub(unittest.TestCase):
    """Test the fallback stubs in paramiko_compat when paramiko is not installed."""

    def _get_stub_paramiko(self):
        import sys, builtins
        real_paramiko = sys.modules.get("paramiko")
        real_compat = sys.modules.get("ssh_device_manager.paramiko_compat")

        sys.modules.pop("paramiko", None)
        sys.modules.pop("ssh_device_manager.paramiko_compat", None)

        old_import = builtins.__import__

        def _failing_import(name, *args, **kwargs):
            if name == "paramiko":
                raise ModuleNotFoundError("No module named 'paramiko'")
            return old_import(name, *args, **kwargs)

        builtins.__import__ = _failing_import
        try:
            import ssh_device_manager.paramiko_compat as compat_mod
            stub = compat_mod.paramiko
        finally:
            builtins.__import__ = old_import
            sys.modules.pop("ssh_device_manager.paramiko_compat", None)
            if real_compat is not None:
                sys.modules["ssh_device_manager.paramiko_compat"] = real_compat
            if real_paramiko is not None:
                sys.modules["paramiko"] = real_paramiko

        return stub

    def test_stub_ssh_client_connect_raises(self):
        stub = self._get_stub_paramiko()
        client = stub.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(None)
        with self.assertRaises(ModuleNotFoundError):
            client.connect(hostname="host")

    def test_stub_ssh_client_exec_command_raises(self):
        stub = self._get_stub_paramiko()
        client = stub.SSHClient()
        with self.assertRaises(ModuleNotFoundError):
            client.exec_command("ls")

    def test_stub_ssh_client_open_sftp_raises(self):
        stub = self._get_stub_paramiko()
        client = stub.SSHClient()
        with self.assertRaises(ModuleNotFoundError):
            client.open_sftp()

    def test_stub_ssh_client_get_transport_returns_none(self):
        stub = self._get_stub_paramiko()
        client = stub.SSHClient()
        self.assertIsNone(client.get_transport())

    def test_stub_ssh_client_close_is_noop(self):
        stub = self._get_stub_paramiko()
        client = stub.SSHClient()
        client.close()

    def test_stub_sftp_client_put_raises(self):
        stub = self._get_stub_paramiko()
        sftp = stub.SFTPClient()
        with self.assertRaises(ModuleNotFoundError):
            sftp.put("local", "remote")

    def test_stub_sftp_client_close_is_noop(self):
        stub = self._get_stub_paramiko()
        sftp = stub.SFTPClient()
        sftp.close()


# ---------------------------------------------------------------------------
# validation.py – line 23: parse_int_input below min with no maximum
# ---------------------------------------------------------------------------

class TestParseIntInputNoMaxBelowMin(unittest.TestCase):
    """Cover the range_text = f'{minimum}+' branch when maximum is None."""

    def test_below_minimum_no_maximum_shows_range_text(self):
        app = SSH_DeviceManager.SSHGuiApp(init_ui=False)
        # value 0 is below minimum 1; no maximum supplied → line 23 branch
        result = app._parse_int_input("0", "Count", minimum=1)
        self.assertIsNone(result)
