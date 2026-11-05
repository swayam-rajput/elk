import sys
from pathlib import Path
# Resolve the 'src' directory relative to this file and add it to sys.path
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import getpass
from config.settings_manager import SettingsManager
from storage.local import LocalStorage
from storage.github import GitHubStorage
from sync.sync_manager import SyncManager
from vault.service import VaultService
from phone.app import PhoneApp
from profiles.manager import ProfileManager

def main():
    profile_manager = ProfileManager()
    profile = profile_manager.get_active_profile()

    storage = LocalStorage(profile.vault_path)

    settings_manager = SettingsManager(
        path=f"data/profiles/{profile.id}/settings.json"
    )
    settings = settings_manager.load()
    service = VaultService(storage)

    if not storage.exists():
        print("Vault not found. Please create one using the desktop app.")
        return

    while True:
        # Unlock Vault
        max_attempts = 3
        unlocked = False
        password = None
        for attempt in range(max_attempts):
            password = getpass.getpass("Master Password: ")
            try:
                service.unlock_vault(password)
                unlocked = True
                break
            except ValueError as e:
                print(f"Error: {e} ({max_attempts - attempt - 1} attempts left)")

        if not unlocked:
            return

        # Optional Sync on Startup
        if settings.github_enabled:
            try:
                token = service.decrypt_token(settings.github_token)
                github = GitHubStorage(settings.github_username, settings.github_repository, token, profile.id)
                sync_man = SyncManager(storage, github)
                service.sync_manager = sync_man

                print("Checking remote sync...")
                if sync_man.sync():
                    # Reload the vault with the derived key in case local file was updated
                    service.unlock_vault(password)
            except Exception as e:
                print(f"Sync failed: {e}")

        # Launch UI App
        app = PhoneApp(service)
        try:
            app.run()
        except KeyboardInterrupt:
            print("\nExiting...")
            break

        # Save & Sync on exit if dirty
        if service.dirty:
            print("Saving changes...")
            service.save()
            if settings.github_enabled and settings.auto_sync:
                print("Syncing changes to GitHub...")
                service.sync()
        else:
            print("No changes to save.")

        if app.locked_by_user:
            service.lock()
            print("\nVault locked.")
            continue
        break

if __name__ == "__main__":
    main()
