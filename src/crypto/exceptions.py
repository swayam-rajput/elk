class VaultError(Exception):
    pass


class InvalidMasterPassword(VaultError):
    pass


class CorruptedVault(VaultError):
    pass


class UnsupportedVaultVersion(VaultError):
    pass