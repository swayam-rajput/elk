import json
from dataclasses import asdict
from pathlib import Path

from models.enc_vault import (
    EncryptedVault,
    EncryptionMetadata,
    KDFMetadata,
)
from storage.provider import StorageProvider


class LocalStorage(StorageProvider):
    """
    Handles reading and writing the encrypted vault
    from the local filesystem.
    """

    def __init__(self, vault_path: str = "vault/encrypted-vault.json"):
        self.vault_path = Path(vault_path)
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        return self.vault_path.exists()

    def load(self) -> EncryptedVault:
        """
        Loads the encrypted vault from disk.
        """

        with open(self.vault_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return EncryptedVault(
            version=data["version"],
            kdf=KDFMetadata(
                algorithm=data["kdf"]["algorithm"],
                memory=data["kdf"]["memory"],
                iterations=data["kdf"]["iterations"],
                parallelism=data["kdf"]["parallelism"],
                salt=data["kdf"]["salt"],
            ),
            encryption=EncryptionMetadata(
                algorithm=data["encryption"]["algorithm"],
                nonce=data["encryption"]["nonce"],
            ),
            ciphertext=data["ciphertext"],
        )

    def save(self, vault: EncryptedVault) -> None:
        """
        Saves the encrypted vault to disk.
        """

        with open(self.vault_path, "w", encoding="utf-8") as file:
            json.dump(
                asdict(vault),
                file,
                indent=4,
            )

    def delete(self) -> None:
        """
        Deletes the encrypted vault.
        """

        if self.exists():
            self.vault_path.unlink()