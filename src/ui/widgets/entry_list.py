from textual.containers import VerticalScroll

from models.entry import Entry

from ui.widgets.entry_item import EntryItem


class EntryList(VerticalScroll):

    def __init__(self):
        super().__init__()

        self.entries: list[Entry] = []

        self.selected_index = 0

    def load_entries(
        self,
        entries: list[Entry],
    ):

        self.entries = entries

        self.remove_children()

        for i, entry in enumerate(entries):

            self.mount(
                EntryItem(
                    entry,
                    selected=i == self.selected_index,
                )
            )


    @property
    def current_entry(self):

        if not self.entries:
            return None

        return self.entries[self.selected_index]
    
    
    def move_up(self):

        if self.selected_index > 0:

            self.selected_index -= 1

            self.refresh_list()


    def move_down(self):

        if self.selected_index < len(self.entries) - 1:

            self.selected_index += 1

            self.refresh_list()


    def refresh_list(self):

        self.remove_children()

        for i, entry in enumerate(self.entries):

            self.mount(
                EntryItem(
                    entry,
                    selected=i == self.selected_index,
                )
            )