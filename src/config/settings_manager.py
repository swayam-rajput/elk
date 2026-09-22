import json
import os
from pathlib import Path
from dataclasses import asdict
from config.settings import Settings

class SettingsManager:
    def __init__(self, path: str = "vault/settings.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._settings = Settings()

    @property
    def settings(self) -> Settings:
        return self._settings

    def load(self) -> Settings:
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._settings = Settings(**data)
        return self._settings

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(asdict(self._settings), f, indent=4)

    def reset(self) -> None:
        self._settings = Settings()
        self.save()

    def configured(self) -> bool:
        return self.path.exists()
