import json
import logging
import os
from pathlib import Path

import pytest
from _pytest.logging import caplog as _caplog
from loguru import logger
from lxml import html
from pydantic import BaseModel

# Configure the environment before the application module is imported, so the
# startup checks and the database engine see test values.
os.environ["ENVIRONMENT"] = "development"
os.environ["DATABASE_PATH"] = ":memory:"
os.environ["SESSION_SECRET"] = "test-session-secret"
os.environ["ADMIN_USERNAME"] = "test-admin"
os.environ["ADMIN_PASSWORD"] = "test-admin-password"
os.environ["SUPERADMIN_USERNAME"] = "test-superadmin"
os.environ["SUPERADMIN_PASSWORD"] = "test-superadmin-password"
os.environ["API_KEY"] = "test-api-key"
os.environ.pop("STATIC_DIR", None)

from starlette.testclient import TestClient  # noqa: E402

from wmf_scraper.database import (  # noqa: E402
    create_db_if_not_exists,
    drop_test_db,
    get_db,
    get_test_db,
)
from wmf_scraper.main import app  # noqa: E402
from wmf_scraper.models.competition import CompetitionRequest  # noqa: E402

API = "/api"

FILE_FOLDER = "html_examples"
EXPECTED_FOLDER = "html_examples_expected"

ONE_COMPETITION_DUMMY_DATA = [CompetitionRequest(competition_url="MyURL", competition_description="_")]

MANY_COMPETITIONS_DUMMY_DATA = [
    [
        CompetitionRequest(competition_url="MyURL1", competition_description="Description1"),
        CompetitionRequest(competition_url="MyURL2", competition_description="Description2"),
        CompetitionRequest(competition_url="MyURL3", competition_description="Description3"),
    ]
]


def resolve_path(path: str) -> Path:
    return Path(__file__).resolve().parent.joinpath(path)


def get_test_files(data_tests_folder: str, tests_to_run: str) -> list[Path]:
    return list(resolve_path(f"{data_tests_folder}/{FILE_FOLDER}").glob(tests_to_run))


def get_xml_tree_from_file(path: Path):
    return html.fromstring(path.read_text())


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
    tasks: list[str]


class ExpectedTaskResults(BaseModel):
    expected_number_task_results: int


def get_expected_competitor_and_task(path: Path) -> ExpectedCompetitorTask:
    return ExpectedCompetitorTask(**json.loads(path_to_read_expected(path).read_text()))


def get_expected_task_results(path: Path) -> ExpectedTaskResults:
    return ExpectedTaskResults(**json.loads(path_to_read_expected(path).read_text()))


@pytest.fixture(scope="function")
def anonymous_client():
    """Client backed by the in-memory test database, with no session."""
    create_db_if_not_exists(is_test=True)
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    drop_test_db()


def _login(client: TestClient, role: str) -> TestClient:
    response = client.post(
        f"{API}/auth/login",
        json={
            "username": os.environ[f"{role.upper()}_USERNAME"],
            "password": os.environ[f"{role.upper()}_PASSWORD"],
        },
    )
    assert response.status_code == 200, response.text
    return client


@pytest.fixture(scope="function")
def test_client(anonymous_client):
    """Client logged in as superadmin. The default for most tests."""
    return _login(anonymous_client, "superadmin")


@pytest.fixture(scope="function")
def admin_client(anonymous_client):
    """Client logged in as admin, i.e. without write permissions."""
    return _login(anonymous_client, "admin")


@pytest.fixture(scope="function", autouse=True)
def caplog(_caplog: _caplog):  # type: ignore[valid-type]
    """Route loguru output into pytest's caplog."""

    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropagateHandler(), format="{message}")
    yield _caplog
    logger.remove(handler_id)
