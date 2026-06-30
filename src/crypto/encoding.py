import base64

class Encoding:
    """
    Utility class for converting between bytes and Base64 strings
    """

    @staticmethod
    def bytes_to_base64(data: bytes) -> str:
    
        return base64.b64encode(data).decode('utf-8')
    

    @staticmethod
    def base64_to_bytes(data: str) -> bytes:

        return base64.b64decode(data.encode("utf-8"))
