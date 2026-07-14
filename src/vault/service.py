from dataclasses import asdict
import json
import hashlib
from cryptography.exceptions import InvalidTag

from models.entry import Entry
from models.email import Email

from datetime import datetime, UTC

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
from storage.provider import StorageProvider
from vault.serializer import VaultSerializer
from sync.sync_manager import SyncManager

class VaultService:

    def __init__(self, storage: StorageProvider, sync_manager: SyncManager | None = None):
        self.storage = storage
        self.sync_manager = sync_manager
        self._vault: Vault | None = None
        self._key: bytes | None = None
        self._salt: bytes | None = None
        self._dirty: bool = False
        self._local_hash: str | None = None
        self._remote_hash: str | None = None
        self._needs_sync: bool = False

    @property
    def dirty(self) -> bool:
        return self._dirty

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
    
    def _calculate_hash(self, plaintext: bytes) -> str:
        return hashlib.sha256(plaintext).hexdigest()

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
            updated_at=datetime.now(UTC).isoformat(),
        )

        self.storage.save(encrypted_vault)
        self._local_hash = self._calculate_hash(plaintext)
        self._needs_sync = True


    def unlock_vault(self, master_password: str):

        encrypted_vault = self.storage.load()

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

        self._local_hash = self._calculate_hash(plaintext)
        self._remote_hash = self._local_hash
        
        self._vault = VaultSerializer.deserialize(
            plaintext
        )
    
    def save(self) -> bool:
        if not self._dirty:
            return False

        if self._vault is None:
            raise ValueError("Vault is locked.")

        if self._key is None:
            raise ValueError("Vault key not found.")

        if self._salt is None:
            raise ValueError("Vault salt not found.")

        plaintext = VaultSerializer.serialize(
            self._vault
        )
        
        current_hash = self._calculate_hash(plaintext)
        if current_hash == self._local_hash:
            self._dirty = False
            return False

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
            updated_at=datetime.now(UTC).isoformat(),
        )

        self.storage.save(encrypted_vault)
        self._local_hash = current_hash
        self._dirty = False
        self._needs_sync = True
        return True
    
    def sync(self) -> bool:
        if not self._needs_sync:
            return False
        if self.sync_manager is None:
            return False

        success = self.sync_manager.sync()
        if success:
            self._remote_hash = self._local_hash
            self._needs_sync = False
        return success
        
    def encrypt_token(self, token: str) -> str:
        if self._key is None:
            raise ValueError("Vault is locked.")
        nonce = RandomGenerator.generate_nonce()
        ciphertext = AESManager.encrypt(token.encode('utf-8'), self._key, nonce)
        return Encoding.bytes_to_base64(nonce) + ":" + Encoding.bytes_to_base64(ciphertext)

    def decrypt_token(self, encrypted_token: str) -> str:
        if self._key is None:
            raise ValueError("Vault is locked.")
        if not encrypted_token:
            return ""
        parts = encrypted_token.split(":")
        if len(parts) != 2:
            raise ValueError("Invalid encrypted token format.")
        nonce = Encoding.base64_to_bytes(parts[0])
        ciphertext = Encoding.base64_to_bytes(parts[1])
        try:
            plaintext = AESManager.decrypt(ciphertext, self._key, nonce)
            return plaintext.decode('utf-8')
        except InvalidTag:
            raise ValueError("Failed to decrypt token.")


    def get_entries(self) -> list[Entry]:
        if self._vault is None:
            return []

        return self._vault.entries

    def get_entry(self, entry_id: str) -> Entry | None:
        if self._vault is None:
            return None

        for entry in self._vault.entries:
            if entry.id == entry_id:
                return entry

        return None


    def get_emails(self) -> list[Email]:
        if self._vault is None:
            return []

        return self._vault.emails

    def get_email(self, email_id: str) -> Email | None:
        if self._vault is None:
            return None

        for email in self._vault.emails:
            if email.id == email_id:
                return email

        return None

    def add_entry(self, entry: Entry):
        if self._vault is None:
            raise ValueError("Vault is locked.")
        for e in self.get_entries():
            if (
                e.site.url == entry.site.url
                and e.email_id == entry.email_id
            ):
                raise ValueError("An entry for this site and email already exists.")
        self._vault.entries.append(entry)
        self._dirty = True


    def add_email(self, email: Email):
        if self._vault is None:
            raise ValueError("Vault is locked.")

        self._vault.emails.append(email)
        self._dirty = True


    def update_entry(self, entry: Entry):
        if self._vault is None:
            raise ValueError("Vault is locked.")

        for i, e in enumerate(self._vault.entries):
            if e.id == entry.id:
                entry.updated_at = datetime.now()
                self._vault.entries[i] = entry
                self._dirty = True
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
        self._dirty = True


    def delete_email(self, email_id: str):
        if self._vault is None:
            raise ValueError("Vault is locked.")

        email_to_delete = None
        for email in self._vault.emails:
            if email.id == email_id:
                email_to_delete = email
                break
        
        if not email_to_delete:
            return

        for entry in self._vault.entries:
            if entry.email_id == email_to_delete.address:
                raise ValueError(
                    "Email is used by one or more entries."
                )

        self._vault.emails = [
            email
            for email in self._vault.emails
            if email.id != email_id
        ]
        self._dirty = True

    def update_email(self, email: Email):
        if self._vault is None:
            raise ValueError("Vault is locked.")

        old_address = None
        for i, e in enumerate(self._vault.emails):
            if e.id == email.id:
                old_address = e.address
                self._vault.emails[i] = email
                break
                
        if old_address is None:
            raise ValueError(f"Email {email.id} not found.")

        if old_address != email.address:
            for entry in self._vault.entries:
                if entry.email_id == old_address:
                    entry.email_id = email.address

        self._dirty = True

    def export_backup(self, destination: str) -> str:
        from pathlib import Path
        from storage.backup import BackupManager
        
        if not isinstance(self.storage, LocalStorage):
            raise ValueError("Export is only supported for local storage")

        BackupManager.export_vault(Path(self.storage.vault_path), Path(destination))
        return destination
    
    def import_vault(self, source: str):
        from pathlib import Path
        from storage.backup import BackupManager

        if not isinstance(self.storage, LocalStorage):
            raise ValueError(
                "Import is only supported for local storage."
            )

        BackupManager.import_vault(
            source=Path(source),
            destination=self.storage.vault_path,
        )

        self.lock()
