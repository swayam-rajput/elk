from dataclasses import dataclass


@dataclass
class Profile:
    id: str
    name: str
    vault_path: str