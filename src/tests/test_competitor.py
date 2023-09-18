import pytest
from pytest_mock import MockerFixture

from tests.conftest import (
    ONE_COMPETITION_DUMMY_DATA,
    get_expected_competitor_and_task,
    get_test_files,
    get_xml_tree_from_file,
)

TESTS_TO_RUN: str = "**/*.html"
DATA_TESTS_FOLDER: str = "data/competitors_and_tasks"


@pytest.mark.parametrize(
    "user_data_to_add, html_file",
    [
        (ONE_COMPETITION_DUMMY_DATA, x)
        for x in get_test_files(DATA_TESTS_FOLDER, TESTS_TO_RUN)
    ],
)
def test_competitor_parser(
    test_client, user_data_to_add, html_file, mocker: MockerFixture
):
    for user_data in user_data_to_add:
        response = test_client.post("/competition/add", json=user_data.dict())
        assert response.status_code == 200
    mocker.patch(
        "parser.parse_utilities._html_from_url",
        return_value=get_xml_tree_from_file(html_file),
    )
    response = test_client.get(
        "/competitor/get_competitors_in_competition", params={"competition_id": 1}
    )
    expected = get_expected_competitor_and_task(html_file)
    assert response.status_code == expected.expected_response
    if response.status_code == 200:
        assert len(response.json()) == expected.expected_number_competitors


def test_competitor_empty_competitions(test_client):
    response = test_client.get(
        "/competitor/get_competitors_in_competition", params={"competition_id": 1}
    )
    assert response.status_code == 200
    assert response.json() == []
