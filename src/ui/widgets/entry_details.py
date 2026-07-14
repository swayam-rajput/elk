from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Static, Select

from models.entry import Entry
from models.email import Email


class DetailView(Static):
    def __init__(self, item, emails) -> None:
        super().__init__()
        self._item = item
        self._emails = emails
        self._password_visible = False

    def toggle_password(self) -> None:
        self._password_visible = not self._password_visible
        self.refresh()

    def render(self) -> str:
        lines = []
        if isinstance(self._item, Entry):
            lines.append(f"[white]{self._item.site.name}[/white]\n")
            
            lines.append(f"[gray]URL:[/gray] {self._item.site.url}")
                        
            email = next(
                (
                    email.address
                    for email in self._emails
                    if email.address == self._item.email_id
                ),
                "Unknown Email",
            )

            lines.append(f"[gray]Email:[/] {email}")
            
            lines.append(f"[gray]Username:[/gray] {self._item.username}")
            
            pwd = self._item.password if self._password_visible else "•" * 10
            lines.append(f"[gray]Password:[/gray] {pwd}")
            
            lines.append(f"[gray]Notes:[/gray]")
            
            lines.append(f"{self._item.notes}")
        
        elif isinstance(self._item, Email):
            lines.append(f"[white]Email Account[/white]\n")
            lines.append(f"{self._item.address}\n")
            if self._item.label:
                lines.append(f"[gray]Label:[/gray] {self._item.label}")
        elif type(self._item).__name__ == "SettingItem":

            match self._item.editor:

                case "number":

                    lines.append(f"[white]{self._item.label}[/white]\n")
                    lines.append(f"[gray]Current:[/] {self._item.value}\n")
                    lines.append(self._item.description)
                    lines.append("\n\nPress [b]E[/b] to edit.")

                case "export":

                    lines.append("[white]Export Encrypted Vault[/white]\n")
                    lines.append(
                        "Create an encrypted backup of your vault.\n"
                    )
                    lines.append(
                        "\nPress [b]E[/b] to choose a destination."
                    )

                case "import":

                    lines.append("[white]Import Encrypted Vault[/white]\n")
                    lines.append(
                        "Replace the current vault with an existing backup.\n"
                    )
                    lines.append(
                        "\nPress [b]E[/b] to select a backup."
                    )
        return "\n".join(lines)


class EditForm(Vertical):
    can_focus = True

    def __init__(self, item, emails) -> None:
        super().__init__()
        self._item = item
        self._emails = emails

    def compose(self) -> ComposeResult:
        if isinstance(self._item, Entry):
            self._site_input = Input(
                value=self._item.site.name, placeholder="Site"
            )
            self._url_input = Input(
                value=self._item.site.url or 'https://', placeholder="URL"
            )
            
            self._email_select = Select(
                options=[
                    (
                        f"{email.address}",
                        email.address,
                    )
                    for email in self._emails
                ],

                
                compact=True,
                value=self._item.email_id or "Select email",
                prompt="Email Account",
                allow_blank=False
            )

            self._username_input = Input(
                value=self._item.username or "", placeholder="Username"
            )
            self._password_input = Input(
                value=self._item.password, placeholder="Password", password=True
            )
            self._notes_input = Input(
                value=self._item.notes, placeholder="Notes"
            )
            for inp in (
                self._site_input,
                self._url_input,
                self._email_select,
                self._username_input,
                self._password_input,
                self._notes_input,
            ):
                yield inp
        elif isinstance(self._item, Email):
            self._address_input = Input(
                value=self._item.address, placeholder="Email Account"
            )
            self._label_input = Input(
                value=self._item.label, placeholder="Label"
            )
            for inp in (
                self._address_input,
                self._label_input,
            ):
                yield inp
        elif type(self._item).__name__ == "SettingItem":
            from pathlib import Path
            match self._item.editor:
                case "number":

                    self._value_input = Input(
                        value=str(self._item.value),
                        placeholder="New Value",
                    )

                    yield self._value_input

                case "export":

                    self._destination_input = Input(
                        placeholder="Destination Folder",
                        value=str(Path.cwd() / "backup/elk-backup.vault"),
                        id='destination'
                    )

                    yield self._destination_input

                case "import":

                    self._source_input = Input(
                        placeholder="Backup File",
                    )

                    yield self._source_input


    def on_mount(self) -> None:
        inputs = self.query(Input)
        if inputs:
            inputs.first().focus()

    def collect(self) -> dict:
        if isinstance(self._item, Entry):
            return {
                "id": self._item.id,
                "site_name": self._site_input.value,
                "site_url": self._url_input.value or 'https://',
                "email_id": self._email_select.value,
                "username": self._username_input.value or None,
                "password": self._password_input.value,
                "notes": self._notes_input.value,
            }
        elif isinstance(self._item, Email):
            return {
                "id": self._item.id,
                "address": self._address_input.value,
                "label": self._label_input.value,
            }
        elif type(self._item).__name__ == "SettingItem":
            
            match self._item.editor:

                case "number":
                    
                    return {
                        "key": self._item.key,
                        "value": int(self._value_input.value),
                    }

                case "export":

                    return {
                        "action": "export",
                        "destination": self._destination_input.value,
                    }

                case "import":

                    return {
                        "action": "import",
                        "source": self._source_input.value,
                    }

        return {}


class DetailPanel(Vertical):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._current_item = None

    def show_item(self, item, emails=None) -> None:
        self._current_item = item
        self.remove_children()
        self.mount(DetailView(item, emails))

    def show_entry(self, entry, emails) -> None:
        self.show_item(entry, emails)

    def show_edit(self, item, emails=None) -> None:
        self._current_item = item
        self.remove_children()
        self.mount(EditForm(item, emails))

    def toggle_password(self) -> None:
        view = self.query(DetailView).first()
        if view:
            view.toggle_password()
