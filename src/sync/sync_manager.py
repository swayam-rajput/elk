from storage.provider import StorageProvider
from sync.conflicts import (
    ConflictResolver,
    ConflictResolution,
)
from requests.exceptions import ConnectionError, Timeout, RequestException

class SyncManager:

    def __init__(
        self,
        local: StorageProvider,
        remote: StorageProvider,
    ):
        self.local = local
        self.remote = remote

    def sync(self) -> bool:
        """
        Synchronize the local and remote vaults.
        """

        try:

            local = (
                self.local.load()
                if self.local.exists()
                else None
            )

            remote = (
                self.remote.load()
                if self.remote.exists()
                else None
            )

            action = ConflictResolver.resolve(
                local_vault=local,
                remote_vault=remote,
            )

            if action == ConflictResolution.UPLOAD_LOCAL:

                self.remote.save(local)

                print("Uploaded local vault to the remote location.\nChanges synced")

                return True

            if action == ConflictResolution.DOWNLOAD_REMOTE:

                self.local.save(remote)

                print("Downloaded remote vault.")

                return True

            if action == ConflictResolution.NO_ACTION:

                print("Vault already synchronized.")

                return True

            return False

        except ConnectionError:
            print("Unable to connect to GitHub. Check your internet connection.")
            return False

        except Timeout:
            print("Connection to GitHub timed out.")
            return False

        except RequestException:
            print("Unable to synchronize with GitHub.")
            return False

        except Exception as e:
            print(f"Sync failed: {e}")
            return False