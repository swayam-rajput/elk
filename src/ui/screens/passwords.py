from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer

from crypto.random import RandomGenerator
from models.entry import Entry, Site
from vault.service import VaultService
from ui.messages import SelectionChanged
from ui.widgets.entry_details import DetailPanel, EditForm
from ui.widgets.entry_list import ScrollableList
from ui.widgets.custom_header import CustomHeader


class PasswordsScreen(Screen):
    BINDINGS = [
        ("a", "add_entry", "Add"),
        ("d", "delete_entry", "Delete"),
        ("e", "edit_entry", "Edit"),
        ("p", "reveal_password", "Reveal"),
        ("y", "copy_password", "Copy"),
        ("ctrl+s", "save_entry", "Save"),
        ("escape", "cancel_edit", "Cancel"),
    ]

    def __init__(self, service: VaultService):
        super().__init__()
        self.service = service
        self._selected_entry: Entry | None = None
        self._editing = False
        self._emails = self.service.get_emails()

    def compose(self) -> ComposeResult:
        yield CustomHeader(active_tab=1)
        with Horizontal(id="main-layout"):
            yield ScrollableList(id="entry-list")
            yield DetailPanel(id="entry-details")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_entries()

    def on_selection_changed(self, message: SelectionChanged) -> None:
        entries = self.service.get_entries()
        if 0 <= message.index < len(entries):
            self._selected_entry = entries[message.index]
            if not self._editing:
                detail = self.query_one(DetailPanel)
                detail.show_entry(self._selected_entry, self._emails)

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
        detail = self.query_one(DetailPanel)
        detail.show_edit(new_entry, self._emails)

    def action_delete_entry(self) -> None:
        if self._selected_entry is None or self._editing:
            return
        entry_id = self._selected_entry.id
        self.service.delete_entry(entry_id)

        self._selected_entry = None
        self._editing = False
        self._refresh_entries()
        detail = self.query_one(DetailPanel)
        detail.remove_children()

    def action_edit_entry(self) -> None:
        if self._selected_entry is None or self._editing:
            return
        self._editing = True
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
        self._selected_entry = updated
        detail.show_entry(updated, self._emails)
        self._refresh_entries()
        self.query_one(ScrollableList).focus()

    def action_cancel_edit(self) -> None:
        if not self._editing:
            return
        self._editing = False
        if self._selected_entry:
            detail = self.query_one(DetailPanel)
            detail.show_entry(self._selected_entry, self._emails)
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
        entries = self.service.get_entries()
        entry_list = self.query_one(ScrollableList)
        entry_list.load_items(entries)
        try:
            self.query_one(CustomHeader).item_count = len(entries)
        except Exception:
            pass
        if entries:
            self._selected_entry = entries[0]
            self.query_one(DetailPanel).show_entry(entries[0], self._emails)
        else:
            self._selected_entry = None
            self.query_one(DetailPanel).remove_children()
