from dataclasses import dataclass, field
from typing import List

from .email import Email
from .entry import Entry
from .settings import Settings

@dataclass
class Vault:
    """
    Represents the decrypted vault.
    """

    version: int = 1

    emails: List[Email] = field(default_factory=list)

    entries: List[Entry] = field(default_factory=list)

    settings: Settings = field(default_factory=Settings)