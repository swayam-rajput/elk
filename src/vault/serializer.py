import json
from dataclasses import asdict
from datetime import datetime

from models.email import Email
from models.entry import Entry, Site
from models.settings import Settings
from models.vault import Vault

class VaultSerializer:
    """
    Responsible for converting between Vault objects and bytes.
    """

    @staticmethod
    def serialize(vault: Vault) -> bytes:
        """
        Convert a Vault object into UTF-8 encoded JSON bytes.
        """

        vault_dict = asdict(vault)

        vault_json = json.dumps(
            vault_dict,
            indent=4,
            sort_keys=True,
            default=str,
        )

        return vault_json.encode("utf-8")

    @staticmethod
    def deserialize(data: bytes) -> dict:
        """
        Convert UTF-8 encoded JSON bytes back into a dictionary.

        """
        vault_dict = json.loads(
            data.decode('utf-8')
        )

        emails = [
            Email(**email) for email in vault_dict['emails']
        ]

        entries = []

        for entry in vault_dict['entries']:
            site = Site(**entry['site'])

            entries.append(
                Entry(
                    id=entry['id'],
                    site=site,
                    email_id=entry['email_id'],
                    username=entry['username'],
                    password=entry['password'],
                    notes=entry['notes'],
                    favorite=entry['favorite'],
                    created_at=datetime.fromisoformat(
                        entry['created_at']
                    ),
                    updated_at=datetime.fromisoformat(
                        entry['updated_at']
                    ),
                )
            )
        
        settings = Settings(
            **vault_dict['settings']
        )

        return Vault(
            version=vault_dict['version'],
            emails=emails,
            entries=entries,
            settings=settings,
        )
