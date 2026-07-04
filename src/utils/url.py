from urllib.parse import urlparse


class URL:

    @staticmethod
    def normalize(url: str) -> str:

        if "://" not in url:
            url = "https://" + url

        parsed = urlparse(url)

        host = parsed.netloc.lower()

        if host.startswith("www."):
            host = host[4:]

        return host