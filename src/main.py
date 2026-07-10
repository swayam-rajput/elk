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

def main():

    storage = LocalStorage()
    service = VaultService(storage)

    if not storage.exists():

        master_password = input(
            "Create Master Password: "
        )

        service.create_vault(master_password)

    else:

        master_password = input(
            "Master Password: "
        )

        try:
            service.unlock_vault(master_password)

        except ValueError as e:
            print(e)
            return

    app = PasswordManager(service)
    print('app')
    app.run()
    print('synced')
    service.sync()
if __name__ == "__main__":
    main()
