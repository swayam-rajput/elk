from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AESManager:
    """
    Handles AES-256-GCM encryption and decryption.
    """

    @staticmethod
    def encrypt(
        plaintext: bytes,
        key: bytes,
        nonce: bytes,
    ) -> bytes:

        aes = AESGCM(key)

        return aes.encrypt(
            nonce,
            plaintext,
            None,
        )

    @staticmethod
    def decrypt(
        ciphertext: bytes,
        key: bytes,
        nonce: bytes,
    ) -> bytes:

        aes = AESGCM(key)

        return aes.decrypt(
            nonce,
            ciphertext,
            None,
        )