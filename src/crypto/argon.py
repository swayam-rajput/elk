from argon2.low_level import Type, hash_secret_raw

from .config import Argon2Config


class Argon2KeyDeriver:
    """
    Derives a 256-bit AES key from the user's master password using Argon2id.
    """

    def __init__(self, config: Argon2Config | None = None):
        self.config = config or Argon2Config()

    def derive_key(self, master_password: str, salt: bytes) -> bytes:
        return hash_secret_raw(
            secret=master_password.encode("utf-8"),
            salt=salt,
            time_cost=self.config.time_cost,
            memory_cost=self.config.memory_cost,
            parallelism=self.config.parallelism,
            hash_len=self.config.hash_length,
            type=Type.ID,
        )