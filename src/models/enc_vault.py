from dataclasses import dataclass
from enum import Enum

class KDFAlgorithm(Enum):
    ARGON2ID = "argon2id"

class EncryptionAlgorithm(Enum):
    AES_256_GCM = "aes-256-gcm"


@dataclass
class KDFMetadata:
    algorithm: KDFAlgorithm

    memory: int

    iterations: int

    parallelism: int

    salt: str


@dataclass
class EncryptionMetadata:
    algorithm: EncryptionAlgorithm

    nonce: str


@dataclass
class EncryptedVault:
    version: int

    kdf: KDFMetadata

    encryption: EncryptionMetadata

    ciphertext: str

    updated_at: str