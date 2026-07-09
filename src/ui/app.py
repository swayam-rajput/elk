from textual.app import App, Binding

from vault.service import VaultService
from ui.screens.passwords import PasswordsScreen


class PasswordManager(App):

    CSS_PATH = "style.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("1", "tab_passwords", "Passwords", show=False),
        Binding("2", "tab_emails", "Emails", show=False),
        Binding("3", "tab_settings", "Settings", show=False),
    ]

    def __init__(self, service: VaultService):
        super().__init__()
        self.service = service

    def on_mount(self):
        self.push_screen(PasswordsScreen(self.service))

    def action_tab_passwords(self):
        self._switch_to(PasswordsScreen)

    def action_tab_emails(self):
        from ui.screens.emails import EmailsScreen

        self._switch_to(EmailsScreen)

    def action_tab_settings(self):
        from ui.screens.settings import SettingsScreen

        self._switch_to(SettingsScreen)

    def _switch_to(self, screen_class):
        self.pop_screen()
        self.push_screen(screen_class(self.service))
