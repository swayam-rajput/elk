from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer

from vault.service import VaultService
from ui.messages import SelectionChanged
from ui.widgets.entry_details import DetailPanel, EditForm
from ui.widgets.entry_list import ScrollableList
from ui.widgets.custom_header import CustomHeader


class SettingItem:
    def __init__(self, key: str, label: str, value: int, description: str, editable: bool = True, action: str | None = None):
        self.key = key
        self.label = label
        self.value = value
        self.description = description
        self.editable = editable
        self.action = action


class SettingsScreen(Screen):
    BINDINGS = [
        ("e", "edit_setting", "Edit"),
        ("ctrl+s", "save_setting", "Save"),
        ("escape", "cancel_edit", "Cancel"),
    ]

    def __init__(self, service: VaultService, settings_manager=None):
        super().__init__()
        self.service = service
        self.settings_manager = settings_manager
        self._items = []
        self._selected_item = None
        self._editing = False

    def compose(self) -> ComposeResult:
        yield CustomHeader(active_tab=3, item_count=2, item_type="settings")
        with Horizontal(id="main-layout"):
            yield ScrollableList(id="entry-list")
            yield DetailPanel(id="entry-details")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_settings()

    def on_selection_changed(self, message: SelectionChanged) -> None:
        if 0 <= message.index < len(self._items):
            self._selected_item = self._items[message.index]
            if not self._editing:
                detail = self.query_one(DetailPanel)
                detail.show_item(self._selected_item)

    def action_edit_setting(self) -> None:
        if self._selected_item is None or self._editing:
            return
        
        if self._selected_item.action == 'github_setup':
            from ui.screens.github_setup import GitHubSetupScreen

            self.app.push_screen(
                GitHubSetupScreen(
                    self.service,
                    self.settings_manager
                ),
                callback=lambda _: self._refresh_settings(),
            )
            return
        if not self._selected_item.editable:
            return 
        
        if self._editing:
            return
        
        self._editing = True
        detail = self.query_one(DetailPanel)
        detail.show_edit(self._selected_item)

    def action_save_setting(self) -> None:
        if not self._editing:
            return
        detail = self.query_one(DetailPanel)
        form = detail.query(EditForm).first()
        if not form:
            return
        data = form.collect()
        
        if self.service.vault and self.service.vault.settings:
            try:
                val = int(data["value"])
                setattr(self.service.vault.settings, data["key"], val)
                self.service._dirty = True
            except ValueError:
                pass
                
        self._editing = False
        self._refresh_settings()
        self.query_one(ScrollableList).focus()

    def action_cancel_edit(self) -> None:
        if not self._editing:
            return
        self._editing = False
        if self._selected_item:
            detail = self.query_one(DetailPanel)
            detail.show_item(self._selected_item)
        self.query_one(ScrollableList).focus()

    def _refresh_settings(self) -> None:
        settings = self.service.vault.settings if self.service.vault else None
        
        clipboard_val = settings.clipboard_timeout if settings else 30
        autolock_val = settings.auto_lock_minutes if settings else 5
        github_enabled = (
            self.settings_manager.settings.github_enabled
            if self.settings_manager
            else False
        )

        github_status = (
            "[#42AA22]Enabled [/]"
            if github_enabled
            else "[#B54044]Disabled [/]"
        )
        TOKEN_DESC = """
How to Personal Access Token
    1. Go to:
        GitHub -> Settings -> Developer settings -> Personal access tokens -> Fine-grained tokens

    2. Generate a new token.

    3. Repository access:
    • Only select repositories
    • Choose or create your vault repository which must be private.

    4. Repository permissions:
    • Contents -> Read and Write

    5. Paste the token below."""
        self._items = [
            SettingItem(
                key="github_sync",
                label="GitHub Sync",
                value=github_status,
                description="\n[#B0B4BF]Configure cloud synchronization.\nChanges are synced when you close the app"+TOKEN_DESC+' [/]',
                editable=False,
                action="github_setup",
            ),
            SettingItem(
                key="clipboard_timeout",
                label="Clipboard Timeout",
                value=clipboard_val,
                description="[#B0B4BF]Number of seconds before the copied password is cleared from the clipboard[/]."
            ),
            SettingItem(
                key="auto_lock_minutes",
                label="Auto Lock Timeout",
                value=autolock_val,
                description="[#B0B4BF]Minutes of inactivity before the database automatically locks[/]."
            ),
        ]
        
        entry_list = self.query_one(ScrollableList)
        select_idx = 0
        if self._selected_item:
            for idx, item in enumerate(self._items):
                if item.key == self._selected_item.key:
                    select_idx = idx
                    break
        
        entry_list.load_items(self._items, select_index=select_idx)
        
        if self._items:
            self._selected_item = self._items[select_idx]
            self.query_one(DetailPanel).show_item(self._selected_item)
        else:
            self._selected_item = None
            self.query_one(DetailPanel).remove_children()
