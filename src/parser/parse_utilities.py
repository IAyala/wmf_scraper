from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from lxml import html


def html_from_url(url: str):  # pragma: no cover
    try:
        with urlopen(url) as the_url_reader:
            return html.fromstring(the_url_reader.read())
    except (HTTPError, URLError) as ex:
        raise ValueError(f"Not possible to open URL: {url}") from ex
