from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Input, Label
from textual.containers import Vertical

from storage.local import LocalStorage
from vault.service import VaultService
from profiles.model import Profile


class UnlockScreen(Screen):
    BINDINGS = [("escape", "go_back", "Back")]

    CSS = """
    UnlockScreen { align: center middle; }
    #ul-container { width: 40; height: auto; border: round #444; padding: 1 2; }
    Input { margin-top: 1; }
    """

    def __init__(self, storage: LocalStorage, profile: Profile, has_multiple_profiles: bool = False):
        super().__init__()
        self.storage = storage
        self.profile = profile
        self.has_multiple = has_multiple_profiles
        self._is_new = not storage.exists()

    def compose(self) -> ComposeResult:
        with Vertical(id="ul-container"):
            yield Label(f"Profile: {self.profile.name}")
            yield Input(placeholder="Master Password", password=True, id="pw")
            if self._is_new:
                yield Input(placeholder="Confirm Password", password=True, id="confirm")

    def on_mount(self) -> None:
        self.query_one("#pw", Input).focus()

    def action_go_back(self) -> None:
        self.dismiss(None) if self.has_multiple else self.app.exit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        pw = self.query_one("#pw", Input).value
        if not pw: return

        if self._is_new:
            if event.input.id == "pw":
                self.query_one("#confirm", Input).focus()
                return
            if pw != self.query_one("#confirm", Input).value:
                self.query_one("#confirm", Input).value = ""
                return
            service = VaultService(self.storage)
            service.create_vault(pw)
            self.dismiss(service)
        else:
            service = VaultService(self.storage)
            try:
                service.unlock_vault(pw)
                self.dismiss(service)
            except ValueError as e:
                self.notify(str(e).split('\n')[0], severity="error")
                pw_input = self.query_one("#pw", Input)
                pw_input.value = ""
                pw_input.focus()
