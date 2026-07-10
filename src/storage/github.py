import base64
import json
import requests
from dataclasses import asdict

from models.enc_vault import (
    EncryptedVault,
    EncryptionMetadata,
    KDFMetadata,
)
from storage.provider import StorageProvider


class GitHubStorage(StorageProvider):

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

    def exists(self) -> bool:

        response = requests.get(
            self.url,
            headers=self.headers,
        )

        return response.status_code == 200

    def load(self) -> EncryptedVault:

        response = requests.get(
            self.url,
            headers=self.headers,
        )

        response.raise_for_status()

        content = response.json()["content"]

        decoded = base64.b64decode(
            content
        ).decode("utf-8")

        data = json.loads(decoded)

        return EncryptedVault(
            version=data["version"],
            kdf=KDFMetadata(**data["kdf"]),
            encryption=EncryptionMetadata(
                **data["encryption"]
            ),
            ciphertext=data["ciphertext"],
        )

    def save(self, vault: EncryptedVault):

        content = json.dumps(
            asdict(vault),
            indent=4,
        )

        encoded = base64.b64encode(
            content.encode("utf-8")
        ).decode("utf-8")

        sha = None

        if self.exists():

            response = requests.get(
                self.url,
                headers=self.headers,
            )

            sha = response.json()["sha"]

        payload = {
            "message": "Update encrypted vault",
            "content": encoded,
        }

        if sha:
            payload["sha"] = sha

        response = requests.put(
            self.url,
            headers=self.headers,
            json=payload,
        )

        response.raise_for_status()

    def delete(self):

        raise NotImplementedError(
            "Delete not implemented."
        )