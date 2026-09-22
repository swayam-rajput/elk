from dataclasses import dataclass

@dataclass
class Settings:
    github_enabled: bool = False
    github_username: str = ""
    github_repository: str = ""
    github_token: str = ""
    auto_sync: bool = True
    clipboard_timeout: int = 30
