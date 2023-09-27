from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from lxml import html

URL_PREFIX = "https://www.watchmefly.net/events"


def _html_from_url(url: str) -> html.HtmlElement:  # pragma: no cover
    with urlopen(url) as the_url_reader:
        return html.fromstring(the_url_reader.read())


def html_from_url(url: str) -> html.HtmlElement:
    try:
        return _html_from_url(url)
    except (HTTPError, URLError) as ex:  # pragma: no cover
        raise ValueError(f"Not possible to open URL: {url}") from ex  # pragma: no cover
