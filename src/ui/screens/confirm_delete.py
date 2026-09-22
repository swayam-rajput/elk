from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label


class ConfirmDeleteScreen(ModalScreen[bool]):
    BINDINGS = [
        ("y", "confirm", "Yes"),
        ("d", "confirm", "Delete"),
        ("enter", "confirm", "Delete"),
        ("n", "cancel", "No"),
        ("escape", "cancel", "Cancel"),
    ]

    CSS = """
    ConfirmDeleteScreen {
        align: center bottom;
        background: transparent;
    }

    #dialog {
    
        width: 100%;
        height: 1;
        background: #262624 ;
        color: white;
        padding: 0 2;
    }
    """

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Label(self.message, id="dialog")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)
