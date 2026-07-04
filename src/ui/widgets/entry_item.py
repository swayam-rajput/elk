from datetime import datetime
from textual.reactive import reactive
from textual.widgets import Static

from models.entry import Entry
from models.email import Email


class EntryRow(Static):
    selected: reactive[bool] = reactive(False)

    def __init__(self, entry: Entry, selected: bool = False) -> None:
        super().__init__()
        self.entry = entry
        self.selected = selected

    def watch_selected(self, selected: bool) -> None:
        self.refresh()
        if selected:
            self.add_class("selected")
        else:
            self.remove_class("selected")

    def render(self) -> str:
        # prefix = " " if self.selected else "  "
        # date_str = ""
        # if hasattr(self.entry, "created_at") and isinstance(self.entry.created_at, datetime):
        #     date_str = self.entry.created_at.strftime("%Y-%m-%d") + "  "
        # else:
        #     date_str = datetime.now().strftime("%Y-%m-%d") + "  "
        
        fav = " \u2605" if getattr(self.entry, "favorite", False) else ""
        return f"{self.entry.site.name}{fav}"
        # return f"{prefix}{date_str}{self.entry.site.name}{fav}"


class EmailRow(Static):
    selected: reactive[bool] = reactive(False)

    def __init__(self, email: Email, selected: bool = False) -> None:
        super().__init__()
        self.email = email
        self.selected = selected

    def watch_selected(self, selected: bool) -> None:
        self.refresh()
        if selected:
            self.add_class("selected")
        else:
            self.remove_class("selected")

    def render(self) -> str:
        # prefix = "▌  " if self.selected else "  "
        label_part = f" ({self.email.label})" if self.email.label else ""
        return f"{self.email.address}"


class SettingRow(Static):
    selected: reactive[bool] = reactive(False)

    def __init__(self, item, selected: bool = False) -> None:
        super().__init__()
        self.item = item
        self.selected = selected

    def watch_selected(self, selected: bool) -> None:
        self.refresh()
        if selected:
            self.add_class("selected")
        else:
            self.remove_class("selected")

    def render(self) -> str:
        return f"{self.item.label}"
