from pathlib import Path
import shutil


class BackupManager:

    @staticmethod
    def export_vault(
        source: Path,
        destination: Path,
    ) -> Path:

        if not source.exists():
            raise FileNotFoundError(
                "Vault not found."
            )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            source,
            destination,
        )

        return destination

    @staticmethod
    def import_vault(
        source: Path,
        destination: Path,
    ) -> Path:

        if not source.exists():
            raise FileNotFoundError(
                "Backup file not found."
            )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            source,
            destination,
        )

        return destination