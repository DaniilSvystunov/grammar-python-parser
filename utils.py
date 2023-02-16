from urllib.parse import urlparse


def get_domain(url: str) -> str:
    """Obtain domain from the given url.

    Args:
        url (str): provided url
    """
    return urlparse(url).netloc
