import logging
from pathlib import Path

import pytest
from _pytest.logging import caplog as _caplog
from loguru import logger
from starlette.testclient import TestClient

from main import app


@pytest.fixture(scope="session", autouse=True)
def test_client():
    client = TestClient(app)
    yield client


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
