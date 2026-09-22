import json
import shutil
from pathlib import Path

from profiles.model import Profile


# Legacy vault written before profiles existed
_LEGACY_VAULT = Path("vault/encrypted-vault.json")


class ProfileManager:
    def __init__(self, profiles_file: str = "data/profiles.json"):
        self.profiles_file = Path(profiles_file)
        self.profiles_dir = self.profiles_file.parent / "profiles"

        self.profiles: list[Profile] = []
        self.active_profile_id: str | None = None
        self.default_profile_id: str | None = None

        self._load()

    # ── Persistence ────────────────────────────────────────────────────────

    def _load(self):
        if not self.profiles_file.exists():
            self._create_default()
            return

        with self.profiles_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        self.active_profile_id = data.get("active_profile")
        self.default_profile_id = data.get("default_profile")

        self.profiles = []
        for p in data.get("profiles", []):
            profile_dir = self.profiles_dir / p["id"]
            # Backfill settings_path for profiles.json written before this field existed
            settings_path = p.get(
                "settings_path",
                str(profile_dir / "settings.json"),
            )
            self.profiles.append(
                Profile(
                    id=p["id"],
                    name=p["name"],
                    vault_path=p["vault_path"],
                    settings_path=settings_path,
                    is_default=p.get("is_default", False),
                )
            )

        # First time reading an older profiles.json that has no default set:
        # auto-assign and resave so it's persisted going forward.
        if not self.default_profile_id and self.profiles:
            self.default_profile_id = self.profiles[0].id
            self.profiles[0].is_default = True
            self._save()

    def _create_default(self):
        """Called on very first launch: build the Personal profile and
        migrate the legacy vault if it exists."""
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

        profile_dir = self.profiles_dir / "personal"
        profile_dir.mkdir(parents=True, exist_ok=True)

        vault_path = profile_dir / "vault.enc"
        settings_path = profile_dir / "settings.json"

        # Req 5: migrate legacy vault unchanged
        if _LEGACY_VAULT.exists() and not vault_path.exists():
            shutil.copy2(_LEGACY_VAULT, vault_path)

        profile = Profile(
            id="personal",
            name="Personal",
            vault_path=str(vault_path),
            settings_path=str(settings_path),
            is_default=True,
        )

        self.profiles = [profile]
        self.active_profile_id = profile.id
        self.default_profile_id = profile.id

        self._save()

    def _save(self):
        self.profiles_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "active_profile": self.active_profile_id,
            "default_profile": self.default_profile_id,
            "profiles": [
                {
                    "id": p.id,
                    "name": p.name,
                    "vault_path": p.vault_path,
                    "settings_path": p.settings_path,
                    "is_default": p.is_default,
                }
                for p in self.profiles
            ],
        }

        with self.profiles_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ── Queries ────────────────────────────────────────────────────────────

    def list_profiles(self) -> list[Profile]:
        return self.profiles

    def get_profile(self, profile_id: str) -> Profile | None:
        for p in self.profiles:
            if p.id == profile_id:
                return p
        return None

    def get_active_profile(self) -> Profile | None:
        if self.active_profile_id is None:
            return None
        return self.get_profile(self.active_profile_id)

    def get_default_profile(self) -> Profile | None:
        if self.default_profile_id is None:
            return None
        return self.get_profile(self.default_profile_id)

    # ── Mutations ──────────────────────────────────────────────────────────

    def set_active_profile(self, profile_id: str):
        if self.get_profile(profile_id) is None:
            raise ValueError(f"Profile '{profile_id}' not found.")
        self.active_profile_id = profile_id
        self._save()

    def set_default_profile(self, profile_id: str):
        """Mark *profile_id* as the default and clear the flag on all others."""
        profile = self.get_profile(profile_id)
        if profile is None:
            raise ValueError(f"Profile '{profile_id}' not found.")
        for p in self.profiles:
            p.is_default = False
        profile.is_default = True
        self.default_profile_id = profile_id
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
            settings_path=str(profile_dir / "settings.json"),
            is_default=False,
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

        self.profiles = [p for p in self.profiles if p.id != profile_id]

        if self.active_profile_id == profile_id:
            self.active_profile_id = self.profiles[0].id

        if self.default_profile_id == profile_id:
            self.default_profile_id = self.profiles[0].id
            self.profiles[0].is_default = True

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