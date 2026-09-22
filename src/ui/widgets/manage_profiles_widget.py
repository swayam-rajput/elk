from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Button, Input, Label, ListItem, ListView
from textual.containers import Horizontal, Vertical
from profiles.model import Profile
from profiles.manager import ProfileManager

class ManageProfilesWidget(Vertical):
    """Inline widget for profile management."""

    BINDINGS = [
        Binding("n", "new_profile", "New", show=True),
        Binding("r", "rename_profile", "Rename", show=True),
        Binding("d", "delete_profile", "Delete", show=True),
        Binding("space", "set_default", "Set Default", show=True),
        Binding("escape", "cancel_action", "Cancel", show=True),
    ]

    CSS = """
    #mpw-container {
        width: 100%;
        height: auto;
    }
    #mp-list {
        height: auto;
        min-height: 4;
        max-height: 12;
        margin-bottom: 1;
        background: $surface;
    }
    #mp-hints {
        color: #555;
        margin-bottom: 1;
    }
    #mp-form {
        display: none;
        margin-top: 1;
    }
    #mp-form.visible {
        display: block;
    }
    #mp-form Input {
        margin-bottom: 1;
    }
    """

    def __init__(self, profile_manager: ProfileManager):
        super().__init__()
        self.profile_manager = profile_manager
        self._form_mode: str | None = None  # "new" | "rename"

    def compose(self) -> ComposeResult:
        with Vertical(id="mpw-container"):
            yield Label("[white]Configure Profiles[/white]\n")
            yield ListView(id="mp-list")
            yield Label(
                "[gray]N new  R rename  D delete  Space set-default  Esc cancel[/gray]",
                id="mp-hints",
            )
            with Vertical(id="mp-form"):
                yield Input(placeholder="Profile name", id="mp-form-input")

    def on_mount(self) -> None:
        self._refresh_list()
        self.query_one("#mp-list", ListView).focus()

    def _refresh_list(self) -> None:
        profiles = self.profile_manager.list_profiles()
        default_id = self.profile_manager.default_profile_id
        lv = self.query_one("#mp-list", ListView)
        prev_idx = lv.index or 0
        lv.clear()
        for p in profiles:
            star = " [yellow]>[/yellow] " if p.id == default_id else "  "
            lv.append(ListItem(Label(f"{star}{p.name}")))
        if profiles:
            lv.index = min(prev_idx, len(profiles) - 1)

    def _get_selected(self) -> Profile | None:
        lv = self.query_one("#mp-list", ListView)
        profiles = self.profile_manager.list_profiles()
        idx = lv.index
        if idx is not None and 0 <= idx < len(profiles):
            return profiles[idx]
        return None

    def action_new_profile(self) -> None:
        if self._form_mode: return
        self._form_mode = "new"
        inp = self.query_one("#mp-form-input", Input)
        inp.placeholder = "New profile name"
        inp.value = ""
        self.query_one("#mp-form").add_class("visible")
        inp.focus()

    def action_rename_profile(self) -> None:
        if self._form_mode: return
        profile = self._get_selected()
        if not profile: return
        self._form_mode = "rename"
        inp = self.query_one("#mp-form-input", Input)
        inp.placeholder = "New name"
        inp.value = profile.name
        self.query_one("#mp-form").add_class("visible")
        inp.focus()

    def action_delete_profile(self) -> None:
        if self._form_mode: return
        profile = self._get_selected()
        if not profile: return
        try:
            self.profile_manager.delete_profile(profile.id)
            self.notify(f"Profile '{profile.name}' deleted.")
            self._refresh_list()
            self._notify_settings_refresh()
        except ValueError as e:
            self.notify(str(e), severity="error")

    def action_set_default(self) -> None:
        if self._form_mode: return
        profile = self._get_selected()
        if not profile: return
        self.profile_manager.set_default_profile(profile.id)
        self.notify(f"'{profile.name}' is now the default profile.")
        self._refresh_list()
        self._notify_settings_refresh()

    def action_cancel_action(self) -> None:
        if self._form_mode:
            self._cancel_form()
        else:
            try:
                self.app.query_one("SettingsScreen").action_cancel_edit()
            except Exception:
                pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "mp-form-input":
            self._submit_form()

    def _cancel_form(self) -> None:
        self._form_mode = None
        self.query_one("#mp-form").remove_class("visible")
        self.query_one("#mp-list", ListView).focus()

    def _submit_form(self) -> None:
        name = self.query_one("#mp-form-input", Input).value.strip()
        if not name:
            self.notify("Name cannot be empty.", severity="error")
            return

        if self._form_mode == "new":
            try:
                profile = self.profile_manager.create_profile(name)
                self.notify(f"Profile '{profile.name}' created.")
                self._cancel_form()
                self._refresh_list()
                self._notify_settings_refresh()
            except ValueError as e:
                self.notify(str(e), severity="error")

        elif self._form_mode == "rename":
            profile = self._get_selected()
            if profile:
                try:
                    self.profile_manager.rename_profile(profile.id, name)
                    self.notify("Profile renamed.")
                    self._cancel_form()
                    self._refresh_list()
                    self._notify_settings_refresh()
                except ValueError as e:
                    self.notify(str(e), severity="error")

    def _notify_settings_refresh(self) -> None:
        # Ask SettingsScreen to refresh its list (so Active: / Default: text updates)
        try:
            self.app.query_one("SettingsScreen")._refresh_settings()
        except Exception:
            pass
