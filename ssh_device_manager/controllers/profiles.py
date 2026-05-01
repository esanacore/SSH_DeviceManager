"""Profile persistence orchestration."""

from tkinter import messagebox


class ProfileController:
    """Owns profile CRUD behavior for the connection form."""

    def __init__(self, app):
        self.app = app

    def refresh_profile_list(self):
        profile_names = sorted(self.app.app_config.get("profiles", {}).keys())
        self.app.profile_combo["values"] = profile_names
        current = self.app.profile_select_var.get().strip()
        if current in profile_names:
            return
        if profile_names:
            self.app.profile_select_var.set(profile_names[0])
        else:
            self.app.profile_select_var.set("")

    def save_profile(self):
        profile_name = (
            self.app.profile_name_var.get().strip()
            or self.app.profile_select_var.get().strip()
        )
        if not profile_name:
            messagebox.showwarning(
                "Missing Profile Name",
                "Enter a profile name before saving.",
            )
            return

        inputs = self.app._get_connection_inputs()
        if inputs is None:
            return
        host, port, user, _pw, timeout = inputs

        self.app.app_config.setdefault("profiles", {})[profile_name] = {
            "host": host,
            "port": port,
            "username": user,
            "timeout": timeout,
            "host_key_mode": self.app._get_host_key_mode(),
        }
        self.app._save_app_config()
        self.refresh_profile_list()
        self.app.profile_select_var.set(profile_name)
        self.app.profile_name_var.set(profile_name)
        self.app.log(f"[OK] Saved profile '{profile_name}'.")

    def load_selected_profile(self):
        profile_name = self.app.profile_select_var.get().strip()
        if not profile_name:
            messagebox.showwarning(
                "No Profile Selected",
                "Choose a saved profile to load.",
            )
            return

        profile = self.app.app_config.get("profiles", {}).get(profile_name)
        if not isinstance(profile, dict):
            messagebox.showerror(
                "Missing Profile",
                f"Profile '{profile_name}' was not found.",
            )
            self.app._refresh_profile_list()
            return

        host = str(profile.get("host", ""))
        self.app.profile_name_var.set(profile_name)
        self.app.host_var.set(host)
        self.app.port_var.set(int(profile.get("port", 22)))
        self.app.user_var.set(str(profile.get("username", "")))
        self.app.timeout_var.set(int(profile.get("timeout", 10)))
        self.app.host_key_mode_var.set(str(profile.get("host_key_mode", "warning")))
        if host and host not in self.app.host_history:
            self.app.host_history.insert(0, host)
            self.app.host_combo["values"] = self.app.host_history + ["<Clear History>"]
        self.app.log(f"[OK] Loaded profile '{profile_name}'.")

    def delete_selected_profile(self):
        profile_name = self.app.profile_select_var.get().strip()
        if not profile_name:
            messagebox.showwarning(
                "No Profile Selected",
                "Choose a saved profile to delete.",
            )
            return
        confirmed = messagebox.askyesno(
            "Delete Profile",
            f"Delete profile '{profile_name}'?",
        )
        if not confirmed:
            return
        profiles = self.app.app_config.get("profiles", {})
        if profile_name in profiles:
            del profiles[profile_name]
            self.app._save_app_config()
            self.app._refresh_profile_list()
            if self.app.profile_name_var.get().strip() == profile_name:
                self.app.profile_name_var.set("")
            self.app.log(f"[OK] Deleted profile '{profile_name}'.")
