import json
from dataclasses import asdict

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

        (We'll reconstruct a Vault object in a later step.)
        """

        return json.loads(data.decode("utf-8"))