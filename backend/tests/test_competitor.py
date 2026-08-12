import pytest
from pytest_mock import MockerFixture

from tests.conftest import (
    API,
    ONE_COMPETITION_DUMMY_DATA,
    get_expected_competitor_and_task,
    get_test_files,
    get_xml_tree_from_file,
)
from tests.test_competition import add_user_data_and_assert
from wmf_scraper.actions.competitor import preprocess_competitors
from wmf_scraper.database import get_test_db
from wmf_scraper.models.competitor import CompetitorModel
from wmf_scraper.models.task import TaskModel
from wmf_scraper.models.task_result import TaskResultModel

TESTS_TO_RUN: str = "**/*.html"
DATA_TESTS_FOLDER: str = "data/competitors_and_tasks"

HTML_FILES = get_test_files(DATA_TESTS_FOLDER, TESTS_TO_RUN)


@pytest.mark.parametrize(
    "user_data_to_add, html_file",
    [(ONE_COMPETITION_DUMMY_DATA, x) for x in HTML_FILES],
)
def test_competitor_parser(test_client, user_data_to_add, html_file, mocker: MockerFixture):
    add_user_data_and_assert(user_data_to_add, test_client, [200] * len(user_data_to_add))
    mocker.patch(
        "wmf_scraper.parsers.utilities._html_from_url",
        return_value=get_xml_tree_from_file(html_file),
    )
    response = test_client.get(
        f"{API}/competitor/get_competitors_in_competition",
        params={"competition_id": 1},
    )
    expected = get_expected_competitor_and_task(html_file)
    assert response.status_code == expected.expected_response
    if response.status_code == 200:
        assert len(response.json()) == expected.expected_number_competitors


def test_competitor_empty_competitions(test_client):
    response = test_client.get(
        f"{API}/competitor/get_competitors_in_competition",
        params={"competition_id": 1},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Competition ID: 1 not found"


@pytest.mark.parametrize(
    "user_data_to_add, html_file",
    [(ONE_COMPETITION_DUMMY_DATA, x) for x in HTML_FILES],
)
def test_add_competitors(
    test_client,
    user_data_to_add,
    html_file,
    mocker: MockerFixture,
    caplog,
):
    add_user_data_and_assert(user_data_to_add, test_client, [200] * len(user_data_to_add))
    mocker.patch(
        "wmf_scraper.parsers.utilities._html_from_url",
        return_value=get_xml_tree_from_file(html_file),
    )
    response = test_client.post(
        f"{API}/competitor/add_competitors_in_competition",
        params={"competition_id": 1},
    )
    if response.status_code == 200:
        assert "Competitor 1 added" in caplog.text


@pytest.mark.parametrize(
    "user_data_to_add, html_file",
    [(ONE_COMPETITION_DUMMY_DATA, x) for x in get_test_files(DATA_TESTS_FOLDER, "**/DutchBalloonTrophy_2023.html")],
)
def test_add_competitors_already_added(
    test_client,
    user_data_to_add,
    html_file,
    mocker: MockerFixture,
):
    add_user_data_and_assert(user_data_to_add, test_client, [200] * len(user_data_to_add))
    mocker.patch(
        "wmf_scraper.parsers.utilities._html_from_url",
        return_value=get_xml_tree_from_file(html_file),
    )
    for _ in range(2):
        response = test_client.post(
            f"{API}/competitor/add_competitors_in_competition",
            params={"competition_id": 1},
        )
    assert response.status_code == 200


def test_roster_comes_from_the_database_once_loaded(test_client, mocker: MockerFixture):
    """The screens must list pilots even when the live standings page is empty.

    WatchMeFly publishes no standings table while an event is still running, so
    scraping it returns nothing. Anything already loaded has to come from the
    database instead.
    """
    add_user_data_and_assert(ONE_COMPETITION_DUMMY_DATA, test_client, [200])

    session = next(get_test_db())
    competitors = preprocess_competitors(
        [
            CompetitorModel(competitor_name="ZEBERLI, Stefan", competitor_country="Switzerland"),
            CompetitorModel(competitor_name="BAREFORD, Dominic", competitor_country="United Kingdom"),
        ],
        session=session,
    )
    task = TaskModel(competition_id=1, task_url="u", task_name="Fly In", task_status="Provisional", task_order=1)
    session.add(task)
    session.commit()
    session.refresh(task)
    for competitor in competitors:
        session.add(
            TaskResultModel(
                task_id=task.task_id,
                competitor_id=competitor.competitor_id,
                tr_result="1.0",
                tr_gross_score=1000,
                tr_task_penalty=0,
                tr_competition_penalty=0,
                tr_net_score=1000,
                tr_notes="",
            )
        )
    session.commit()

    # Patch where it is used, not where it is defined, so this genuinely proves
    # the endpoints never fall back to the live page once data is stored.
    scrape = mocker.patch("wmf_scraper.actions.competitor.get_competitor_data", return_value=[])

    response = test_client.get(f"{API}/competitor/get_competitors_in_competition", params={"competition_id": 1})
    assert response.status_code == 200
    assert [c["competitor_name"] for c in response.json()] == ["BAREFORD, Dominic", "ZEBERLI, Stefan"]

    response = test_client.get(f"{API}/competitor/get_countries_in_competition", params={"competition_id": 1})
    assert response.status_code == 200
    assert [c["competitor_country"] for c in response.json()] == ["Switzerland", "United Kingdom"]

    response = test_client.get(
        f"{API}/competitor/get_competitors_in_competition_by_country",
        params={"competition_id": 1, "country_name": "Switzerland"},
    )
    assert response.status_code == 200
    assert [c["competitor_name"] for c in response.json()] == ["ZEBERLI, Stefan"]

    scrape.assert_not_called()
