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

from vault.serializer import VaultSerializer

class VaultService:
    def create_vault(
        self,
        master_password:str
    ) -> EncryptedVault:
        vault = Vault()

        salt = RandomGenerator.generate_salt()

        nonce = RandomGenerator.generate_nonce()

        key = Argon2KeyDeriver.derive_key(
            master_password,
            salt
        )

        plaintext = VaultSerializer.serialize(vault)

        ciphertext = AESManager.encrypt(
            plaintext,
            key,
            nonce
        )

        return EncryptedVault(
            version=1,
            kdf=KDFMetadata(
                algorithm='argon2id',
                memory=Argon2Config.memory_cost,
                iterations=Argon2Config.time_cost,
                parallelism=Argon2Config.parallelism,
                salt=Encoding.bytes_to_base64(salt)
            ),
            encryption=EncryptionMetadata(
                algorithm='aes-256-gcm',
                nonce=Encoding.bytes_to_base64(nonce),
            ),
            ciphertext=Encoding.bytes_to_base64(ciphertext)
        )
    
    def unlock_vault(
        self,
        encrypted_vault: EncryptedVault,
        master_password: str,
    ) -> dict:
        salt = Encoding.base64_to_bytes(
            encrypted_vault.kdf.salt
        )

        nonce = Encoding.base64_to_bytes(
            encrypted_vault.encryption.nonce
        )

        ciphertext = Encoding.base64_to_bytes(
            encrypted_vault.ciphertext
        )

        key = Argon2KeyDeriver.derive_key(
            master_password,
            salt,
        )

        plaintext = AESManager.decrypt(
            ciphertext,
            key,
            nonce,
        )

        return VaultSerializer.deserialize(
            plaintext
        )
