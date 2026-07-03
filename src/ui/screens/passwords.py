from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen

from vault.service import VaultService

from ui.widgets.entry_details import EntryDetails
from ui.widgets.entry_list import EntryList


class PasswordsScreen(Screen):

    BINDINGS = [
        ("up", "move_up"),
        ("down", "move_down"),
    ]

    def __init__(self, service: VaultService):
        super().__init__()
        self.service = service

    def compose(self) -> ComposeResult:

        with Horizontal(id="main-layout"):

            yield EntryList()

            yield EntryDetails(id="entry-details")

    def on_mount(self):

        entry_list = self.query_one(EntryList)

        entry_list.load_entries(
            self.service.get_entries()
        )

        if entry_list.current_entry:

            self.query_one(
                EntryDetails
            ).show_entry(
                entry_list.current_entry
            )

    def action_move_up(self):

        entry_list = self.query_one(EntryList)

        entry_list.move_up()

        if entry_list.current_entry:

            self.query_one(
                EntryDetails
            ).show_entry(
                entry_list.current_entry
            )

    def action_move_down(self):

        entry_list = self.query_one(EntryList)

        entry_list.move_down()

        if entry_list.current_entry:

            self.query_one(
                EntryDetails
            ).show_entry(
                entry_list.current_entry
            )