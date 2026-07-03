from textual.widgets import Static

from models.entry import Entry


class EntryItem(Static):

    def __init__(
        self,
        entry: Entry,
        selected: bool = False,
    ):
        super().__init__()

        self.entry = entry
        self.selected = selected

    def render(self):

        prefix = "> " if self.selected else "  "

        favorite = " !" if self.entry.favorite else ""

        return f"{prefix}{self.entry.site.name}{favorite}"