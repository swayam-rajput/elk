from dataclasses import dataclass


@dataclass
class ProfileGitHubSettings:
    enabled: bool = False
    username: str = ""
    repository: str = ""
    token: str = ""