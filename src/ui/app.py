from datetime import datetime
from urllib.parse import urlparse
import pyperclip

from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widget import Widget
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Input, Button, ListView, ListItem, Select
from textual.binding import Binding

from vault.service import VaultService
from models.email import Email
from models.entry import Entry, Site
from crypto.random import RandomGenerator
from storage.local import LocalStorage

# ─────────────────────────────────────────────────────────
# Mock Data for Demo Mode (Password: "demo")
# ─────────────────────────────────────────────────────────

MOCK_EMAILS = [
    Email(id="email-1", address="simon@gmail.com", label="Personal"),
    Email(id="email-2", address="simon.codes@company.com", label="Work"),
    Email(id="email-3", address="simon.gaming@gmail.com", label="Gaming"),
]

MOCK_ENTRIES = [
    Entry(
        id="entry-1",
        site=Site(name="GitHub", url="https://github.com"),
        email_id="email-2",
        username="SimonCodes",
        password="SuperSecretGitHubPassword123!",
        notes="Personal dev account. 2FA is enabled via Authenticator app.",
        favorite=True,
        created_at=datetime(2025, 1, 10, 14, 30),
        updated_at=datetime(2026, 6, 12, 9, 15),
    ),
    Entry(
        id="entry-2",
        site=Site(name="Google", url="https://google.com"),
        email_id="email-1",
        username="simon@gmail.com",
        password="MySecureGoogleAccount456?",
        notes="Recovery email is work address. Used for Google Cloud Console.",
        favorite=True,
        created_at=datetime(2025, 2, 5, 10, 0),
        updated_at=datetime(2026, 5, 20, 11, 45),
    ),
    Entry(
        id="entry-3",
        site=Site(name="Netflix", url="https://netflix.com"),
        email_id="email-1",
        username="simon@gmail.com",
        password="FamilyNetflixSharing789!",
        notes="Shared with family. Premium 4K subscription.",
        favorite=False,
        created_at=datetime(2025, 3, 15, 18, 20),
        updated_at=datetime(2025, 11, 1, 15, 30),
    ),
    Entry(
        id="entry-4",
        site=Site(name="Steam", url="https://store.steampowered.com"),
        email_id="email-3",
        username="SimonTheGamer",
        password="GamerPassword999!!",
        notes="Steam Guard is active on mobile.",
        favorite=True,
        created_at=datetime(2025, 4, 1, 12, 0),
        updated_at=datetime(2026, 7, 1, 16, 10),
    ),
    Entry(
        id="entry-5",
        site=Site(name="Spotify", url="https://spotify.com"),
        email_id="email-1",
        username="simon.music",
        password="SpotifyBeatDrop00!",
        notes="Premium duo plan.",
        favorite=False,
        created_at=datetime(2025, 5, 12, 8, 45),
        updated_at=datetime(2025, 5, 12, 8, 45),
    ),
    Entry(
        id="entry-6",
        site=Site(name="Amazon", url="https://amazon.com"),
        email_id="email-1",
        username="simon@gmail.com",
        password="AmazonPrimeShopping2026",
        notes="Prime membership renews annually in December.",
        favorite=False,
        created_at=datetime(2025, 6, 20, 16, 55),
        updated_at=datetime(2026, 4, 18, 10, 12),
    ),
]


# ─────────────────────────────────────────────────────────
# Custom Widgets
# ─────────────────────────────────────────────────────────

class SearchBar(Input):
    """Custom search input field matching styling."""
    pass


class PasswordField(Widget):
    """Custom password input field wrapper matching styling."""
    def compose(self) -> ComposeResult:
        yield Input(password=True, placeholder="Master Password", id="unlock-password")


class AppFooter(Widget):
    """Custom application footer display panel."""
    def compose(self) -> ComposeResult:
        bindings = [
            ("↑↓", "Navigate"),
            ("Enter", "View"),
            ("a", "Add"),
            ("e", "Edit"),
            ("d", "Delete"),
            ("y", "Copy"),
            ("p", "Show Pass"),
            ("/", "Search"),
            ("Tab", "Switch Panel"),
            ("q", "Quit"),
        ]
        for key, desc in bindings:
            yield Label(f"[bold #7c6af7]{key}[/] {desc}  • ", classes="footer-binding")


