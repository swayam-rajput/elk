from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
)

from storage.github import GitHubStorage
from vault.service import VaultService


class GitHubSetupScreen(ModalScreen):

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]
    CSS = """
    GitHubSetupScreen {
        align: center middle;
    }

    #dialog {
        width: 60;
        padding: 1 2;
    }



    #buttons {
        height: auto;
        align: center middle ;
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

            yield Input(
                placeholder="GitHub Username",
                id="username",
            )

            yield Input(
                placeholder="Repository",
                id="repository",
            )

            yield Input(
                compact=True,
                placeholder="Personal Access Token",
                password=True,
                id="token",
            )

            with Horizontal(id="buttons"):

                yield Button(
                    "Save",
                    compact=True,
                    id="save",
                )

                yield Button(
                    "Cancel",
                    compact=True,
                    id="cancel",
                )

        yield Footer()

    def action_cancel(self):

        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed):

        if event.button.id == "cancel":

            self.dismiss()

            return

        username = self.query_one(
            "#username",
            Input,
        ).value.strip()

        repository = self.query_one(
            "#repository",
            Input,
        ).value.strip()

        token = self.query_one(
            "#token",
            Input,
        ).value.strip()

        if not username or not repository or not token:

            self.notify(
                "Please complete every field.",
                severity="error",
            )

            return

        github = GitHubStorage(
            username=username,
            repository=repository,
            token=token,
        )

        if not github.authenticate():

            self.notify(
                "GitHub authentication failed.",
                severity="error",
            )

            return

        settings = self.settings_manager.settings

        settings.github_enabled = True
        settings.github_username = username
        settings.github_repository = repository
        settings.github_token = self.service.encrypt_token(token)

        self.settings_manager.save()

        self.notify(
            "GitHub Sync configured.",
            severity="information",
        )

        self.dismiss(True)