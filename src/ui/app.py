from textual.app import App, Binding

from profiles.manager import ProfileManager
from profiles.model import Profile
from config.settings_manager import SettingsManager
from vault.service import VaultService


class PasswordManager(App):
    """Main Textual application.

    Startup flow (all inside Textual, no input() calls):
        1. If >1 profile  →  ProfileSelectScreen
        2. Profile chosen →  UnlockScreen  (create vault on first use)
        3. Vault unlocked →  PasswordsScreen  (main UI)

    GitHub sync is wired up automatically after unlock if configured.
    """

    CSS_PATH = "style.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("1", "tab_passwords", "Passwords", show=False),
        Binding("2", "tab_emails", "Emails", show=False),
        Binding("3", "tab_settings", "Settings", show=False),
    ]

    def __init__(self, profile_manager: ProfileManager, settings_manager: SettingsManager):
        super().__init__()
        self.profile_manager = profile_manager
        self.settings_manager = settings_manager
        # Set after vault is unlocked
        self.service: VaultService | None = None
        self.active_profile: Profile | None = None

    # ── Startup flow ────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        profiles = self.profile_manager.list_profiles()
        if len(profiles) > 1:
            default = self.profile_manager.get_default_profile() or profiles[0]
            from ui.screens.profile_select import ProfileSelectScreen
            self.push_screen(
                ProfileSelectScreen(self.profile_manager, default),
                self._on_profile_selected,
            )
        else:
            self._open_unlock(profiles[0], has_multiple=False)

    def _on_profile_selected(self, profile: Profile | None) -> None:
        if profile is None:
            self.exit()
            return
        self._open_unlock(profile, has_multiple=True)

    def _open_unlock(self, profile: Profile, has_multiple: bool = False) -> None:
        from ui.screens.unlock import UnlockScreen
        from storage.local import LocalStorage

        self.active_profile = profile
        self.profile_manager.set_active_profile(profile.id)
        storage = LocalStorage(profile.vault_path)
        self.push_screen(
            UnlockScreen(storage, profile, has_multiple_profiles=has_multiple),
            self._on_vault_unlocked,
        )

    def _on_vault_unlocked(self, service: VaultService | None) -> None:
        if service is None:
            # User pressed Back → re-show profile selector
            profiles = self.profile_manager.list_profiles()
            default = self.profile_manager.get_default_profile() or profiles[0]
            from ui.screens.profile_select import ProfileSelectScreen
            self.push_screen(
                ProfileSelectScreen(self.profile_manager, default),
                self._on_profile_selected,
            )
            return

        self.service = service
        self._setup_github_sync()

        from ui.screens.passwords import PasswordsScreen
        self.push_screen(PasswordsScreen(service, self.settings_manager))

    def _setup_github_sync(self) -> None:
        """Wire up GitHubStorage + SyncManager if the user has GitHub sync configured."""
        if self.service is None or self.active_profile is None:
            return
        settings = self.settings_manager.settings
        if not settings.github_enabled:
            return
        try:
            from storage.github import GitHubStorage
            from storage.local import LocalStorage
            from sync.sync_manager import SyncManager

            token = self.service.decrypt_token(settings.github_token)
            github = GitHubStorage(
                settings.github_username,
                settings.github_repository,
                token,
                self.active_profile.id,
            )
            sync_man = SyncManager(
                LocalStorage(self.active_profile.vault_path),
                github,
            )
            self.service.sync_manager = sync_man
        except Exception:
            self.notify("GitHub sync configuration error.", severity="warning")

    # ── Tab switching ───────────────────────────────────────────────────────

    def action_tab_passwords(self) -> None:
        from ui.screens.passwords import PasswordsScreen
        self._switch_to(PasswordsScreen)

    def action_tab_emails(self) -> None:
        from ui.screens.emails import EmailsScreen
        self._switch_to(EmailsScreen)

    def action_tab_settings(self) -> None:
        from ui.screens.settings import SettingsScreen
        self._switch_to(SettingsScreen)

    def _switch_to(self, screen_class) -> None:
        self.pop_screen()
        self.push_screen(screen_class(self.service, self.settings_manager))
