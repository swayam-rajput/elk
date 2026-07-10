from pathlib import Path
import json
from dataclasses import asdict

from models.enc_vault import EncryptedVault, EncryptionMetadata, KDFMetadata
from storage.local import LocalStorage
from vault.service import VaultService
from ui.app import PasswordManager

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


def load_encrypted_vault(storage: LocalStorage) -> EncryptedVault:
    with open(storage.vault_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    return EncryptedVault(
        version=data['version'],
        kdf = KDFMetadata(**data['kdf']),
        encryption=EncryptionMetadata(**data['encryption']),
        ciphertext=data['ciphertext']
    )


def main():
    storage = LocalStorage()

    service = VaultService(storage)

    if not storage.exists():
        master_password = input(
            "Create Master Password: "
        )

        service.create_vault(
            master_password
        )

    else:

        # master_password = input(
        #     "Master Password: "
        # )
        master_password = 'that'

        encrypted_vault = load_encrypted_vault(
            storage
        )

        try:

            service.unlock_vault(
                master_password,
            )
            print(service._vault)

        except ValueError as e:

            print(e)

            return

    app = PasswordManager(service)

    app.run()
if __name__ == "__main__":
    main()
