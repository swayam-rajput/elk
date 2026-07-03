from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import ListView

from vault.service import VaultService

from ui.widgets.entry_details import EntryDetails
from ui.widgets.entry_list import EntryList


class PasswordsScreen(Screen):

    def __init__(
        self,
        service: VaultService,
    ):

        super().__init__()

        self.service = service

    def compose(self) -> ComposeResult:

        with Horizontal():

            yield EntryList(
                id="entry-list",
            )

            yield EntryDetails(
                id="entry-details",
            )

    def on_mount(self):

        entry_list = self.query_one(
            EntryList
        )

        entries = self.service.get_entries()

        entry_list.load_entries(entries)

        if entries:

            self.query_one(
                EntryDetails
            ).show_entry(entries[0])

    def on_list_view_highlighted(
        self,
        event: ListView.Highlighted,
    ):

        entries = self.service.get_entries()

        if not entries:
            return

        index = event.list_view.index

        self.query_one(
            EntryDetails
        ).show_entry(
            entries[index]
        )