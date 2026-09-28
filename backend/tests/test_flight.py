"""The flights view, and how it joins to the tasks of the Results view.

Both fixtures are the real 2026 US Nationals, saved because that event has
every awkward case in it at once: a cancelled flight whose task numbers were
reused by the flight that replaced it, a task with no published results, and a
practice flight that the Results view lists separately.
"""

from datetime import date

import pytest
from pytest_mock import MockerFixture

from tests.conftest import get_xml_tree_from_file, resolve_path
from wmf_scraper.models.competition import CompetitionModel
from wmf_scraper.parsers.flight import Flight, flight_from_header, get_flights_data
from wmf_scraper.parsers.task import get_tasks_data
from wmf_scraper.parsers.utilities import task_data_url

FLIGHTS_PAGE = resolve_path("data/flights/html_examples/USNationals_2026_flights.html")
RESULTS_PAGE = resolve_path("data/flights/html_examples/USNationals_2026_results.html")

US_NATIONALS = CompetitionModel(
    competition_id=1,
    competition_description="2026 BFA/HACD US Nationals Championship",
    competition_url="https://www.watchmefly.net/events/event.php?e=usnationals2026&v=tt",
)

# Task 17 is missing on purpose: it was set but never scored, so the Results
# view does not link it and it never reaches the database.
EXPECTED_FLIGHT_OF_TASK = {
    1: 1, 2: 1, 3: 1, 4: 1,
    5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 2, 11: 2,
    12: 3, 13: 3, 14: 3, 15: 3, 16: 3,
    18: 4, 19: 4, 20: 4,
}  # fmt: skip


def page_for(url: str):
    """Serve the flights view or the Results view, as the real site would."""
    return get_xml_tree_from_file(FLIGHTS_PAGE if url.endswith("v=t") else RESULTS_PAGE)


@pytest.mark.parametrize(
    "header, expected",
    [
        ("Flight 4 - 15 Aug 2026 AM", Flight(4, date(2026, 8, 15), "AM")),
        ("Flight 11 - 13 Sep 2023 PM", Flight(11, date(2023, 9, 13), "PM")),
        # Spelled-out month, and a flight with no date published yet.
        ("Flight 2 - 1 September 2024 AM", Flight(2, date(2024, 9, 1), "AM")),
        ("Flight 7 -", Flight(7, None, "")),
        # Shaped like a date but not one: the flight still counts.
        ("Flight 5 - 15 Foobar 2026 PM", Flight(5, None, "PM")),
        # Not a flight header at all.
        ("Competition Tasks", None),
        ("Flight Schedule", None),
        # Practice flights are numbered from 1 of their own, so a competition
        # has both a "Flight 1" and a "Practice Flight 1". Only the first is a
        # flight of the competition, hence the anchored pattern.
        ("Practice Flight 1 - 9 Aug 2026 AM", None),
    ],
)
def test_flight_header_parsing(header, expected):
    assert flight_from_header(header) == expected


def test_flights_view_is_read_by_task_url(mocker: MockerFixture):
    """Keyed by URL because task numbers are not unique.

    The cancelled flight of 12 Aug set tasks 12 to 15, and the flight that
    replaced it on 14 Aug set tasks 12 to 16 all over again.
    """
    mocker.patch("wmf_scraper.parsers.utilities._html_from_url", side_effect=page_for)
    flights = get_flights_data(US_NATIONALS)

    # The competition tasks, and only those: the three practice tasks sit under
    # a "Practice Flight 1" card that is deliberately not read as a flight.
    assert len(flights) == len(EXPECTED_FLIGHT_OF_TASK)
    assert all(url.startswith("https://www.watchmefly.net/events/") for url in flights)
    assert {flight.flight_number for flight in flights.values()} == {1, 2, 3, 4}
    # The cancelled flight has no scored task, so none of its tasks are listed.
    assert date(2026, 8, 12) not in {flight.flight_date for flight in flights.values()}


def test_every_scraped_task_carries_its_flight(mocker: MockerFixture):
    mocker.patch("wmf_scraper.parsers.utilities._html_from_url", side_effect=page_for)
    tasks = get_tasks_data(US_NATIONALS)

    assert {task.task_order: task.flight_number for task in tasks} == EXPECTED_FLIGHT_OF_TASK
    flight_four = [task for task in tasks if task.flight_number == 4]
    assert all(task.flight_date == date(2026, 8, 15) for task in flight_four)
    assert all(task.flight_period == "AM" for task in flight_four)


def test_tasks_still_load_when_there_is_no_flights_view(mocker: MockerFixture):
    """A competition must load even if WatchMeFly publishes no flights."""

    def only_the_results_view(url: str):
        if url.endswith("v=t"):
            raise ValueError(f"Not possible to open URL: {url}")
        return get_xml_tree_from_file(RESULTS_PAGE)

    mocker.patch("wmf_scraper.parsers.utilities._html_from_url", side_effect=only_the_results_view)
    tasks = get_tasks_data(US_NATIONALS)

    assert len(tasks) == len(EXPECTED_FLIGHT_OF_TASK)
    assert all(task.flight_number is None for task in tasks)


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "https://watchmefly.net/events/event.php?e=usnationals2026&v=tt",
            "https://watchmefly.net/events/event.php?e=usnationals2026&v=t",
        ),
        ("https://example.com/nothing", "https://example.com/nothing"),
    ],
)
def test_task_data_url_points_at_the_flights_view(url, expected):
    assert task_data_url(url) == expected
