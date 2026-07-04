from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Horizontal
from textual.reactive import reactive

class CustomHeader(Horizontal):
    active_tab = reactive(1)
    item_count = reactive(0)
    item_type = reactive("sites")

    def __init__(self, active_tab: int = 1, item_count: int = 0, item_type: str = "sites"):
        super().__init__()
        self.active_tab = active_tab
        self.item_count = item_count
        self.item_type = item_type

    def compose(self) -> ComposeResult:
        yield Static(self._get_tabs_markup(), id="header-tabs")
        yield Static(f"{self.item_count} {self.item_type}", id="header-count")

    def _get_tabs_markup(self) -> str:
        tabs = [
            ("1", "Passwords"),
            ("2", "Emails"),
            ("3", "Search"),
            ("4", "Settings"),
        ]
        markup_parts = []
        for i, (num, name) in enumerate(tabs, start=1):
            if i == self.active_tab:
                markup_parts.append(f"[#262624 on #879792]{num} {name}[/]")
            else:
                markup_parts.append(f"[gray]{num} {name}[/gray]")
        
        return "  [gray] | [/]  ".join(markup_parts)

    def watch_active_tab(self, active_tab: int) -> None:
        try:
            self.query_one("#header-tabs", Static).update(self._get_tabs_markup())
        except Exception:
            pass

    def watch_item_count(self, item_count: int) -> None:
        try:
            self.query_one("#header-count", Static).update(f"[gray]{self.item_count} {self.item_type}[/gray]")
        except Exception:
            pass
