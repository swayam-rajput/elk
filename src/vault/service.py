from dataclasses import asdict
import json
from cryptography.exceptions import InvalidTag

from models.vault import Vault
from models.enc_vault import (
    EncryptedVault,
    KDFMetadata,
    EncryptionMetadata
)

from crypto.random import RandomGenerator
from crypto.config import Argon2Config
from crypto.argon import Argon2KeyDeriver
from crypto.aes import AESManager
from crypto.encoding import Encoding

from storage.local import LocalStorage
from vault.serializer import VaultSerializer

class VaultService:
    def __init__(self):
        self._vault = None
        self._key = None
        self._salt = None
        # self._nonce = None

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
        
    def create_vault(
        self,
        master_password:str
    ):
        self._vault = Vault()

        self._salt = RandomGenerator.generate_salt()

        nonce = RandomGenerator.generate_nonce()

        self._key = Argon2KeyDeriver().derive_key(
            master_password=master_password,
            salt=self._salt
        )

        plaintext = VaultSerializer.serialize(self._vault)

        ciphertext = AESManager.encrypt(
            plaintext,
            self._key,
            nonce
        )

        enc_vault = EncryptedVault(
            version=1,
            kdf=KDFMetadata(
                algorithm='argon2id',
                memory=Argon2Config.memory_cost,
                iterations=Argon2Config.time_cost,
                parallelism=Argon2Config.parallelism,
                salt=Encoding.bytes_to_base64(self._salt)
            ),
            encryption=EncryptionMetadata(
                algorithm='aes-256-gcm',
                nonce=Encoding.bytes_to_base64(nonce),
            ),
            ciphertext=Encoding.bytes_to_base64(ciphertext)
        )

        storage = LocalStorage()

        with open(storage.vault_path, 'w', encoding='utf-8') as file:
            json.dump(
                asdict(enc_vault),
                file,
                indent=4
            )
    
    def unlock_vault(
        self,
        master_password: str,
    ) -> dict:
        storage = LocalStorage()

        with open(storage.vault_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        encrypted_vault = EncryptedVault(
            version=data['version'],
            kdf=KDFMetadata(**data['kdf']),
            encryption=EncryptionMetadata(**data['encryption']),
            ciphertext=data['ciphertext']
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
            self._salt
        )

        try:
            plaintext = AESManager.decrypt(
                ciphertext,
                self._key,
                nonce
            )
        except InvalidTag:
            self.lock()
            raise ValueError("Invalid Master Password")

        self._vault = VaultSerializer.deserialize(
            plaintext
        )

        
    
    


    def add_entry(self, entry):
        self._vault.entries.append(entry)

    def get_entries(self):
        return self._vault.entries
    
    def get_entry(self, entry_id: str):
        for entry in self._vault.entries:
            if entry.id == entry_id:
                return entry
        return None
    
    def update_entry(self, updated_entry):
        for i, entry in enumerate(self._vault.entries):
            if entry.id == updated_entry.id:
                self._vault.entries[i] = updated_entry
                self.save()
                return 
        raise ValueError("Entry not found.")
    
    def delete_entry(self, entry_id: str):
        for i, entry in enumerate(self._vault.entries):
            if entry.id == entry_id:
                del self._vault.entries[i] 
                self.save()
                return 
        raise ValueError("Entry not found.")





    def add_email(self, email):
        self._vault.emails.append(email)

    def get_emails(self):
        return self._vault.emails

    def delete_email(self, email_id: str):
        for entry in self._vault.entries:
            if entry.email_id == email_id:
                raise ValueError("Email is used by one or more entries.")
            
        for i, email in enumerate(self._vault.emails):
            if email.id == email_id:
                del self._vault.emails[i]
                self.save()
                return

        raise ValueError("Email not found.")
    
    









    def save(self):
        if self._vault is None:
            raise ValueError("Vault is locked")
        
        if self._key is None:
            raise ValueError("Vault key not found")
        
        if self._salt is None:
            raise ValueError("Vault salt not found")
        
        plaintext = VaultSerializer.serialize(
            self._vault
        )

        nonce = RandomGenerator.generate_nonce()

        ciphertext = AESManager.encrypt(
            plaintext,
            self._key,
            nonce
        )

        encrypted_vault = EncryptedVault(
            version=1,
            kdf=KDFMetadata(
                algorithm="argon2id",
                memory=Argon2Config.memory_cost,
                iterations=Argon2Config.time_cost,
                parallelism=Argon2Config.parallelism,
                salt=Encoding.bytes_to_base64(self._salt),
            ),
            encryption=EncryptionMetadata(
                algorithm="aes-256-gcm",
                nonce=Encoding.bytes_to_base64(nonce),
            ),
            ciphertext=Encoding.bytes_to_base64(ciphertext),
        )

        storage = LocalStorage()
        with open(storage.vault_path, 'w', encoding='utf-8') as file:
            json.dump(
                asdict(encrypted_vault),
                file,
                indent=4
            )
        