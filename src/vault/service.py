from dataclasses import asdict
import json
from cryptography.exceptions import InvalidTag

from models.entry import Entry
from models.email import Email

from models.vault import Vault
from models.enc_vault import (
    EncryptedVault,
    KDFMetadata,
    EncryptionMetadata
)

from crypto.random import RandomGenerator
from crypto.argon import Argon2KeyDeriver
from crypto.aes import AESManager
from crypto.encoding import Encoding

from storage.local import LocalStorage
from vault.serializer import VaultSerializer

class VaultService:

    def __init__(self):
        self._vault: Vault | None = None
        self._key: bytes | None = None
        self._salt: bytes | None = None

    @property
    def vault(self) -> Vault | None:
        return self._vault

    @property
    def is_unlocked(self) -> bool:
        return self._vault is not None

    def lock(self):
        self._vault = None
        self._key = None
        self._salt = None
    def create_vault(self, master_password: str):

        self._vault = Vault()

        self._salt = RandomGenerator.generate_salt()

        deriver = Argon2KeyDeriver()
        self._key = deriver.derive_key(
            master_password,
            self._salt,
        )

        plaintext = VaultSerializer.serialize(self._vault)

        nonce = RandomGenerator.generate_nonce()

        ciphertext = AESManager.encrypt(
            plaintext,
            self._key,
            nonce,
        )

        encrypted_vault = EncryptedVault(
            version=1,
            kdf=KDFMetadata(
                algorithm="argon2id",
                memory=deriver.config.memory_cost,
                iterations=deriver.config.time_cost,
                parallelism=deriver.config.parallelism,
                salt=Encoding.bytes_to_base64(self._salt),
            ),
            encryption=EncryptionMetadata(
                algorithm="aes-256-gcm",
                nonce=Encoding.bytes_to_base64(nonce),
            ),
            ciphertext=Encoding.bytes_to_base64(ciphertext),
        )

        storage = LocalStorage()

        with open(storage.vault_path, "w", encoding="utf-8") as file:
            json.dump(
                asdict(encrypted_vault),
                file,
                indent=4,
            )

    def unlock_vault(self, master_password: str):

        storage = LocalStorage()

        with open(storage.vault_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        encrypted_vault = EncryptedVault(
            version=data["version"],
            kdf=KDFMetadata(**data["kdf"]),
            encryption=EncryptionMetadata(**data["encryption"]),
            ciphertext=data["ciphertext"],
        )

        self._salt = Encoding.base64_to_bytes(
            encrypted_vault.kdf.salt
        )

        nonce = Encoding.base64_to_bytes(
            encrypted_vault.encryption.nonce
        )

        ciphertext = Encoding.base64_to_bytes(
            encrypted_vault.ciphertext
        )

        self._key = Argon2KeyDeriver().derive_key(
            master_password,
            self._salt,
        )

        try:
            plaintext = AESManager.decrypt(
                ciphertext,
                self._key,
                nonce,
            )

        except InvalidTag:
            self.lock()
            raise ValueError("Invalid master password.")

        self._vault = VaultSerializer.deserialize(
            plaintext
        )
    
    def save(self):

        if self._vault is None:
            raise ValueError("Vault is locked.")

        if self._key is None:
            raise ValueError("Vault key not found.")

        if self._salt is None:
            raise ValueError("Vault salt not found.")

        plaintext = VaultSerializer.serialize(
            self._vault
        )

        nonce = RandomGenerator.generate_nonce()

        ciphertext = AESManager.encrypt(
            plaintext,
            self._key,
            nonce,
        )

        deriver = Argon2KeyDeriver()
        encrypted_vault = EncryptedVault(
            version=1,
            kdf=KDFMetadata(
                algorithm="argon2id",
                memory=deriver.config.memory_cost,
                iterations=deriver.config.time_cost,
                parallelism=deriver.config.parallelism,
                salt=Encoding.bytes_to_base64(self._salt),
            ),
            encryption=EncryptionMetadata(
                algorithm="aes-256-gcm",
                nonce=Encoding.bytes_to_base64(nonce),
            ),
            ciphertext=Encoding.bytes_to_base64(ciphertext),
        )

        storage = LocalStorage()

        with open(storage.vault_path, "w", encoding="utf-8") as file:
            json.dump(
                asdict(encrypted_vault),
                file,
                indent=4,
            )



    def get_entries(self) -> list[Entry]:
        if self._vault is None:
            return []

        return self._vault.entries


    def get_emails(self) -> list[Email]:
        if self._vault is None:
            return []

        return self._vault.emails


    def add_entry(self, entry: Entry):
        if self._vault is None:
            raise ValueError("Vault is locked.")

        self._vault.entries.append(entry)


    def add_email(self, email: Email):
        if self._vault is None:
            raise ValueError("Vault is locked.")

        self._vault.emails.append(email)


    def update_entry(self, entry: Entry):
        if self._vault is None:
            raise ValueError("Vault is locked.")

        for i, e in enumerate(self._vault.entries):
            if e.id == entry.id:
                self._vault.entries[i] = entry
                return

        raise ValueError(f"Entry {entry.id} not found.")

    def delete_entry(self, entry_id: str):
        if self._vault is None:
            raise ValueError("Vault is locked.")

        self._vault.entries = [
            entry
            for entry in self._vault.entries
            if entry.id != entry_id
        ]


    def delete_email(self, email_id: str):
        if self._vault is None:
            raise ValueError("Vault is locked.")

        self._vault.emails = [
            email
            for email in self._vault.emails
            if email.id != email_id
        ]