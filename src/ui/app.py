from textual.app import App, Binding

from vault.service import VaultService
from ui.screens.passwords import PasswordsScreen


class PasswordManager(App):

    CSS_PATH = "style.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, service: VaultService):
        super().__init__()
        self.service = service

    def on_mount(self):
        self.push_screen(
            PasswordsScreen(self.service)
        )