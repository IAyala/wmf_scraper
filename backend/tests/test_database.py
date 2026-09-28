"""Schema upkeep on a database that already has results in it."""

import sqlite3

from wmf_scraper.database import DBManager

# taskmodel as it was before the tasks carried a flight.
TASKMODEL_BEFORE_FLIGHTS = """
CREATE TABLE taskmodel (
    task_id INTEGER NOT NULL PRIMARY KEY,
    competition_id INTEGER NOT NULL,
    task_url VARCHAR NOT NULL,
    task_name VARCHAR NOT NULL,
    task_status VARCHAR NOT NULL,
    task_order INTEGER NOT NULL
)
"""
FLIGHT_COLUMNS = {"flight_number", "flight_date", "flight_period"}


def columns_of(database, table: str) -> set[str]:
    with sqlite3.connect(database) as connection:
        return {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}


def test_a_new_column_reaches_a_database_that_already_exists(tmp_path):
    """create_all only creates whole tables, so the stored results of a live
    database would never gain the flight columns without this step."""
    database = tmp_path / "wmf_scraper.db"
    with sqlite3.connect(database) as connection:
        connection.execute(TASKMODEL_BEFORE_FLIGHTS)
        connection.execute("INSERT INTO taskmodel VALUES (1, 1, 'MyTaskURL', 'Fly On', 'Final', 7)")
    assert not FLIGHT_COLUMNS & columns_of(database, "taskmodel")

    manager = DBManager(in_memory=False, file_name=str(database))
    manager.sync_schema()
    manager.sync_schema()  # Running it twice must be a no-op, not an error.

    assert FLIGHT_COLUMNS <= columns_of(database, "taskmodel")
    with sqlite3.connect(database) as connection:
        # The task that was already stored is untouched, and has no flight.
        assert connection.execute("SELECT task_order, flight_number FROM taskmodel").fetchall() == [(7, None)]
        indexes = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'index'")}
    assert "ix_taskmodel_flight_number" in indexes
