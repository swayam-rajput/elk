from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Horizontal

class CustomFooter(Horizontal):
    def __init__(self, bindings_text: str = ""):
        super().__init__()
        self.bindings_text = bindings_text

    def compose(self) -> ComposeResult:
        yield Static(self.bindings_text, id="footer-bindings")
        yield Static("[AES-256-GCM]", id="footer-crypto")
