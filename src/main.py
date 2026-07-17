from pathlib import Path
import json
from dataclasses import asdict

from models.enc_vault import EncryptedVault, EncryptionMetadata, KDFMetadata
from storage.local import LocalStorage
from vault.service import VaultService
from ui.app import PasswordManager
from storage.github import GitHubStorage
from sync.sync_manager import SyncManager

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

def main():
    storage = LocalStorage()
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
            return

    if settings.github_enabled:
        token = service.decrypt_token(settings.github_token)
        github = GitHubStorage(settings.github_username, settings.github_repository, token)
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
