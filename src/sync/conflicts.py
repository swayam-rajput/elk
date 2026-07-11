from enum import Enum


class ConflictResolution(Enum):
    UPLOAD_LOCAL = "upload_local"
    DOWNLOAD_REMOTE = "download_remote"
    NO_ACTION = "no_action"


class ConflictResolver:

    @staticmethod
    def resolve(local_vault, remote_vault):

        if local_vault is None and remote_vault is None:
            return ConflictResolution.NO_ACTION

        if local_vault is not None and remote_vault is None:
            return ConflictResolution.UPLOAD_LOCAL

        if local_vault is None and remote_vault is not None:
            return ConflictResolution.DOWNLOAD_REMOTE

        if local_vault.updated_at == remote_vault.updated_at:
            return ConflictResolution.NO_ACTION

        if local_vault.updated_at > remote_vault.updated_at:
            return ConflictResolution.UPLOAD_LOCAL

        return ConflictResolution.DOWNLOAD_REMOTE