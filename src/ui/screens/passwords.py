from textual.app import ComposeResult, Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Input

from crypto.random import RandomGenerator
from models.entry import Entry, Site
from models.email import Email
from vault.service import VaultService
from ui.messages import SelectionChanged
from ui.widgets.entry_details import DetailPanel, EditForm
from ui.widgets.entry_list import ScrollableList
from ui.widgets.custom_header import CustomHeader


class PasswordsScreen(Screen):
    BINDINGS = [
        Binding("a", "add_entry", "Add"),
        Binding("d", "delete_entry", "Delete"),
        Binding("e", "edit_entry", "Edit"),
        Binding("p", "reveal_password", "Reveal"),
        Binding("y", "copy_password", "Copy"),
        Binding("f", "toggle_search", "Search", priority=True),
        Binding("ctrl+f", "toggle_search", "Search", show=False, priority=True),
        Binding("ctrl+s", "save_entry", "Save"),
        Binding("escape", "cancel_edit", "Cancel"),
    ]

    def __init__(self, service: VaultService, settings_manager=None):
        super().__init__()
        self.service = service
        self.settings_manager = settings_manager
        self._selected_entry: Entry | None = None
        self._editing = False
        self._adding = False
        self._emails = self.service.get_emails()
        self._search_visible = False
        self._search_query = ""

    def compose(self) -> ComposeResult:
        yield CustomHeader(active_tab=1)
        yield Input(
            placeholder="Search passwords and emails...",
            id="search-input",
            classes="-hidden",
        )
        with Horizontal(id="main-layout"):
            yield ScrollableList(id="entry-list")
            yield DetailPanel(id="entry-details")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_entries()
        self.query_one(ScrollableList).focus()

    def on_selection_changed(self, message: SelectionChanged) -> None:
        items = self._get_filtered_items()
        if 0 <= message.index < len(items):
            self._selected_entry = items[message.index]
            if not self._editing:
                detail = self.query_one(DetailPanel)
                detail.show_item(self._selected_entry, self._emails)

    # ── Search ──────────────────────────────────────────────

    def action_toggle_search(self) -> None:
        if self._editing:
            return
        inp = self.query_one("#search-input", Input)
        if self._search_visible:
            # Hide search, clear query, restore full list
            self._search_visible = False
            self._search_query = ""
            inp.value = ""
            inp.add_class("-hidden")
            self.query_one(ScrollableList).focus()
            self._refresh_entries()
        else:
            self._search_visible = True
            inp.remove_class("-hidden")
            inp.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self._search_query = event.value.strip().lower()
            self._refresh_entries()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-input":
            self.query_one(ScrollableList).focus()

    def _get_filtered_items(self) -> list:
        entries = self.service.get_entries()
        query = self._search_query
        if not query:
            return entries
        return [
            e for e in entries
            if (
                query in e.site.name.lower()
                or query in e.site.url.lower()
                or query in (e.username or "").lower()
                or query in e.notes.lower()
                or query in (e.email_id or "").lower()
            )
        ]

    # ── CRUD ────────────────────────────────────────────────

    def action_add_entry(self) -> None:
        new_entry = Entry(
            id=RandomGenerator.generate_uuid(),
            site=Site(name="", url=""),
            email_id=self._emails[0].address if self._emails else "",
            username="",
            password="",
            notes="",
        )
        self.service.add_entry(new_entry)

        entries = self.service.get_entries()
        new_index = len(entries) - 1
        entry_list = self.query_one(ScrollableList)
        entry_list.load_items(entries, select_index=new_index)
        self._selected_entry = new_entry
        self._editing = True
        self._adding = True
        detail = self.query_one(DetailPanel)
        detail.show_edit(new_entry, self._emails)

    def action_delete_entry(self) -> None:
        if self._selected_entry is None or self._editing:
            return

        from ui.screens.confirm_delete import ConfirmDeleteScreen

        entry = self._selected_entry
        message = f"Delete entry [#D16666]{entry.site.name}[/]? Press [orange][b]d[/][/] again to confirm or [orange][b]esc[/][/] to cancel"

        def handle_confirm(confirmed: bool) -> None:
            if confirmed:
                self.service.delete_entry(entry.id)
                self._selected_entry = None
                self._editing = False
                self._adding = False
                self._refresh_entries()
                detail = self.query_one(DetailPanel)
                detail.remove_children()
                self.notify("Password entry deleted.")

        self.app.push_screen(
            ConfirmDeleteScreen(message),
            callback=handle_confirm
        )

    def action_edit_entry(self) -> None:
        if self._selected_entry is None or self._editing:
            return
        self._editing = True
        self._adding = False
        detail = self.query_one(DetailPanel)
        detail.show_edit(self._selected_entry, self.service.get_emails())

    def action_save_entry(self) -> None:
        if not self._editing:
            return
        detail = self.query_one(DetailPanel)
        form = detail.query(EditForm).first()
        if not form:
            return
        data = form.collect()
        original = self._selected_entry
        if original is None:
            return
        updated = Entry(
            id=data["id"],
            site=Site(name=data["site_name"], url=data["site_url"]),
            email_id=data['email_id'],
            username=data["username"],
            password=data["password"],
            notes=data["notes"],
            favorite=original.favorite,
            created_at=original.created_at,
        )
        self.service.update_entry(updated)

        self._editing = False
        self._adding = False
        self._selected_entry = updated
        detail.show_entry(updated, self._emails)
        self._refresh_entries()
        self.query_one(ScrollableList).focus()

    def action_cancel_edit(self) -> None:
        if not self._editing:
            # If search is visible, close it on Escape
            if self._search_visible:
                self.action_toggle_search()
            return
        # If we were adding a new entry, delete the empty record
        if self._adding and self._selected_entry:
            self.service.delete_entry(self._selected_entry.id)
            self._selected_entry = None
        self._editing = False
        self._adding = False
        self._refresh_entries()
        self.query_one(ScrollableList).focus()

    def action_reveal_password(self) -> None:
        if self._editing:
            return
        detail = self.query_one(DetailPanel)
        detail.toggle_password()

    def action_copy_password(self) -> None:
        if self._selected_entry is None or self._editing:
            return
        self.app.copy_to_clipboard(self._selected_entry.password)

    def _refresh_entries(self) -> None:
        items = self._get_filtered_items()
        entry_list = self.query_one(ScrollableList)
        entry_list.load_items(items)
        try:
            header = self.query_one(CustomHeader)
            header.item_count = len(items)
        except Exception:
            pass
        if items:
            self._selected_entry = items[0]
            self.query_one(DetailPanel).show_item(items[0], self._emails)
        else:
            self._selected_entry = None
            self.query_one(DetailPanel).remove_children()
