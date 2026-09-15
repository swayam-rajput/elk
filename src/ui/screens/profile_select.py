from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Label, ListItem, ListView
from textual.containers import Vertical

from profiles.manager import ProfileManager
from profiles.model import Profile


class ProfileSelectScreen(Screen):
    BINDINGS = [("escape", "quit_app", "Quit")]

    CSS = """
    ProfileSelectScreen { align: center middle; }
    #ps-container { width: 40; height: auto; border: round #444; padding: 1 2; }
    #ps-list { height: auto; max-height: 12; margin-top: 1; }
    """

    def __init__(self, profile_manager: ProfileManager, default_profile: Profile | None = None):
        super().__init__()
        self.profile_manager = profile_manager
        self.default_profile = default_profile

    def compose(self) -> ComposeResult:
        with Vertical(id="ps-container"):
            yield Label("Select Profile")
            yield ListView(id="ps-list")

    def on_mount(self) -> None:
        lv = self.query_one(ListView)
        for p in self.profile_manager.list_profiles():
            lv.append(ListItem(Label(p.name)))
        
        if self.default_profile:
            idx = next((i for i, p in enumerate(self.profile_manager.list_profiles()) if p.id == self.default_profile.id), 0)
            lv.index = idx
            
        lv.focus()

    def action_quit_app(self) -> None:
        self.app.exit()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        profiles = self.profile_manager.list_profiles()
        idx = self.query_one(ListView).index
        if idx is not None and 0 <= idx < len(profiles):
            self.profile_manager.set_active_profile(profiles[idx].id)
            self.dismiss(profiles[idx])
