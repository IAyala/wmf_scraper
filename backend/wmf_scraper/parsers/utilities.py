import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from urllib.request import urlopen

import certifi
from lxml import html

URL_PREFIX = "https://www.watchmefly.net/events"

# WatchMeFly publishes an event under several views: v=pp is the pilot list and
# v=enb the noticeboard. Only v=tt, the Results view, carries the standings table
# and the per-task links this scraper reads, and only v=t, the Flights & Tasks
# view, says which flight a task belongs to and on which day it was flown.
RESULTS_VIEW = "tt"
TASK_DATA_VIEW = "t"

# Verify WatchMeFly's certificate against certifi's CA bundle. Passed explicitly
# per request rather than patching ssl globally.
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def view_url(url: str, view: str) -> str:
    """Point a WatchMeFly event URL at one of its views.

    Applied when parsing rather than only when a competition is added, so a URL
    already stored with the wrong view keeps working.
    """
    parts = urlparse(url)
    query = parse_qs(parts.query)
    if "e" not in query:
        # Not an event URL. Leave it alone rather than guess.
        return url
    query["v"] = [view]
    return urlunparse(parts._replace(query=urlencode(query, doseq=True)))


def results_url(url: str) -> str:
    """The Results view, which lists the scored tasks and their standings."""
    return view_url(url, RESULTS_VIEW)


def task_data_url(url: str) -> str:
    """The Flights & Tasks view, which groups the tasks into dated flights."""
    return view_url(url, TASK_DATA_VIEW)


def _html_from_url(url: str) -> html.HtmlElement:  # pragma: no cover
    with urlopen(url, context=_SSL_CONTEXT) as the_url_reader:
        return html.fromstring(the_url_reader.read())


def html_from_url(url: str) -> html.HtmlElement:
    try:
        return _html_from_url(url)
    except (HTTPError, URLError) as ex:  # pragma: no cover
        raise ValueError(f"Not possible to open URL: {url}") from ex  # pragma: no cover
