import ssl
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import certifi
from lxml import html

URL_PREFIX = "https://www.watchmefly.net/events"

# Verify WatchMeFly's certificate against certifi's CA bundle. Passed explicitly
# per request rather than patching ssl globally.
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def _html_from_url(url: str) -> html.HtmlElement:  # pragma: no cover
    with urlopen(url, context=_SSL_CONTEXT) as the_url_reader:
        return html.fromstring(the_url_reader.read())


def html_from_url(url: str) -> html.HtmlElement:
    try:
        return _html_from_url(url)
    except (HTTPError, URLError) as ex:  # pragma: no cover
        raise ValueError(f"Not possible to open URL: {url}") from ex  # pragma: no cover
