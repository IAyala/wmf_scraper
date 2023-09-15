import json
from pathlib import Path
from typing import Any, Dict, List

import pytest
from lxml import html
from pytest_mock import MockerFixture

from models.competition import CompetitionRequest
from tests.conftest import resolve_path

FILE_FOLDER = "html_examples"
EXPECTED_FOLDER = "html_examples_expected"

TESTS_TO_RUN: str = "**/*.html"
TESTS_FILES: List[Path] = list(resolve_path(f"data/{FILE_FOLDER}").glob(TESTS_TO_RUN))
user_data_to_add = [CompetitionRequest(url="MyURL", description="_")]


def get_xml_tree_from_file(path: Path):
    with open(path, "r") as f:
        return html.fromstring(f.read())


def get_expected_results_from_file(path: Path) -> Dict[str, Any]:
    index_to_change = path.parts.index(FILE_FOLDER)
    path_to_read = (
        Path(*path.parts[0:index_to_change])
        .joinpath(EXPECTED_FOLDER)
        .joinpath(*path.parts[index_to_change + 1 :])
        .with_suffix(".json")
    )
    with open(path_to_read, "r") as f:
        return json.load(f)


@pytest.mark.parametrize(
    "user_data_to_add, html_file",
    [(user_data_to_add, x) for x in TESTS_FILES],
)
def test_tasks_parser(test_client, user_data_to_add, html_file, mocker: MockerFixture):
    for user_data in user_data_to_add:
        response = test_client.post("/competition/add", json=user_data.dict())
        assert response.status_code == 200
    mocker.patch(
        "parser.parse_utilities.html_from_url",
        return_value=get_xml_tree_from_file(html_file),
    )
    response = test_client.get(
        "/task/get_tasks_for_competition", params={"competition_id": 1}
    )
    expected = get_expected_results_from_file(html_file)
    assert response.status_code == expected["expected_response"]
    if response.status_code == 200:
        assert len(response.json()) == expected["expected_number_tasks"]
        assert [
            x["name"] for x in sorted(response.json(), key=lambda x: x["task_id"])
        ] == expected["tasks"]


def test_tasks_empty_competitions(test_client):
    response = test_client.get(
        "/task/get_tasks_for_competition", params={"competition_id": 1}
    )
    assert response.status_code == 200
    assert response.json() == []
