from textual.containers import Horizontal
from textual.widgets import Label

from models.entry import Entry


class EntryItem(Horizontal):
    
    DEFAULT_CSS = """
    EntryItem {
        height: auto;
    }
    """

    def __init__(self, entry: Entry):
        super().__init__()

        self.entry = entry

    def compose(self):

        yield Label(
            self.entry.site.name,
            classes="entry-name",
        )

        if self.entry.favorite:
            yield Label(
                "~ ",
                classes="favorite",
            )