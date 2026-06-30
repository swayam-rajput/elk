from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Site:
    name: str
    url: str


@dataclass
class Entry:
    id: str

    site: Site

    email_id: str

    username: Optional[str]

    password: str

    notes: str

    favorite: bool = False

    created_at: datetime = field(default_factory=datetime.now)

    updated_at: datetime = field(default_factory=datetime.now)