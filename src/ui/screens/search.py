from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Input, Footer

from vault.service import VaultService
from models.entry import Entry
from models.email import Email
from ui.messages import SelectionChanged
from ui.widgets.entry_details import DetailPanel
from ui.widgets.entry_list import ScrollableList
from ui.widgets.custom_header import CustomHeader


class SearchScreen(Screen):
    BINDINGS = [
        ("s", "focus_search", "Search"),
        ("escape", "clear_or_unfocus", "Clear/Unfocus"),
    ]

    def __init__(self, service: VaultService):
        super().__init__()
        self.service = service
        self._results = []
        self._selected_item = None
        self._emails = service.get_emails()

    def compose(self) -> ComposeResult:
        yield CustomHeader(active_tab=3, item_count=0, item_type="results")
        yield Input(placeholder="Search passwords and emails...", id="search-input")
        with Horizontal(id="main-layout"):
            yield ScrollableList(id="entry-list")
            yield DetailPanel(id="entry-details")
        yield Footer()

    def on_mount(self) -> None:
        self._perform_search("")
        self.query_one("#search-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self._perform_search(event.value)

    def on_selection_changed(self, message: SelectionChanged) -> None:
        if 0 <= message.index < len(self._results):
            self._selected_item = self._results[message.index]
            detail = self.query_one(DetailPanel)
            detail.show_item(self._selected_item, self._emails)

    def action_focus_search(self) -> None:
        inp = self.query_one("#search-input", Input)
        inp.focus()
        inp.select_all()

    def action_clear_or_unfocus(self) -> None:
        inp = self.query_one("#search-input", Input)
        if inp.has_focus:
            if inp.value:
                inp.value = ""
            else:
                self.query_one(ScrollableList).focus()

    def _perform_search(self, query: str) -> None:
        query = query.strip().lower()
        entries = self.service.get_entries()
        emails = self._emails
        
        results = []
        for entry in entries:
            if (
                query in entry.site.name.lower() or
                query in entry.site.url.lower() or
                query in (entry.username or "").lower() or
                query in entry.notes.lower()
            ):
                results.append(entry)
                
        for email in emails:
            if (
                query in email.address.lower() or
                query in email.label.lower()
            ):
                results.append(email)
                
        self._results = results
        entry_list = self.query_one(ScrollableList)
        entry_list.load_items(results)
        
        try:
            self.query_one(CustomHeader).item_count = len(results)
        except Exception:
            pass
            
        detail = self.query_one(DetailPanel)
        if results:
            self._selected_item = results[0]
            detail.show_item(results[0], emails)
        else:
            self._selected_item = None
            detail.remove_children()
