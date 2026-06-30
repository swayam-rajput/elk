from dataclasses import dataclass


@dataclass
class Email:
    id: str
    address: str
    label: str

