from textual.widgets import ListItem, ListView

from models.entry import Entry
from ui.widgets.entry_item import EntryItem


class EntryList(ListView):

    def load_entries(
        self,
        entries: list[Entry],
    ):

        self.clear()

        for entry in entries:

            self.append(
                ListItem(
                    EntryItem(entry)
                )
            )