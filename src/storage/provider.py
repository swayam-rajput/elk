from abc import ABC, abstractmethod

from models.enc_vault import EncryptedVault


class StorageProvider(ABC):
    """
    Abstract base class for all storage providers.
    """

    @abstractmethod
    def exists(self) -> bool:
        """
        Returns True if the vault exists.
        """
        raise NotImplementedError

    @abstractmethod
    def load(self) -> EncryptedVault:
        """
        Loads and returns the encrypted vault.
        """
        raise NotImplementedError

    @abstractmethod
    def save(self, vault: EncryptedVault) -> None:
        """
        Saves the encrypted vault.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self) -> None:
        """
        Deletes the encrypted vault.
        """
        raise NotImplementedError
