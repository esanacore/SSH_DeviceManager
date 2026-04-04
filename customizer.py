import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

CONFIG_PATH = "sections.json"

class CustomizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SSH Device Manager Customizer")
        self.geometry("900x600")
        self.config_data = {"sections": []}
        self._build_ui()
        self.load_config(CONFIG_PATH)

    def _build_ui(self):
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=8, pady=8)
        right = ttk.Frame(self)
        right.pack(side="right", fill="both", expand=True, padx=8, pady=8)

        # Section list
        ttk.Label(left, text="Sections").pack(anchor="w")
        self.section_list = tk.Listbox(left, height=20, width=28)
        self.section_list.pack(padx=4, pady=4)
        self.section_list.bind("<<ListboxSelect>>", self.on_select_section)

        ttk.Button(left, text="Add Section", command=self.add_section).pack(fill="x", pady=2)
        ttk.Button(left, text="Remove Section", command=self.remove_section).pack(fill="x", pady=2)
        ttk.Button(left, text="Load...", command=self.load_config_dialog).pack(fill="x", pady=6)
        ttk.Button(left, text="Save", command=self.save_config).pack(fill="x", pady=2)

        # Editor for section/buttons
        editor = ttk.Frame(left)
        editor.pack(fill="x", pady=8)

        ttk.Label(editor, text="Title").pack(anchor="w")
        self.title_var = tk.StringVar()
        ttk.Entry(editor, textvariable=self.title_var).pack(fill="x", pady=2)

        ttk.Label(editor, text="Max Buttons").pack(anchor="w")
        self.max_var = tk.IntVar(value=6)
        ttk.Spinbox(editor, from_=1, to=12, textvariable=self.max_var).pack(fill="x", pady=2)

        ttk.Button(editor, text="Update Section", command=self.update_section).pack(fill="x", pady=6)

        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=6)

        ttk.Label(left, text="Actions (buttons)").pack(anchor="w")
        self.action_list = tk.Listbox(left, height=10, width=28)
        self.action_list.pack(padx=4, pady=4)
        self.action_list.bind("<<ListboxSelect>>", self.on_select_action)

        ttk.Button(left, text="Add Action", command=self.add_action).pack(fill="x", pady=2)
        ttk.Button(left, text="Remove Action", command=self.remove_action).pack(fill="x", pady=2)
        ttk.Button(left, text="Edit Action", command=self.edit_action).pack(fill="x", pady=2)

        # Preview area on the right
        ttk.Label(right, text="Live Preview").pack(anchor="w")
        self.preview_area = ttk.Frame(right)
        self.preview_area.pack(fill="both", expand=True, padx=4, pady=4)

    def refresh_lists(self):
        self.section_list.delete(0, "end")
        for s in self.config_data.get("sections", []):
            self.section_list.insert("end", s.get("title", "Untitled"))
        self.action_list.delete(0, "end")

    def on_select_section(self, _e=None):
        sel = self.section_index()
        if sel is None:
            return
        section = self.config_data["sections"][sel]
        self.title_var.set(section.get("title",""))
        self.max_var.set(section.get("max_buttons",6))
        self.action_list.delete(0, "end")
        for a in section.get("actions", []):
            label = a.get("label","")
            en = "" if a.get("enabled", True) else " (disabled)"
            self.action_list.insert("end", label + en)
        self.build_preview()

    def on_select_action(self, _e=None):
        pass

    def section_index(self):
        sel = self.section_list.curselection()
        return sel[0] if sel else None

    def action_index(self):
        sel = self.action_list.curselection()
        return sel[0] if sel else None

    def add_section(self):
        title = simpledialog.askstring("Section Title", "Enter section title:", parent=self)
        if not title:
            return
        self.config_data.setdefault("sections", []).append({"title": title, "max_buttons": 6, "actions": []})
        self.refresh_lists()
        self.section_list.select_set("end")
        self.on_select_section()

    def remove_section(self):
        idx = self.section_index()
        if idx is None:
            return
        if not messagebox.askyesno("Confirm", "Remove selected section?"):
            return
        self.config_data["sections"].pop(idx)
        self.refresh_lists()
        self.build_preview()

    def update_section(self):
        idx = self.section_index()
        if idx is None:
            return
        self.config_data["sections"][idx]["title"] = self.title_var.get()
        self.config_data["sections"][idx]["max_buttons"] = int(self.max_var.get())
        self.refresh_lists()
        self.section_list.select_set(idx)
        self.build_preview()

    def add_action(self):
        idx = self.section_index()
        if idx is None:
            messagebox.showwarning("No section", "Select a section first.")
            return
        # Simple dialog for label/command
        label = simpledialog.askstring("Action Label", "Button label:", parent=self)
        if not label:
            return
        command = simpledialog.askstring("Command", "Command string or special token (e.g. run:show version or __upload_template__):", parent=self)
        if command is None:
            return
        action = {"label": label, "enabled": True, "command": command, "tooltip": ""}
        self.config_data["sections"][idx].setdefault("actions", []).append(action)
        self.on_select_section()

    def remove_action(self):
        sidx = self.section_index()
        aidx = self.action_index()
        if sidx is None or aidx is None:
            return
        self.config_data["sections"][sidx]["actions"].pop(aidx)
        self.on_select_section()
        self.build_preview()

    def edit_action(self):
        sidx = self.section_index()
        aidx = self.action_index()
        if sidx is None or aidx is None:
            return
        action = self.config_data["sections"][sidx]["actions"][aidx]
        label = simpledialog.askstring("Action Label", "Button label:", initialvalue=action.get("label",""), parent=self)
        if label is None:
            return
        command = simpledialog.askstring("Command", "Command string:", initialvalue=action.get("command",""), parent=self)
        if command is None:
            return
        tooltip = simpledialog.askstring("Tooltip", "Tooltip text:", initialvalue=action.get("tooltip",""), parent=self)
        enabled = messagebox.askyesno("Enabled", "Should this button be enabled?", parent=self)
        action.update({"label": label, "command": command, "tooltip": tooltip or "", "enabled": enabled})
        self.on_select_section()
        self.build_preview()

    def build_preview(self):
        # Clear preview
        for c in self.preview_area.winfo_children():
            c.destroy()
        container = ttk.Frame(self.preview_area)
        container.pack(fill="both", expand=True)
        sections = self.config_data.get("sections", [])
        for i, sec in enumerate(sections):
            frame = ttk.Frame(container, relief="groove", padding=6)
            frame.grid(row=0, column=i, sticky="n", padx=6, pady=6)
            ttk.Label(frame, text=sec.get("title",""), font=("Segoe UI", 10, "bold")).pack(anchor="w")
            actions = [a for a in sec.get("actions", []) if a.get("enabled", True)]
            maxb = sec.get("max_buttons", len(actions))
            if len(actions) > maxb:
                actions = actions[:maxb]
            for a in actions:
                # Buttons in preview do nothing; show tooltip in label
                b = ttk.Button(frame, text=a.get("label",""), width=24)
                b.pack(fill="x", pady=3)
        # make grid columns expand
        for i in range(len(sections)):
            container.columnconfigure(i, weight=1)

    def load_config(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.config_data = json.load(f)
        except Exception:
            self.config_data = {"sections": []}
        self.refresh_lists()
        self.build_preview()

    def load_config_dialog(self):
        p = filedialog.askopenfilename(filetypes=[("JSON files","*.json"),("All files","*.*")])
        if p:
            self.load_config(p)

    def save_config(self):
        p = filedialog.asksaveasfilename(defaultextension=".json", initialfile=CONFIG_PATH, filetypes=[("JSON","*.json")])
        if not p:
            return
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=2)
        messagebox.showinfo("Saved", f"Config saved to {p}")

if __name__ == "__main__":
    app = CustomizerApp()
    app.mainloop()