class EntryRow(ListItem):
    """Custom list row for displaying a password entry."""
    DEFAULT_CLASSES = "entry-row"

    def __init__(self, entry: Entry, email_label: str = "", **kwargs):
        super().__init__(**kwargs)
        self.entry = entry
        self.email_label = email_label

    def compose(self) -> ComposeResult:
        star = "★" if self.entry.favorite else " "
        domain = urlparse(self.entry.site.url).netloc or self.entry.site.url
        yield Label(star, classes="entry-col-star")
        yield Label(self.entry.site.name, classes="entry-col-site")
        yield Label(domain, classes="entry-col-url")
        yield Label(self.email_label, classes="entry-col-label")


class EmptyRow(ListItem):
    """Custom row to display when list is empty."""
    def compose(self) -> ComposeResult:
        yield Label("No entries found", classes="entry-empty")


class LeftPanel(Container):
    """Focusable container representing the Left List Panel."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_focus = True

    def on_focus(self) -> None:
        # Delegate focus to the list inside
        try:
            self.query_one("#entry-list").focus()
        except Exception:
            pass


class RightPanel(Container):
    """Focusable container representing the Right Details/Preview Panel."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_focus = True


class DetailsPreview(Widget):
    """Right-side details preview card container."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entry = None
        self.reveal_password = False
        self.emails_list = []

    def compose(self) -> ComposeResult:
        with Vertical(id="details-body"):
            with Horizontal(classes="detail-row"):
                yield Label("Site Name", classes="detail-label")
                yield Label("-", id="preview-site", classes="detail-value")
            with Horizontal(classes="detail-row"):
                yield Label("URL", classes="detail-label")
                yield Label("-", id="preview-url", classes="detail-value")
            with Horizontal(classes="detail-row"):
                yield Label("Email", classes="detail-label")
                yield Label("-", id="preview-email", classes="detail-value")
            with Horizontal(classes="detail-row"):
                yield Label("Username", classes="detail-label")
                yield Label("-", id="preview-username", classes="detail-value")
            with Horizontal(classes="detail-row"):
                yield Label("Password", classes="detail-label")
                yield Label("-", id="preview-password", classes="detail-value")
            with Horizontal(classes="detail-row"):
                yield Label("Notes", classes="detail-label")
                yield Label("-", id="preview-notes", classes="detail-value")
            with Horizontal(classes="detail-row"):
                yield Label("Created Date", classes="detail-label")
                yield Label("-", id="preview-created", classes="detail-value")
            with Horizontal(classes="detail-row"):
                yield Label("Updated Date", classes="detail-label")
                yield Label("-", id="preview-updated", classes="detail-value")

    def update_entry(self, entry: Entry | None, emails_list: list):
        self.entry = entry
        self.emails_list = emails_list
        self.refresh_details()

    def refresh_details(self):
        if not self.entry:
            for item in ["site", "url", "email", "username", "password", "notes", "created", "updated"]:
                self.query_one(f"#preview-{item}", Label).update("-")
            return

        email_str = "-"
        for email in self.emails_list:
            if email.id == self.entry.email_id:
                email_str = f"{email.label} ({email.address})"
                break

        self.query_one("#preview-site", Label).update(self.entry.site.name)
        self.query_one("#preview-url", Label).update(self.entry.site.url)
        self.query_one("#preview-email", Label).update(email_str)
        self.query_one("#preview-username", Label).update(self.entry.username or "-")
        
        pass_str = self.entry.password if self.reveal_password else "••••••••••••"
        self.query_one("#preview-password", Label).update(pass_str)
        
        self.query_one("#preview-notes", Label).update(self.entry.notes or "-")
        self.query_one("#preview-created", Label).update(self.entry.created_at.strftime("%Y-%m-%d %H:%M"))
        self.query_one("#preview-updated", Label).update(self.entry.updated_at.strftime("%Y-%m-%d %H:%M"))


# ─────────────────────────────────────────────────────────
# Screens & Modal Dialogs
# ─────────────────────────────────────────────────────────

class UnlockScreen(Screen):
    """The master password unlock screen."""
    def compose(self) -> ComposeResult:
        storage = LocalStorage()
        vault_exists = storage.exists()

        title = "ELK PASSWORD MANAGER"
        if not vault_exists:
            subtitle = "No vault found. Create a Master Password to initialize."
            btn_text = "Create Vault"
        else:
            subtitle = "Vault is locked. Enter master password."
            btn_text = "Unlock Vault"

        with Container(id="unlock-card"):
            yield Label(title, id="unlock-title")
            yield Label(subtitle, id="unlock-subtitle")
            yield PasswordField()
            yield Label("", id="unlock-error")
            yield Button(btn_text, id="unlock-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "unlock-btn":
            self.submit_password()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "unlock-password":
            self.submit_password()

    def submit_password(self) -> None:
        password_input = self.query_one("#unlock-password", Input)
        password = password_input.value
        error_label = self.query_one("#unlock-error", Label)

        if not password:
            error_label.update("Password cannot be empty")
            return

        storage = LocalStorage()

        try:
            if password.lower() == "demo":
                self.app.mock_mode = True
                
                # Mock a decrypted Vault structure
                class MockVault:
                    def __init__(self):
                        self.entries = list(MOCK_ENTRIES)
                        self.emails = list(MOCK_EMAILS)
                        class MockSettings:
                            clipboard_timeout = 30
                            auto_lock_minutes = 5
                        self.settings = MockSettings()

                self.app.service._vault = MockVault()
                self.app.switch_screen(HomeScreen())
                self.notify("Unlocked demo mode!", severity="information")
                return

            if not storage.exists():
                self.app.service.create_vault(password)
                self.app.service.unlock_vault(password)
                # Add default email account
                self.app.service.add_email(
                    Email(
                        id=RandomGenerator.generate_uuid(),
                        address="simon@gmail.com",
                        label="Personal",
                    )
                )
                self.app.service.save()
            else:
                self.app.service.unlock_vault(password)

            self.app.switch_screen(HomeScreen())
            self.notify("Vault unlocked!", severity="information")

        except Exception as e:
            error_label.update(str(e))


class HomeScreen(Screen):
    """The Main Vault screen with a three-part layout."""
    BINDINGS = [
        Binding("up,down", "navigate", "Navigate", show=False),
        Binding("left", "focus_left", "Left Panel", show=False),
        Binding("right", "focus_right", "Right Panel", show=False),
        Binding("tab", "toggle_panel_focus", "Toggle Panel", show=False),
        Binding("enter", "view_details", "View/Open Details", show=False),
        Binding("a", "add_entry", "Add Entry", show=False),
        Binding("e", "edit_entry", "Edit Entry", show=False),
        Binding("d", "delete_entry", "Delete Entry", show=False),
        Binding("y", "copy_password", "Copy Password", show=False),
        Binding("p", "toggle_password", "Toggle Password", show=False),
        Binding("slash", "focus_search", "Search", show=False),
        Binding("m", "manage_emails", "Emails", show=False),
        Binding("s", "open_settings", "Settings", show=False),
        Binding("h", "about", "About", show=False),
        Binding("q", "quit_app", "Quit", show=False),
        Binding("escape", "clear_search", "Clear Search", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="home-header"):
            yield Label("ELK PASSWORD MANAGER", id="app-title")
            yield Label("Vault Unlocked", id="vault-status")

        with Container(id="search-container"):
            yield Label("🔍", id="search-icon")
            yield SearchBar(placeholder="Type / to search...", id="search-bar")

        with Container(id="entry-list-container"):
            with LeftPanel(id="left-panel"):
                yield ListView(id="entry-list")
            with RightPanel(id="right-panel"):
                yield DetailsPreview(id="details-preview")

        yield AppFooter()

    def on_mount(self) -> None:
        self.refresh_list()
        self.query_one("#entry-list").focus()

    def refresh_list(self, result=None) -> None:
        entry_list = self.query_one("#entry-list", ListView)
        entry_list.clear()

        entries = self.app.service.get_entries()
        emails = self.app.service.get_emails()

        if not entries:
            entry_list.append(EmptyRow())
            self.query_one("#details-preview", DetailsPreview).update_entry(None, emails)
        else:
            for entry in entries:
                email_lbl = "-"
                for email in emails:
                    if email.id == entry.email_id:
                        email_lbl = email.label
                        break
                entry_list.append(EntryRow(entry, email_lbl))

            # Select first item and update preview
            entry_list.index = 0
            self.query_one("#details-preview", DetailsPreview).update_entry(entries[0], emails)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if isinstance(event.item, EntryRow):
            emails = self.app.service.get_emails()
            self.query_one("#details-preview", DetailsPreview).update_entry(event.item.entry, emails)
        else:
            self.query_one("#details-preview", DetailsPreview).update_entry(None, [])

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, EntryRow):
            self.app.push_screen(DetailsScreen(event.item.entry), self.refresh_list)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-bar":
            self.filter_entries(event.value)

    def filter_entries(self, query: str) -> None:
        entry_list = self.query_one("#entry-list", ListView)
        entry_list.clear()

        entries = self.app.service.get_entries()
        emails = self.app.service.get_emails()

        filtered = []
        for entry in entries:
            if not query or query.lower() in entry.site.name.lower() or query.lower() in entry.site.url.lower():
                filtered.append(entry)

        if not filtered:
            entry_list.append(EmptyRow())
            self.query_one("#details-preview", DetailsPreview).update_entry(None, emails)
        else:
            for entry in filtered:
                email_lbl = "-"
                for email in emails:
                    if email.id == entry.email_id:
                        email_lbl = email.label
                        break
                entry_list.append(EntryRow(entry, email_lbl))
            
            entry_list.index = 0
            self.query_one("#details-preview", DetailsPreview).update_entry(filtered[0], emails)

    def action_focus_left(self) -> None:
        self.query_one("#left-panel").focus()

    def action_focus_right(self) -> None:
        self.query_one("#right-panel").focus()

    def action_toggle_panel_focus(self) -> None:
        if self.focused == self.query_one("#entry-list"):
            self.query_one("#right-panel").focus()
        else:
            self.query_one("#left-panel").focus()

    def action_view_details(self) -> None:
        active_row = self.query_one("#entry-list").highlighted_child
        if active_row and isinstance(active_row, EntryRow):
            self.app.push_screen(DetailsScreen(active_row.entry), self.refresh_list)

    def action_focus_search(self) -> None:
        self.query_one("#search-bar").focus()

    def action_clear_search(self) -> None:
        search_bar = self.query_one("#search-bar")
        if search_bar.has_focus:
            search_bar.value = ""
            self.query_one("#entry-list").focus()

    def action_toggle_password(self) -> None:
        preview = self.query_one("#details-preview", DetailsPreview)
        preview.reveal_password = not preview.reveal_password
        preview.refresh_details()
        self.notify("Password visibility toggled", severity="information")

    def action_copy_password(self) -> None:
        active_row = self.query_one("#entry-list").highlighted_child
        if active_row and isinstance(active_row, EntryRow):
            pyperclip.copy(active_row.entry.password)
            self.notify("Password copied to clipboard!", severity="information")

    def action_add_entry(self) -> None:
        emails = self.app.service.get_emails()
        if not emails:
            self.notify("Please add an email account first!", severity="warning")
            return
        self.app.push_screen(EditEntryScreen(mode="add"), self.refresh_list)

    def action_edit_entry(self) -> None:
        active_row = self.query_one("#entry-list").highlighted_child
        if active_row and isinstance(active_row, EntryRow):
            self.app.push_screen(EditEntryScreen(mode="edit", entry=active_row.entry), self.refresh_list)

    def action_delete_entry(self) -> None:
        active_row = self.query_one("#entry-list").highlighted_child
        if active_row and isinstance(active_row, EntryRow):
            self.app.push_screen(DeleteConfirmationModal(entry=active_row.entry), self.refresh_list)

    def action_manage_emails(self) -> None:
        self.app.push_screen(EmailsScreen(), self.refresh_list)

    def action_open_settings(self) -> None:
        self.app.push_screen(SettingsScreen())

    def action_about(self) -> None:
        self.app.push_screen(AboutModal())

    def action_quit_app(self) -> None:
        self.app.service.lock()
        self.app.exit()


class DetailsScreen(Screen):
    """Full-screen detail view for a specific entry."""
    def __init__(self, entry: Entry, **kwargs):
        super().__init__(**kwargs)
        self.entry = entry
        self.reveal_password = False

    def compose(self) -> ComposeResult:
        with Container(id="details-header"):
            yield Label(self.entry.site.name, id="details-site-name")

        with ScrollableContainer(id="details-body"):
            with Horizontal(classes="detail-row"):
                yield Label("Site Name", classes="detail-label")
                yield Label(self.entry.site.name, classes="detail-value")
            with Horizontal(classes="detail-row"):
                yield Label("URL", classes="detail-label")
                yield Label(self.entry.site.url, classes="detail-value")
            
            email_str = "-"
            for email in self.app.service.get_emails():
                if email.id == self.entry.email_id:
                    email_str = f"{email.label} ({email.address})"
                    break

            with Horizontal(classes="detail-row"):
                yield Label("Email", classes="detail-label")
                yield Label(email_str, classes="detail-value")
            with Horizontal(classes="detail-row"):
                yield Label("Username", classes="detail-label")
                yield Label(self.entry.username or "-", classes="detail-value")
            with Horizontal(classes="detail-row"):
                yield Label("Password", classes="detail-label")
                yield Label("••••••••••••", id="details-password", classes="detail-value")
            with Horizontal(classes="detail-row"):
                yield Label("Notes", classes="detail-label")
                yield Label(self.entry.notes or "-", classes="detail-value")
            with Horizontal(classes="detail-row"):
                yield Label("Created Date", classes="detail-label")
                yield Label(self.entry.created_at.strftime("%Y-%m-%d %H:%M:%S"), classes="detail-value")
            with Horizontal(classes="detail-row"):
                yield Label("Updated Date", classes="detail-label")
                yield Label(self.entry.updated_at.strftime("%Y-%m-%d %H:%M:%S"), classes="detail-value")

        with Container(id="details-actions"):
            yield Button("Copy Password", id="btn-copy-pass", classes="btn-primary")
            yield Button("Reveal Password", id="btn-toggle-pass", classes="btn-secondary")
            yield Button("Edit Entry", id="btn-edit", classes="btn-secondary")
            yield Button("Delete Entry", id="btn-delete", classes="btn-danger")
            yield Button("Back", id="btn-back", classes="btn-secondary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.dismiss(False)
        elif event.button.id == "btn-copy-pass":
            pyperclip.copy(self.entry.password)
            self.notify("Password copied!", severity="information")
        elif event.button.id == "btn-toggle-pass":
            self.reveal_password = not self.reveal_password
            pass_label = self.query_one("#details-password", Label)
            if self.reveal_password:
                pass_label.update(self.entry.password)
                event.button.label = "Hide Password"
            else:
                pass_label.update("••••••••••••")
                event.button.label = "Reveal Password"
        elif event.button.id == "btn-edit":
            self.app.push_screen(EditEntryScreen(mode="edit", entry=self.entry), self.on_form_returned)
        elif event.button.id == "btn-delete":
            self.app.push_screen(DeleteConfirmationModal(entry=self.entry), self.on_delete_returned)

    def on_form_returned(self, result: bool) -> None:
        if result:
            self.dismiss(True)

    def on_delete_returned(self, result: bool) -> None:
        if result:
            self.dismiss(True)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(False)


class EditEntryScreen(Screen):
    """Screen for adding or editing password credentials."""
    def __init__(self, mode="add", entry=None, **kwargs):
        super().__init__(**kwargs)
        self.mode = mode
        self.entry = entry

    def compose(self) -> ComposeResult:
        title = "ADD NEW ENTRY" if self.mode == "add" else f"EDIT {self.entry.site.name.upper()}"

        with Container(id="edit-header"):
            yield Label(title, id="edit-title")

        with ScrollableContainer(id="edit-form"):
            # Site Name
            with Container(classes="form-field"):
                yield Label("Site Name", classes="form-label")
                yield Input(
                    value=self.entry.site.name if self.entry else "",
                    placeholder="e.g. GitHub",
                    id="edit-site-name"
                )
                yield Label("", classes="form-error", id="err-site-name")

            # Site URL
            with Container(classes="form-field"):
                yield Label("Site URL", classes="form-label")
                yield Input(
                    value=self.entry.site.url if self.entry else "",
                    placeholder="e.g. github.com",
                    id="edit-site-url"
                )
                yield Label("", classes="form-error", id="err-site-url")

            # Email Account Select
            emails = self.app.service.get_emails()
            email_choices = [(e.label, e.id) for e in emails]
            default_email_id = self.entry.email_id if self.entry else (emails[0].id if emails else None)

            with Container(classes="form-field"):
                yield Label("Email Account", classes="form-label")
                yield Select(
                    email_choices,
                    value=default_email_id,
                    id="edit-email-id",
                    prompt="Select Email Account"
                )
                yield Label("", classes="form-error", id="err-email-id")

            # Username
            with Container(classes="form-field"):
                yield Label("Username", classes="form-label")
                yield Input(
                    value=self.entry.username if (self.entry and self.entry.username) else "",
                    placeholder="e.g. SimonCodes",
                    id="edit-username"
                )
                yield Label("", classes="form-error", id="err-username")

            # Password
            with Container(classes="form-field"):
                yield Label("Password", classes="form-label")
                yield Input(
                    value=self.entry.password if self.entry else "",
                    password=True,
                    placeholder="Enter password",
                    id="edit-password"
                )
                yield Label("", classes="form-error", id="err-password")

            # Notes
            with Container(classes="form-field"):
                yield Label("Notes", classes="form-label")
                yield Input(
                    value=self.entry.notes if (self.entry and self.entry.notes) else "",
                    placeholder="e.g. 2FA Enabled",
                    id="edit-notes"
                )
                yield Label("", classes="form-error", id="err-notes")

        with Container(id="edit-footer"):
            yield Button("Save", id="btn-save", classes="btn-primary")
            yield Button("Cancel", id="btn-cancel", classes="btn-secondary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(False)
        elif event.button.id == "btn-save":
            self.save_form()

    def save_form(self) -> None:
        site_name = self.query_one("#edit-site-name", Input).value.strip()
        site_url = self.query_one("#edit-site-url", Input).value.strip()
        email_id = self.query_one("#edit-email-id", Select).value
        username = self.query_one("#edit-username", Input).value.strip()
        password = self.query_one("#edit-password", Input).value.strip()
        notes = self.query_one("#edit-notes", Input).value.strip()

        has_error = False

        for f in ["site-name", "site-url", "email-id", "password"]:
            self.query_one(f"#err-{f}", Label).update("")

        if not site_name:
            self.query_one("#err-site-name", Label).update("Site name is required")
            has_error = True
        if not site_url:
            self.query_one("#err-site-url", Label).update("Site URL is required")
            has_error = True
        if not email_id or email_id is Select.BLANK:
            self.query_one("#err-email-id", Label).update("Email account is required")
            has_error = True
        if not password:
            self.query_one("#err-password", Label).update("Password is required")
            has_error = True

        if has_error:
            return

        if self.mode == "add":
            new_entry = Entry(
                id=RandomGenerator.generate_uuid(),
                site=Site(name=site_name, url=site_url),
                email_id=email_id,
                username=username or None,
                password=password,
                notes=notes or None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.app.service.add_entry(new_entry)
        else:
            self.entry.site.name = site_name
            self.entry.site.url = site_url
            self.entry.email_id = email_id
            self.entry.username = username or None
            self.entry.password = password
            self.entry.notes = notes or None
            self.entry.updated_at = datetime.now()
            self.app.service.update_entry(self.entry)

        if not self.app.mock_mode:
            self.app.service.save()

        self.notify("Entry saved successfully!", severity="information")
        self.dismiss(True)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(False)


class EmailsScreen(Screen):
    """Screen for managing configured email identities."""
    def compose(self) -> ComposeResult:
        with Container(id="emails-header"):
            yield Label("EMAIL ACCOUNTS", id="emails-title")

        yield ScrollableContainer(id="emails-body")

        with Container(id="emails-footer"):
            yield Button("Add Email", id="btn-add-email", classes="btn-primary")
            yield Button("Delete Email", id="btn-delete-email", classes="btn-danger")
            yield Button("Back", id="btn-back", classes="btn-secondary")

    def on_mount(self) -> None:
        self.refresh_emails()

    def refresh_emails(self) -> None:
        body = self.query_one("#emails-body")
        for child in list(body.children):
            child.remove()

        emails = self.app.service.get_emails()
        for email in emails:
            card = Container(classes="email-card")
            card.can_focus = True
            card.email_id = email.id
            card.mount(
                Label(email.address, classes="email-card-address"),
                Label(email.label, classes="email-card-label")
            )
            body.mount(card)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.dismiss()
        elif event.button.id == "btn-add-email":
            self.app.push_screen(AddEmailModal(), self.on_email_added)
        elif event.button.id == "btn-delete-email":
            focused = self.focused
            if focused and "email-card" in focused.classes:
                email_id = focused.email_id
                entries = self.app.service.get_entries()
                used = any(e.email_id == email_id for e in entries)
                if used:
                    self.notify("Cannot delete: Email is used by credentials", severity="warning")
                else:
                    self.app.service.delete_email(email_id)
                    if not self.app.mock_mode:
                        self.app.service.save()
                    self.notify("Email deleted successfully", severity="information")
                    self.refresh_emails()
            else:
                self.notify("Select an email entry card first", severity="warning")

    def on_email_added(self, result: bool) -> None:
        if result:
            self.refresh_emails()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss()


class SettingsScreen(Screen):
    """Settings Screen showing configuration parameters."""
    def compose(self) -> ComposeResult:
        with Container(id="settings-header"):
            yield Label("SETTINGS", id="settings-title")

        with ScrollableContainer(id="settings-body"):
            yield Label("Security Settings", classes="settings-section-title")
            with Container(classes="settings-row"):
                yield Label("Clipboard Auto-clear Timeout", classes="settings-row-label")
                yield Label("30 seconds", classes="settings-row-value")
            with Container(classes="settings-row"):
                yield Label("Auto-lock Vault Timeout", classes="settings-row-label")
                yield Label("5 minutes", classes="settings-row-value")

            yield Label("Preferences", classes="settings-section-title")
            with Container(classes="settings-row"):
                yield Label("Application Theme", classes="settings-row-label")
                yield Label("Dark Glass (Obsidian)", classes="settings-row-value")
            with Container(classes="settings-row"):
                yield Label("Cloud Sync Provider", classes="settings-row-label")
                yield Label("None (Local-only)", classes="settings-row-value")

            yield Label("Password Generator Defaults", classes="settings-section-title")
            with Container(classes="settings-row"):
                yield Label("Default Length", classes="settings-row-label")
                yield Label("16 characters", classes="settings-row-value")
            with Container(classes="settings-row"):
                yield Label("Include Symbols & Numbers", classes="settings-row-label")
                yield Label("Yes", classes="settings-row-value")

            yield Label("Press [bold]Escape[/] to return", classes="settings-placeholder")

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss()


class DeleteConfirmationModal(ModalScreen):
    """Centered confirmation dialog for entry deletion."""
    def __init__(self, entry: Entry, **kwargs):
        super().__init__(**kwargs)
        self.entry = entry

    def compose(self) -> ComposeResult:
        with Container(id="modal-card"):
            yield Label("Delete Password Entry", id="modal-title")
            yield Label(
                f"Are you sure you want to delete credentials for '{self.entry.site.name}'? "
                "This action cannot be undone.",
                id="modal-message"
            )
            with Container(id="modal-actions"):
                yield Button("Delete", id="btn-confirm-delete", classes="btn-danger")
                yield Button("Cancel", id="btn-cancel-delete", classes="btn-secondary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-confirm-delete":
            self.app.service.delete_entry(self.entry.id)
            if not self.app.mock_mode:
                self.app.service.save()
            self.notify("Entry deleted successfully", severity="information")
            self.dismiss(True)
        elif event.button.id == "btn-cancel-delete":
            self.dismiss(False)


class AddEmailModal(ModalScreen):
    """Centered modal input dialog for adding a new email account."""
    def compose(self) -> ComposeResult:
        with Container(id="modal-card"):
            yield Label("Add Email Account", id="modal-title")
            yield Label("Enter the email details below:", id="modal-message")

            yield Input(placeholder="e.g. simon@gmail.com", id="new-email-address")
            yield Label("", classes="form-error", id="err-new-email-address")
            yield Input(placeholder="Label (e.g. Personal)", id="new-email-label")
            yield Label("", classes="form-error", id="err-new-email-label")

            with Container(id="modal-actions"):
                yield Button("Add Account", id="btn-confirm-add-email", classes="btn-primary")
                yield Button("Cancel", id="btn-cancel-add-email", classes="btn-secondary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel-add-email":
            self.dismiss(False)
        elif event.button.id == "btn-confirm-add-email":
            address = self.query_one("#new-email-address", Input).value.strip()
            label = self.query_one("#new-email-label", Input).value.strip()

            has_error = False
            if not address or "@" not in address:
                self.notify("Valid email address is required", severity="warning")
                has_error = True
            if not label:
                self.notify("Label is required", severity="warning")
                has_error = True

            if has_error:
                return

            new_email = Email(
                id=RandomGenerator.generate_uuid(),
                address=address,
                label=label
            )
            self.app.service.add_email(new_email)
            if not self.app.mock_mode:
                self.app.service.save()
            self.notify("Email account added successfully!", severity="information")
            self.dismiss(True)


class AboutModal(ModalScreen):
    """Centered info dialog for About screen."""
    def compose(self) -> ComposeResult:
        with Container(id="modal-card"):
            yield Label("About Elk Password Manager", id="modal-title")
            yield Label(
                "Elk Password Manager v0.1.0\n\n"
                "A modern, local-first, keyboard-centric password vault built with Python and Textual.\n\n"
                "Inspired by LazyGit, k9s, and Lazydocker.\n\n"
                "Designed for maximum security and ease of use.",
                id="modal-message"
            )
            with Container(id="modal-actions"):
                yield Button("Close", id="btn-close-about", classes="btn-primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close-about":
            self.dismiss()


# ─────────────────────────────────────────────────────────
# Main TUI App Entry Class
# ─────────────────────────────────────────────────────────

class ElkPasswordManagerApp(App):
    """Main Textual application for Elk Password Manager."""
    CSS_PATH = "styles.tcss"
    TITLE = "Elk Password Manager"

    def __init__(self, service: VaultService = None, **kwargs):
        super().__init__(**kwargs)
        self.service = service or VaultService()
        self.mock_mode = False

    def on_mount(self) -> None:
        self.push_screen(UnlockScreen())


if __name__ == "__main__":
    app = ElkPasswordManagerApp()
    app.run()
