import json
import logging
from pathlib import Path
from typing import List

import pytest
from _pytest.logging import caplog as _caplog
from loguru import logger
from lxml import html
from pydantic import BaseModel
from starlette.testclient import TestClient

from database import create_db_if_not_exists, drop_test_db, get_db, get_test_db
from main import app
from models.competition import CompetitionRequest

FILE_FOLDER = "html_examples"
EXPECTED_FOLDER = "html_examples_expected"


def get_test_files(data_tests_folder: str, tests_to_run: str) -> List[Path]:
    return list(resolve_path(f"{data_tests_folder}/{FILE_FOLDER}").glob(tests_to_run))


ONE_COMPETITION_DUMMY_DATA = [CompetitionRequest(url="MyURL", description="_")]


def get_xml_tree_from_file(path: Path):
    with open(path, "r") as f:
        return html.fromstring(f.read())


def path_to_read_expected(path: Path) -> Path:
    index_to_change = path.parts.index(FILE_FOLDER)
    return (
        Path(*path.parts[0:index_to_change])
        .joinpath(EXPECTED_FOLDER)
        .joinpath(*path.parts[index_to_change + 1 :])
        .with_suffix(".json")
    )


class ExpectedCompetitorTask(BaseModel):
    expected_number_competitors: int
    expected_number_tasks: int
    expected_response: int
    tasks: List[str]


class ExpectedTaskResults(BaseModel):
    expected_number_task_results: int


def get_expected_competitor_and_task(path: Path) -> ExpectedCompetitorTask:
    with open(path_to_read_expected(path), "r") as f:
        return ExpectedCompetitorTask(**json.load(f))


def get_expected_task_results(path: Path) -> ExpectedTaskResults:
    with open(path_to_read_expected(path), "r") as f:
        return ExpectedTaskResults(**json.load(f))


def resolve_path(path: str) -> Path:
    dir_path = Path(__file__).resolve().parent
    return dir_path.joinpath(path)


@pytest.fixture(scope="function")
def test_client():
    create_db_if_not_exists(is_test=True)
    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    drop_test_db()


@pytest.fixture(scope="session", autouse=True)
def set_loguru_sink():
    dir_path = Path(__file__).resolve().parent
    log_file = dir_path.joinpath("tests.log")
    if log_file.exists():
        log_file.unlink()
    logger.add(log_file)


@pytest.fixture(scope="function", autouse=True)
def caplog(_caplog: _caplog):  # type: ignore
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropagateHandler(), format="{message}")  # type: ignore
    yield _caplog
    logger.remove(handler_id)
