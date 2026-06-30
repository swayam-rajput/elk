from dataclasses import dataclass

@dataclass
class Settings:
    """
    User-configurable settings for the password manager.
    """

    clipboard_timeout: int = 30
    auto_lock_minutes: int = 5

