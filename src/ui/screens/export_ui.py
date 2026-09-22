from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from vault.service import VaultService


class ExportVaultScreen(ModalScreen):

    BINDINGS = [
        ("ctrl+s", "save", "Export"),
        ("escape", "cancel", "Cancel"),
    ]

    CSS = """
    ExportVaultScreen {
        align: center middle;
    }

    #dialog {
        width: 60;
        padding: 1 2;
    }

    Input {
        margin: 1 0;
    }

    #buttons {
        height: auto;
        background:transparent;
        layout: horizontal;
        align: right middle;
        margin-top: 1;
        
    }

    Button {
        margin-left: 1;
        background: transparent;
    }
    """

    def __init__(self, service: VaultService):
        super().__init__()

        self.service = service

    def compose(self) -> ComposeResult:

        with Vertical(id="dialog"):

            yield Label("Export Encrypted Vault")

            yield Input(
                placeholder="Destination path",
                value=str(Path.cwd() / "backup/elk-backup.vault"),
                id="destination",
            )

            with Vertical(id="buttons"):

                yield Button(
                    "Export",
                    compact=True,
                    id="export",
                )

                yield Button(
                    "Cancel",
                    compact=True,
                    id="cancel",
                )

    def action_cancel(self):

        self.dismiss()

    def action_save(self):

        self._export()

    def on_button_pressed(self, event: Button.Pressed):

        if event.button.id == "cancel":
            self.dismiss()
            return

        if event.button.id == "export":
            self._export()

    def _export(self):

        destination = self.query_one(
            "#destination",
            Input,
        ).value.strip()

        if not destination:

            self.notify(
                "Please enter a destination.",
                severity="error",
            )

            return

        try:

            path = self.service.export_backup(
                destination,
            )

            self.notify(
                f"Exported to\n{path}",
            )

            self.dismiss(True)

        except Exception as e:
            print(e)
            self.notify(
                str(e),
                severity="error",
            )