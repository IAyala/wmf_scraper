import pytest
from lxml import html
from pytest_mock import MockerFixture

from tests.conftest import (
    ONE_COMPETITION_DUMMY_DATA,
    get_expected_competitor_and_task,
    get_test_files,
    get_xml_tree_from_file,
)
from tests.test_competition import add_user_data_and_assert
from wmf_scraper.models.competition import CompetitionModel
from wmf_scraper.parsers.task import get_tasks_data
from wmf_scraper.parsers.utilities import results_url

TESTS_TO_RUN: str = "**/*.html"
DATA_TESTS_FOLDER: str = "data/competitors_and_tasks"


@pytest.mark.parametrize(
    "user_data_to_add, html_file",
    [(ONE_COMPETITION_DUMMY_DATA, x) for x in get_test_files(DATA_TESTS_FOLDER, TESTS_TO_RUN)],
)
def test_tasks_parser(test_client, user_data_to_add, html_file, mocker: MockerFixture):
    add_user_data_and_assert(user_data_to_add, test_client, [200] * len(user_data_to_add))
    mocker.patch(
        "wmf_scraper.parsers.utilities._html_from_url",
        return_value=get_xml_tree_from_file(html_file),
    )
    response = test_client.get("/api/task/get_tasks_for_competition", params={"competition_id": 1})
    expected = get_expected_competitor_and_task(html_file)
    assert response.status_code == expected.expected_response
    if response.status_code == 200:
        assert len(response.json()) == expected.expected_number_tasks
        assert [x["task_name"] for x in sorted(response.json(), key=lambda x: x["task_order"])] == expected.tasks


def test_tasks_empty_competitions(test_client):
    response = test_client.get("/api/task/get_tasks_for_competition", params={"competition_id": 1})
    assert response.status_code == 400
    assert response.json()["detail"] == "Competition ID: 1 not found"


NON_TASK_ANCHOR_PAGE = """
<html><body>
  <a class="text-black" href="event.php?e=x&v=enb">Go To Noticeboard</a>
  <a class="text-black" href="event.php?v=tr&tid=1">
    <h7 class="mb-0">Task 1 - Pilot Declared Goal</h7>
    <div class="ms-auto"><h7> Final </h7></div>
  </a>
  <a class="text-black" href="event.php?v=tr&tid=2">
    <h7 class="mb-0">Task 2 - Fly On</h7>
  </a>
</body></html>
"""

DUMMY_COMPETITION = CompetitionModel(
    competition_id=1,
    competition_description="dummy",
    competition_url="https://watchmefly.net/events/event.php?e=dummy&v=tt",
)


def test_tasks_parser_skips_anchors_that_are_not_tasks(mocker: MockerFixture):
    """The event page reuses .text-black for links such as "Go To Noticeboard".

    Reading a task title out of one of those used to raise IndexError, which
    surfaced as a bare "list index out of range" when loading a competition.
    """
    mocker.patch(
        "wmf_scraper.parsers.utilities._html_from_url",
        return_value=html.fromstring(NON_TASK_ANCHOR_PAGE),
    )
    tasks = get_tasks_data(DUMMY_COMPETITION)

    assert [(t.task_order, t.task_name) for t in tasks] == [
        (1, "Pilot Declared Goal"),
        (2, "Fly On"),
    ]
    # A task card with no status element must not blow up either.
    assert [t.task_status for t in tasks] == ["Final", ""]


@pytest.mark.parametrize(
    "url, expected",
    [
        # The Task Data view, the typo that broke the 2026 US Nationals.
        (
            "https://watchmefly.net/events/event.php?e=usnationals2026&v=t",
            "https://watchmefly.net/events/event.php?e=usnationals2026&v=tt",
        ),
        # Already correct.
        (
            "https://watchmefly.net/events/event.php?e=france2026&v=tt",
            "https://watchmefly.net/events/event.php?e=france2026&v=tt",
        ),
        # Pilots view, and no view at all.
        (
            "https://watchmefly.net/events/event.php?e=x&v=pp",
            "https://watchmefly.net/events/event.php?e=x&v=tt",
        ),
        (
            "https://watchmefly.net/events/event.php?e=x",
            "https://watchmefly.net/events/event.php?e=x&v=tt",
        ),
        # Not an event URL: left alone rather than guessed at.
        ("https://example.com/nothing", "https://example.com/nothing"),
    ],
)
def test_results_url_points_at_the_results_view(url, expected):
    assert results_url(url) == expected
