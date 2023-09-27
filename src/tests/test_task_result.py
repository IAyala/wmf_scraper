from parser.task_results import get_task_results

import pytest
from pytest_mock import MockerFixture

from models.task import TaskModel
from tests.conftest import (
    get_expected_task_results,
    get_test_files,
    get_xml_tree_from_file,
)

TESTS_TO_RUN: str = "**/*.html"
DATA_TESTS_FOLDER: str = "data/task_results"
DUMMY_TASK_MODEL = TaskModel(
    task_url="dummy",
    task_name="dummy",
    task_status="dummy",
    task_order=-1,
    competition_id=-1,
)


@pytest.mark.parametrize(
    "html_file",
    [(x) for x in get_test_files(DATA_TESTS_FOLDER, TESTS_TO_RUN)],
)
def test_task_results_parser(html_file, mocker: MockerFixture):
    mocker.patch(
        "parser.utilities._html_from_url",
        return_value=get_xml_tree_from_file(html_file),
    )
    task_results = get_task_results(DUMMY_TASK_MODEL)
    expected = get_expected_task_results(html_file)
    assert len(task_results) == expected.expected_number_task_results
