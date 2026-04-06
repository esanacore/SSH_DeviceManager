import sys
import types
import unittest
from unittest.mock import MagicMock, patch

# =========================================================================
# Minimal Tkinter Mock
# =========================================================================
# We mock tkinter before importing customizer.py so that we can instantiate
# the app and test its logic without triggering a real graphical display.

tk = types.ModuleType('tkinter')
ttk = types.ModuleType('tkinter.ttk')
messagebox = types.ModuleType('tkinter.messagebox')
simpledialog = types.ModuleType('tkinter.simpledialog')
filedialog = types.ModuleType('tkinter.filedialog')

class DummyWidget(MagicMock):
    def __init__(self, *a, **k):
        super().__init__()
    def pack(self, *a, **k): pass
    def grid(self, *a, **k): pass
    def bind(self, *a, **k): pass
    def insert(self, *a, **k): pass
    def delete(self, *a, **k): pass
    def winfo_children(self, *a, **k): return []
    def curselection(self): return []

class DummyTk(DummyWidget):
    def __init__(self, *a, **k):
        super().__init__()
    def title(self, *a, **k): pass
    def geometry(self, *a, **k): pass
    def mainloop(self, *a, **k): pass

tk.Tk = DummyTk
tk.StringVar = MagicMock
tk.IntVar = MagicMock
tk.Listbox = DummyWidget
tk.END = "end"

ttk.Frame = DummyWidget
ttk.Label = DummyWidget
ttk.Button = DummyWidget
ttk.Entry = DummyWidget
ttk.Spinbox = DummyWidget
ttk.Separator = DummyWidget

sys.modules['tkinter'] = tk
sys.modules['tkinter.ttk'] = ttk
sys.modules['tkinter.messagebox'] = messagebox
sys.modules['tkinter.simpledialog'] = simpledialog
sys.modules['tkinter.filedialog'] = filedialog

filedialog.askopenfilename = MagicMock(return_value='')
filedialog.asksaveasfilename = MagicMock(return_value='')
messagebox.showinfo = MagicMock()
messagebox.showwarning = MagicMock()
messagebox.showerror = MagicMock()
messagebox.askyesno = MagicMock(return_value=False)
simpledialog.askstring = MagicMock(return_value=None)

# Now we can safely import the customizer app
import customizer


# =========================================================================
# Unit Tests
# =========================================================================

