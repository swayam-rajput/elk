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
    def __init__(self, key: str, label: str, value: int, description: str, editable: bool = True, action: str | None = None, editor: str = 'number'):
        self.key = key
        self.label = label
        self.value = value
        self.description = description
        self.editable = editable
        self.action = action
        self.editor = editor


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
        yield CustomHeader(active_tab=3, item_count=6, item_type="settings")
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

        if not self._selected_item.editable:
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

        try:

            match self._selected_item.editor:

                case "number":

                    if self.service.vault is None:
                        return

                    value = int(data["value"])

                    setattr(
                        self.service.vault.settings,
                        data["key"],
                        value,
                    )

                    self.service._dirty = True
                    self.service.save()

                case "export":

                    self.service.export_backup(
                        data["destination"],
                    )

                    self.notify(
                        "Vault exported successfully.",
                    )

                case "import":

                    self.service.import_vault(
                        data["source"],
                    )

                    self.notify(
                        "Vault imported successfully.\nPlease unlock again.",
                    )

                    self.app.pop_screen()

                case "github_sync":
                    username = data["username"]
                    repository = data["repository"]
                    token = data["token"]

                    if not username or not repository or not token:
                        raise ValueError("Please complete every field.")

                    from storage.github import GitHubStorage
                    github = GitHubStorage(
                        username=username,
                        repository=repository,
                        token=token
                    )
                    if not github.authenticate():
                        raise ValueError("GitHub authentication failed.")

                    settings = self.settings_manager.settings
                    settings.github_enabled = True
                    settings.github_username = username
                    settings.github_repository = repository
                    settings.github_token = self.service.encrypt_token(token)

                    self.settings_manager.save()

                    # Update active storage / sync manager on the service
                    from storage.local import LocalStorage
                    from sync.sync_manager import SyncManager
                    sync_man = SyncManager(LocalStorage(), github)
                    self.service.sync_manager = sync_man

                    self.notify("GitHub Sync configured successfully.")

                case "change_master_password":
                    current_pw = data["current_password"]
                    new_pw = data["new_password"]
                    confirm_pw = data["confirm_password"]

                    if not current_pw or not new_pw or not confirm_pw:
                        raise ValueError("Please fill out all fields.")

                    if new_pw != confirm_pw:
                        raise ValueError("New passwords do not match.")

                    settings = self.settings_manager.settings
                    old_encrypted_token = settings.github_token if settings.github_enabled else ""

                    new_encrypted_token = self.service.change_master_password(
                        current_pw,
                        new_pw,
                        old_encrypted_token
                    )

                    if settings.github_enabled and new_encrypted_token:
                        settings.github_token = new_encrypted_token
                        self.settings_manager.save()
                        print("Master Password changed, syncing...")
                        if not self.service.sync():
                            self.notify(
                                "Master password changed, but GitHub sync failed.",
                                severity="warning",
                            )
                            return
                        print("Sync Complete")
                    
                    self.notify("Master password updated successfully.")

        except Exception as e:
            print(e)
            self.notify(
                str(e),
                severity="error",
            )

            return

        self._editing = False

        self._refresh_settings()

        self.query_one(
            ScrollableList,
        ).focus()
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
                editable=True,
                editor="github_sync",
            ),
            SettingItem(
                key="change_master_password",
                label="Change Master Password",
                value="",
                description="\n[#B0B4BF]Change the master password used to lock/unlock your vault. This will re-encrypt your entire database and any configured cloud keys with the new password.[/]",
                editable=True,
                editor="change_master_password",
            ),
            SettingItem(
                key="export_vault",
                label="Export Encrypted Vault",
                value='',
                description="Export the encrypted vault.",
                # editable=False,
                
                editor="export",
            ),

            SettingItem(
                key="import_vault",
                label="Import Encrypted Vault",
                value="",
                description="Replace the current vault with another encrypted vault.",
                # editable=False,
                
                editor="import",
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
