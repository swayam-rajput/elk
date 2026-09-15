import json
from pathlib import Path

from profiles.model import Profile


class ProfileManager:
    def __init__(self, profiles_file: str = "data/profiles.json"):
        self.profiles_file = Path(profiles_file)
        self.profiles_dir = self.profiles_file.parent / "profiles"

        self.profiles: list[Profile] = []
        self.active_profile_id: str | None = None

        self._load()

    def _load(self):
        if not self.profiles_file.exists():
            self._create_default()

            return

        with self.profiles_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        self.active_profile_id = data.get("active_profile")

        self.profiles = [
            Profile(
                id=profile["id"],
                name=profile["name"],
                vault_path=profile["vault_path"],
            )
            for profile in data.get("profiles", [])
        ]

    def _create_default(self):
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

        profile = Profile(
            id="personal",
            name="Personal",
            vault_path="data/profiles/personal/vault.enc",
        )

        self.profiles = [profile]
        self.active_profile_id = profile.id

        self._save()

    def _save(self):
        self.profiles_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "active_profile": self.active_profile_id,
            "profiles": [
                {
                    "id": profile.id,
                    "name": profile.name,
                    "vault_path": profile.vault_path,
                }
                for profile in self.profiles
            ],
        }

        with self.profiles_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def list_profiles(self) -> list[Profile]:
        return self.profiles

    def get_active_profile(self) -> Profile | None:
        if self.active_profile_id is None:
            return None

        for profile in self.profiles:
            if profile.id == self.active_profile_id:
                return profile

        return None

    def get_profile(self, profile_id: str) -> Profile | None:
        for profile in self.profiles:
            if profile.id == profile_id:
                return profile

        return None

    def set_active_profile(self, profile_id: str):
        profile = self.get_profile(profile_id)

        if profile is None:
            raise ValueError(f"Profile '{profile_id}' not found.")

        self.active_profile_id = profile_id
        self._save()

    def create_profile(self, name: str) -> Profile:
        name = name.strip()

        if not name:
            raise ValueError("Profile name cannot be empty.")

        profile_id = name.lower().replace(" ", "-")

        if self.get_profile(profile_id):
            raise ValueError("A profile with this name already exists.")

        profile_dir = self.profiles_dir / profile_id
        profile_dir.mkdir(parents=True, exist_ok=True)

        profile = Profile(
            id=profile_id,
            name=name,
            vault_path=str(profile_dir / "vault.enc"),
        )

        self.profiles.append(profile)
        self._save()

        return profile

    def delete_profile(self, profile_id: str):
        if len(self.profiles) == 1:
            raise ValueError("Cannot delete the only profile.")

        profile = self.get_profile(profile_id)

        if profile is None:
            raise ValueError(f"Profile '{profile_id}' not found.")

        self.profiles = [
            p for p in self.profiles
            if p.id != profile_id
        ]

        if self.active_profile_id == profile_id:
            self.active_profile_id = self.profiles[0].id

        self._save()

    def rename_profile(self, profile_id: str, new_name: str):
        profile = self.get_profile(profile_id)

        if profile is None:
            raise ValueError(f"Profile '{profile_id}' not found.")

        new_name = new_name.strip()

        if not new_name:
            raise ValueError("Profile name cannot be empty.")

        profile.name = new_name
        self._save()