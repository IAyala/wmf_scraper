"""Parsing of WatchMeFly's "Flights & Tasks" view.

The Results view lists the tasks and their scores but says nothing about when
they were flown. The task data view groups those same tasks into dated flights,
which is what a pilot actually remembers a competition by: "the morning of the
14th", not "tasks 12 to 16".
"""

import re
from datetime import date, datetime
from typing import NamedTuple

from loguru import logger
from lxml.html import HtmlElement

from wmf_scraper.models.competition import CompetitionModel
from wmf_scraper.parsers.utilities import URL_PREFIX, html_from_url, task_data_url

# "Flight 4 - 15 Aug 2026 AM"
FLIGHT_HEADER = re.compile(r"^Flight\s+(\d+)\s*-\s*(.*)$", re.IGNORECASE)
FLIGHT_DATE = re.compile(r"\d{1,2}\s+[A-Za-z]+\s+\d{4}")
FLIGHT_PERIOD = re.compile(r"\b(AM|PM)\b", re.IGNORECASE)
DATE_FORMATS = ("%d %b %Y", "%d %B %Y")

# Task result pages, as opposed to the flight's task data sheet (v=tds).
TASK_RESULTS_VIEW = "v=tr"


class Flight(NamedTuple):
    flight_number: int
    flight_date: date | None
    flight_period: str


def parse_flight_date(text: str) -> date | None:
    found = FLIGHT_DATE.search(text)
    if not found:
        return None
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(found.group(), date_format).date()
        except ValueError:
            continue
    logger.warning(f"Unrecognised flight date: {found.group()!r}")
    return None


def parse_flight_period(text: str) -> str:
    """AM or PM. A competition can fly twice in one day, so the date alone
    does not identify a flight."""
    found = FLIGHT_PERIOD.search(text)
    return found.group().upper() if found else ""


def flight_from_header(text: str) -> Flight | None:
    header = FLIGHT_HEADER.match(" ".join(text.split()))
    if not header:
        return None
    number, remainder = header.groups()
    return Flight(
        flight_number=int(number),
        flight_date=parse_flight_date(remainder),
        flight_period=parse_flight_period(remainder),
    )


def flight_cards(page: HtmlElement):
    """Every card on the page that is headed by a flight, with its flight."""
    for card in page.find_class("card"):
        for header in card.findall(".//h6"):
            flight = flight_from_header(header.text_content())
            if flight is not None:
                yield card, flight
                break


def get_flights_data(the_competition: CompetitionModel) -> dict[str, Flight]:
    """Map each task's results URL to the flight it was flown in.

    Keyed by URL and not by task number on purpose: when a flight is cancelled
    WatchMeFly reuses its task numbers for the flight that replaces it, so the
    2026 US Nationals publish two different "Task 12". The URL is the same one
    the Results view links to, so the two views join exactly.

    Returns an empty mapping rather than raising when the view is unavailable:
    the flight is extra information, and losing it must not fail a load.
    """
    try:
        page = html_from_url(task_data_url(the_competition.competition_url))
    except ValueError:
        logger.warning(f"Competition {the_competition.competition_id} publishes no flights view; skipping flights")
        return {}

    flights: dict[str, Flight] = {}
    for card, flight in flight_cards(page):
        for anchor in card.findall(".//a"):
            task_url = anchor.get("href")
            if task_url and TASK_RESULTS_VIEW in task_url:
                flights.setdefault(f"{URL_PREFIX}/{task_url}", flight)
    if not flights:
        logger.warning(f"Competition {the_competition.competition_id}: flights view lists no tasks")
    return flights