class TestCustomizerApp(unittest.TestCase):

    @patch('customizer.open', new_callable=unittest.mock.mock_open, read_data='{"sections": [{"title": "Test"}]}')
    def test_load_config_on_init(self, mock_open):
        """Tests that the customizer loads sections.json correctly on startup."""
        app = customizer.CustomizerApp()
        self.assertEqual(len(app.config_data["sections"]), 1)
        self.assertEqual(app.config_data["sections"][0]["title"], "Test")

    @patch('customizer.open', side_effect=FileNotFoundError)
    def test_load_config_fallback(self, mock_open):
        """Tests fallback to empty data if sections.json is missing."""
        app = customizer.CustomizerApp()
        self.assertEqual(app.config_data, {"sections": []})

    def test_add_section(self):
        """Tests adding a new section via dialog."""
        app = customizer.CustomizerApp()
        app.config_data = {"sections": []}
        
        with patch('customizer.simpledialog.askstring', return_value="New Section"):
            app.add_section()
            
        self.assertEqual(len(app.config_data["sections"]), 1)
        self.assertEqual(app.config_data["sections"][0]["title"], "New Section")
        self.assertEqual(app.config_data["sections"][0]["max_buttons"], 6)
        self.assertEqual(app.config_data["sections"][0]["actions"], [])

    def test_add_section_cancelled(self):
        """Tests adding a section when dialog is cancelled."""
        app = customizer.CustomizerApp()
        app.config_data = {"sections": []}
        
        with patch('customizer.simpledialog.askstring', return_value=None):
            app.add_section()
            
        self.assertEqual(len(app.config_data["sections"]), 0)

    def test_remove_section(self):
        """Tests removing a section when confirmed."""
        app = customizer.CustomizerApp()
        app.config_data = {"sections": [{"title": "Sec1"}, {"title": "Sec2"}]}
        
        with patch.object(app, 'section_index', return_value=0), \
             patch('customizer.messagebox.askyesno', return_value=True):
            app.remove_section()
            
        self.assertEqual(len(app.config_data["sections"]), 1)
        self.assertEqual(app.config_data["sections"][0]["title"], "Sec2")

    def test_remove_section_cancelled(self):
        """Tests removing a section when rejected/cancelled."""
        app = customizer.CustomizerApp()
        app.config_data = {"sections": [{"title": "Sec1"}]}
        
        with patch.object(app, 'section_index', return_value=0), \
             patch('customizer.messagebox.askyesno', return_value=False):
            app.remove_section()
            
        self.assertEqual(len(app.config_data["sections"]), 1)

    def test_update_section(self):
        """Tests updating a section's title and max buttons from UI fields."""
        app = customizer.CustomizerApp()
        app.config_data = {"sections": [{"title": "Sec1", "max_buttons": 6}]}
        
        app.title_var.get.return_value = "Updated Sec1"
        app.max_var.get.return_value = 10
        
        with patch.object(app, 'section_index', return_value=0):
            app.update_section()
            
        self.assertEqual(app.config_data["sections"][0]["title"], "Updated Sec1")
        self.assertEqual(app.config_data["sections"][0]["max_buttons"], 10)

    def test_add_action(self):
        """Tests adding an action button to a selected section."""
        app = customizer.CustomizerApp()
        app.config_data = {"sections": [{"title": "Sec1", "actions": []}]}
        
        with patch.object(app, 'section_index', return_value=0), \
             patch('customizer.simpledialog.askstring', side_effect=["My Action", "run:ls"]):
            app.add_action()
            
        actions = app.config_data["sections"][0]["actions"]
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["label"], "My Action")
        self.assertEqual(actions[0]["command"], "run:ls")
        self.assertTrue(actions[0]["enabled"])

    def test_add_action_no_section_selected(self):
        """Tests adding an action fails safely if no section is selected."""
        app = customizer.CustomizerApp()
        app.config_data = {"sections": [{"title": "Sec1", "actions": []}]}
        
        with patch.object(app, 'section_index', return_value=None), \
             patch('customizer.messagebox.showwarning') as mock_warn:
            app.add_action()
            
        mock_warn.assert_called_once()
        self.assertEqual(len(app.config_data["sections"][0]["actions"]), 0)

    def test_remove_action(self):
        """Tests removing a specific action button."""
        app = customizer.CustomizerApp()
        app.config_data = {"sections": [
            {"title": "Sec1", "actions": [{"label": "A1"}, {"label": "A2"}]}
        ]}
        
        with patch.object(app, 'section_index', return_value=0), \
             patch.object(app, 'action_index', return_value=0):
            app.remove_action()
            
        actions = app.config_data["sections"][0]["actions"]
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["label"], "A2")

    def test_edit_action(self):
        """Tests editing an existing action button."""
        app = customizer.CustomizerApp()
        app.config_data = {"sections": [
            {"title": "Sec1", "actions": [
                {"label": "A1", "command": "c1", "tooltip": "t1", "enabled": False}
            ]}
        ]}
        
        with patch.object(app, 'section_index', return_value=0), \
             patch.object(app, 'action_index', return_value=0), \
             patch('customizer.simpledialog.askstring', side_effect=["NewA1", "new_c1", "new_t1"]), \
             patch('customizer.messagebox.askyesno', return_value=True):
            app.edit_action()
            
        action = app.config_data["sections"][0]["actions"][0]
        self.assertEqual(action["label"], "NewA1")
        self.assertEqual(action["command"], "new_c1")
        self.assertEqual(action["tooltip"], "new_t1")
        self.assertTrue(action["enabled"])

    @patch('customizer.filedialog.askopenfilename', return_value="/fake/load.json")
    @patch('customizer.open', new_callable=unittest.mock.mock_open, read_data='{"sections": [{"title": "LoadedData"}]}')
    def test_load_config_dialog(self, mock_open, mock_askopenfilename):
        """Tests loading configuration from a user-selected file."""
        app = customizer.CustomizerApp()
        
        app.load_config_dialog()
        
        mock_askopenfilename.assert_called_once()
        self.assertEqual(app.config_data["sections"][0]["title"], "LoadedData")

    @patch('customizer.filedialog.asksaveasfilename', return_value="/fake/path.json")
    @patch('customizer.open', new_callable=unittest.mock.mock_open)
    def test_save_config(self, mock_open, mock_asksaveasfilename):
        """Tests writing the configuration data to a user-selected file."""
        app = customizer.CustomizerApp()
        mock_open.reset_mock()  # ignore the open() call made by load_config during __init__
        app.config_data = {"sections": [{"title": "SaveMe"}]}
        
        app.save_config()
        
        mock_asksaveasfilename.assert_called_once()
        mock_open.assert_called_once_with("/fake/path.json", "w", encoding="utf-8")
        
        # Verify that json.dump actually wrote the dictionary properly
        handle = mock_open()
        written = "".join(call.args[0] for call in handle.write.mock_calls)
        self.assertIn("SaveMe", written)
