from pathlib import Path
import json
from dataclasses import asdict

from models.enc_vault import EncryptedVault, EncryptionMetadata, KDFMetadata
from storage.local import LocalStorage
from vault.service import VaultService
from ui.app import PasswordManager
from storage.github import GitHubStorage
from sync.sync_manager import SyncManager
from profiles.manager import ProfileManager

def save_encrypted_vault(storage: LocalStorage, vault: EncryptedVault) -> None:
    """
    Saves an EncryptedVault object as JSON
    """

    with open(storage.vault_path, 'w', encoding='utf-8') as file:
        json.dump(
            asdict(vault),
            file,
            indent=4
        )

from config.settings_manager import SettingsManager
import requests
def select_profile(profile_manager: ProfileManager):
    profiles = profile_manager.list_profiles()

    print("\nProfiles:")

    for index, profile in enumerate(profiles, start=1):
        print(f"{index}. {profile.name}")

    print("N. Create new profile")

    while True:
        choice = input("\nSelect profile: ").strip()

        if choice.lower() == "n":
            name = input("Profile name: ").strip()

            try:
                profile = profile_manager.create_profile(name)
                print(f"Created profile: {profile.name}")
                return profile
            except ValueError as e:
                print(e)
                continue

        try:
            index = int(choice) - 1
            return profiles[index]
        except (ValueError, IndexError):
            print("Invalid selection.")

def main():
    profile_manager = ProfileManager()
    profile = select_profile(profile_manager)
    profile_manager.set_active_profile(profile.id)

    active_profile = profile_manager.get_active_profile()

    if active_profile is None:
        raise RuntimeError("No active profile found.")

    storage = LocalStorage(active_profile.vault_path)

    settings_manager = SettingsManager()
    settings = settings_manager.load()

    service = VaultService(storage)

    if not storage.exists():
        while True:
            master_password = input("Create Master Password: ")
            confirm = input("Confirm Master Password: ")

            if master_password == confirm:
                break

            print("Passwords do not match. Please try again.")

        service.create_vault(master_password)

    else:
        master_password = input("Master Password: ")

        try:
            service.unlock_vault(master_password)

        except ValueError as e:
            print(e)
            input()
            return

    if settings.github_enabled:
        token = service.decrypt_token(settings.github_token)

        github = GitHubStorage(
            settings.github_username,
            settings.github_repository,
            token,
            profile.id
        )

        sync_man = SyncManager(storage, github)
        service.sync_manager = sync_man

    app = PasswordManager(service, settings_manager)
    app.run()

    if service.dirty:
        print("Changes Detected\nSyncing...")

        service.save()

        if settings.auto_sync:
            service.sync()

    else:
        print("No Changes Detected")
if __name__ == "__main__":
    main()
