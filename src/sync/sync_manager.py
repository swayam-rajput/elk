from storage.provider import StorageProvider


class SyncManager:

    def __init__(
        self,
        local: StorageProvider,
        remote: StorageProvider,
    ):
        self.local = local
        self.remote = remote

    def upload(self):
        """
        Upload local vault to GitHub.
        """

        if not self.local.exists():
            raise FileNotFoundError(
                "Local vault not found."
            )

        vault = self.local.load()

        self.remote.save(vault)

    def download(self):
        """
        Download GitHub vault to local storage.
        """

        if not self.remote.exists():
            raise FileNotFoundError(
                "Remote vault not found."
            )

        vault = self.remote.load()

        self.local.save(vault)

    def sync(self):
        """
        Basic synchronization.
        """

        local_exists = self.local.exists()
        remote_exists = self.remote.exists()

        if local_exists and not remote_exists:

            self.upload()
            return

        if remote_exists and not local_exists:

            self.download()
            return

        if local_exists and remote_exists:

            self.upload()
            return

        raise FileNotFoundError(
            "No vault found."
        )