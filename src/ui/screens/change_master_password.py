from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Header, Footer
from vault.service import VaultService


class ChangeMasterPasswordScreen(ModalScreen[bool]):
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    CSS = """
    ChangeMasterPasswordScreen {
        align: center middle;
    }

    #dialog {
        width: 60;
        padding: 1 2;
    }

    #dialog Label {
        text-style: bold;
        margin-bottom: 1;
    }

    Input {
        margin-bottom: 1;
    }

    #buttons {
        height: auto;
        align: center middle;
        background: transparent;
        margin-top: 1;
    }

    Button {
        margin-left: 1;
        background: transparent;
    }
    """

    def __init__(self, service: VaultService, settings_manager):
        super().__init__()
        self.service = service
        self.settings_manager = settings_manager

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="dialog"):
            yield Label("Change Master Password")
            yield Input(
                placeholder="Current Master Password",
                password=True,
                id="current_password",
            )
            yield Input(
                placeholder="New Master Password",
                password=True,
                id="new_password",
            )
            yield Input(
                placeholder="Confirm New Master Password",
                password=True,
                id="confirm_password",
            )
            with Horizontal(id="buttons"):
                yield Button("Save", compact=True, id="save")
                yield Button("Cancel", compact=True, id="cancel")
        yield Footer()

    def action_cancel(self):
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "cancel":
            self.dismiss(False)
            return

        current_pw = self.query_one("#current_password", Input).value
        new_pw = self.query_one("#new_password", Input).value
        confirm_pw = self.query_one("#confirm_password", Input).value

        if not current_pw or not new_pw or not confirm_pw:
            self.notify("Please fill out all fields.", severity="error")
            return

        if new_pw != confirm_pw:
            self.notify("New passwords do not match.", severity="error")
            return

        try:
            settings = self.settings_manager.settings
            old_encrypted_token = settings.github_token if settings.github_enabled else ""
            
            new_encrypted_token = self.service.change_master_password(
                current_pw,
                new_pw,
                old_encrypted_token
            )
            
            if settings.github_enabled and new_encrypted_token:
                settings.github_token = new_encrypted_token
                self.settings_manager.save()

            self.notify("Master password updated successfully.", severity="information")
            self.dismiss(True)
        except Exception as e:
            self.notify(str(e), severity="error")
