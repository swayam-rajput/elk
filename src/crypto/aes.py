import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class AESManager:
    """
    Handles AES-256-GCM encryption and decryption
    """
    @staticmethod
    def encrypt(data: dict, key:bytes, nonce:bytes) -> bytes:
        plaintxt = json.dumps(
            data,
            separators=(",",":"),
            sort_keys=True
        ).encode('utf-8')

        aes=AESGCM(key)

        ciphertxt = aes.encrypt(
            nonce,
            plaintxt,
            None
        )
        return ciphertxt


    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes, nonce: bytes) -> dict:

        aes = AESGCM(key)
        print(ciphertext, '='*20)
        plaintxt = aes.decrypt(
            nonce,
            ciphertext,
            None
        )

        return json.loads(
            plaintxt.decode('utf-8')
        )
    