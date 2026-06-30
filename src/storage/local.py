from pathlib import Path

class LocalStorage:
    """
    Handles reading and writing the encrypted vault from the local filesystem
    """
    def __init__(self, vault_path:str = "src/vault/encrypted-vault.json"):
        self.vault_path = Path(vault_path)

        # create the dir if it doesn't exist
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
    
    def exists(self) -> bool:
        """
        Checks whether the encrypted vault exists
        """
        return self.vault_path.exists()
    
    def save(self, encrypted_data: bytes) -> None:
        """Saves encrypted bytes to disk"""
        with open(self.vault_path, "wb") as file:
            file.write(encrypted_data)
    
    def load(self) -> bytes:
        """Loads encrypted bytes from disk"""

        with open(self.vault_path, "rb") as file:
            return file.read()

        