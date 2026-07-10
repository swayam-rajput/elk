import base64
import requests

from models.encrypted_vault import (
    EncryptedVault,
    EncryptionMetadata,
    KDFMetadata,
)


class GitHubStorage:

    FILE_NAME = "encrypted-vault.json"

    def __init__(
        self,
        username: str,
        repository: str,
        token: str,
    ):
        self.username = username
        self.repository = repository
        self.token = token

        self.url = (
            f"https://api.github.com/repos/"
            f"{username}/{repository}/contents/"
            f"{self.FILE_NAME}"
        )

        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }

        