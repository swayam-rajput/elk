import secrets
import uuid

import secrets
import uuid


class RandomGenerator:
    """
    Responsible for generating cryptographically secure random values.
    """
    @staticmethod
    def generate_salt(length: int = 16) -> bytes:
        """
        Generates a random salt for Argon2id.
        """
        return secrets.token_bytes(length)

    @staticmethod
    def generate_nonce(length: int = 12) -> bytes:
        """
        Generates a random nonce for AES-256-GCM.
        """
        return secrets.token_bytes(length)

    @staticmethod
    def generate_uuid() -> str:
        """
        Generates a unique ID.
        """
        return str(uuid.uuid4())