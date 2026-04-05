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

import SSH_DeviceManager

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

    def test_is_connected(self):
        self.assertFalse(self.ssh_manager.is_connected())
        self.ssh_manager.client = MagicMock()
        self.assertTrue(self.ssh_manager.is_connected())

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
    def test_upload_file(self, mock_ssh_client):
        mock_client_instance = mock_ssh_client.return_value
        self.ssh_manager.client = mock_client_instance
        mock_sftp = MagicMock()
        mock_client_instance.open_sftp.return_value = mock_sftp
        
        self.ssh_manager.upload_file("local", "remote")
        
        self.assertIsNotNone(self.ssh_manager.sftp)
        mock_sftp.put.assert_called_with("local", "remote")

class TestSSHGuiApp(unittest.TestCase):
    @patch('SSH_DeviceManager.SSHManager')
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
        with patch('SSH_DeviceManager.SSHManager') as MockSSHManager:
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

if __name__ == '__main__':
    unittest.main()
