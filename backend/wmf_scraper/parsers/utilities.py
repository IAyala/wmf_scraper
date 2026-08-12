import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from urllib.request import urlopen

import certifi
from lxml import html

URL_PREFIX = "https://www.watchmefly.net/events"

# WatchMeFly publishes an event under several views: v=t is the task data,
# v=pp the pilot list, v=enb the noticeboard. Only v=tt, the Results view,
# carries the standings table and the per-task links this scraper reads.
RESULTS_VIEW = "tt"

# Verify WatchMeFly's certificate against certifi's CA bundle. Passed explicitly
# per request rather than patching ssl globally.
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def results_url(url: str) -> str:
    """Point a WatchMeFly event URL at its Results view.

    Applied when parsing rather than only when a competition is added, so a URL
    already stored with the wrong view keeps working.
    """
    parts = urlparse(url)
    query = parse_qs(parts.query)
    if "e" not in query:
        # Not an event URL. Leave it alone rather than guess.
        return url
    query["v"] = [RESULTS_VIEW]
    return urlunparse(parts._replace(query=urlencode(query, doseq=True)))


def _html_from_url(url: str) -> html.HtmlElement:  # pragma: no cover
    with urlopen(url, context=_SSL_CONTEXT) as the_url_reader:
        return html.fromstring(the_url_reader.read())


def html_from_url(url: str) -> html.HtmlElement:
    try:
        return _html_from_url(url)
    except (HTTPError, URLError) as ex:  # pragma: no cover
        raise ValueError(f"Not possible to open URL: {url}") from ex  # pragma: no cover
