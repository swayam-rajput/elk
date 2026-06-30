from pathlib import Path
import json
from dataclasses import asdict

from models.enc_vault import EncryptedVault, EncryptionMetadata, KDFMetadata
from storage.local import LocalStorage
from vault.service import VaultService

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

    service = VaultService()

    if not storage.exists():
        print('Creating new vault')

        master_pass = input('Create Master Password: ')

        encrypted_vault = service.create_vault(
            master_password=master_pass,
            
        )

        save_encrypted_vault(
            storage,
            encrypted_vault
        )

        print('Vault created successfully')
    
    else:
        print('Vault found.')

        master_password = input(
            'Master Password: '
        )
        encrypted_vault = load_encrypted_vault(
            storage
        )
        try:
            vault = service.unlock_vault(
                encrypted_vault,
                master_password
            )

            print("\nVault decrypted successfully\n")
            print(vault)
        except ValueError as e:
            print(e)
if __name__ == "__main__":
    main()
