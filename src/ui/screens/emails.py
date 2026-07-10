from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer

from crypto.random import RandomGenerator
from models.email import Email
from vault.service import VaultService
from ui.messages import SelectionChanged
from ui.widgets.entry_details import DetailPanel, EditForm
from ui.widgets.entry_list import ScrollableList
from ui.widgets.custom_header import CustomHeader


class EmailsScreen(Screen):
    BINDINGS = [
        ("a", "add_email", "Add"),
        ("d", "delete_email", "Delete"),
        ("e", "edit_email", "Edit"),
        ("ctrl+s", "save_email", "Save"),
        ("escape", "cancel_edit", "Cancel"),
    ]

    def __init__(self, service: VaultService):
        super().__init__()
        self.service = service
        self._selected_email: Email | None = None
        self._editing = False
        self._adding = False

    def compose(self) -> ComposeResult:
        yield CustomHeader(active_tab=2, item_count=len(self.service.get_emails()), item_type="emails")
        with Horizontal(id="main-layout"):
            yield ScrollableList(id="entry-list")
            yield DetailPanel(id="entry-details")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_emails()

    def on_selection_changed(self, message: SelectionChanged) -> None:
        emails = self.service.get_emails()
        if 0 <= message.index < len(emails):
            self._selected_email = emails[message.index]
            if not self._editing:
                detail = self.query_one(DetailPanel)
                detail.show_item(self._selected_email, emails)

    def action_add_email(self) -> None:
        new_email = Email(
            id=RandomGenerator.generate_uuid(),
            address="",
            label="",
        )
        self.service.add_email(new_email)
        emails = self.service.get_emails()
        new_index = len(emails) - 1
        entry_list = self.query_one(ScrollableList)
        entry_list.load_items(emails, select_index=new_index)
        self._selected_email = new_email
        self._editing = True
        self._adding = True
        detail = self.query_one(DetailPanel)
        detail.show_edit(new_email, emails)

    def action_delete_email(self) -> None:
        if self._selected_email is None or self._editing:
            return
        email_id = self._selected_email.id
        try:
            self.service.delete_email(email_id)
        except ValueError as e:
            self.app.notify(str(e), severity="error")
            return
            
        self._selected_email = None
        self._editing = False
        self._adding = False
        self._refresh_emails()
        detail = self.query_one(DetailPanel)
        detail.remove_children()

    def action_edit_email(self) -> None:
        if self._selected_email is None or self._editing:
            return
        self._editing = True
        self._adding = False
        detail = self.query_one(DetailPanel)
        detail.show_edit(self._selected_email, self.service.get_emails())

    def action_save_email(self) -> None:
        if not self._editing:
            return
        detail = self.query_one(DetailPanel)
        form = detail.query(EditForm).first()
        if not form:
            return
        data = form.collect()
        original = self._selected_email
        if original is None:
            return
        updated = Email(
            id=data["id"],
            address=data["address"],
            label=data["label"],
        )
        self.service.update_email(updated)
        self._editing = False
        self._adding = False
        self._selected_email = updated
        detail.show_item(updated, self.service.get_emails())
        self._refresh_emails()
        self.query_one(ScrollableList).focus()

    def action_cancel_edit(self) -> None:
        if not self._editing:
            return
        # If we were adding a new email, delete the empty record
        if self._adding and self._selected_email:
            self.service.delete_email(self._selected_email.id)
            self._selected_email = None
        self._editing = False
        self._adding = False
        self._refresh_emails()
        self.query_one(ScrollableList).focus()

    def _refresh_emails(self) -> None:
        emails = self.service.get_emails()
        entry_list = self.query_one(ScrollableList)
        entry_list.load_items(emails)
        try:
            self.query_one(CustomHeader).item_count = len(emails)
        except Exception:
            pass
        if emails:
            self._selected_email = emails[0]
            self.query_one(DetailPanel).show_item(self._selected_email, emails)
        else:
            self._selected_email = None
            self.query_one(DetailPanel).remove_children()
