from collections.abc import Iterator
from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy import Engine, inspect
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from wmf_scraper.models.competition import CompetitionModel  # noqa: F401
from wmf_scraper.models.competitor import CompetitorModel  # noqa: F401
from wmf_scraper.models.task import TaskModel  # noqa: F401
from wmf_scraper.models.task_result import TaskResultModel  # noqa: F401
from wmf_scraper.settings import get_database_path


@dataclass
class DBManager:
    """Owns a SQLite engine and hands out sessions against it."""

    in_memory: bool
    file_name: str | None = None
    echo: bool = False
    engine: Engine = field(init=False)

    def __post_init__(self) -> None:
        self.engine = create_engine(
            self.url,
            connect_args={"check_same_thread": False},
            echo=self.echo,
            poolclass=StaticPool,
        )

    @property
    def url(self) -> str:
        if self.in_memory:
            return "sqlite:///:memory:"
        return f"sqlite:///{self.file_name}"

    def create_tables(self) -> None:
        """Create any table that does not exist yet. Existing data is untouched."""
        SQLModel.metadata.create_all(self.engine)

    def add_missing_columns(self) -> None:
        """Add columns the models have gained since the tables were created.

        create_all only ever creates whole tables, so a new field on an existing
        model is invisible to it and every query then fails on the missing
        column. SQLite's ADD COLUMN only touches the schema, so this is cheap
        even on a database with results in it.
        """
        inspector = inspect(self.engine)
        for table in SQLModel.metadata.sorted_tables:
            if table.name not in inspector.get_table_names():
                continue
            stored = {column["name"] for column in inspector.get_columns(table.name)}
            for column in (c for c in table.columns if c.name not in stored):
                if not column.nullable:
                    raise RuntimeError(
                        f"Cannot add non-nullable column {table.name}.{column.name} to an existing table. "
                        "Give it a default, or migrate the table by hand."
                    )
                column_type = column.type.compile(self.engine.dialect)
                with self.engine.begin() as connection:
                    connection.exec_driver_sql(f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {column_type}')
                logger.info(f"Added column {table.name}.{column.name} ({column_type})")

    def create_missing_indexes(self) -> None:
        """Index a column added after its table was created."""
        for table in SQLModel.metadata.sorted_tables:
            for index in table.indexes:
                index.create(bind=self.engine, checkfirst=True)

    def sync_schema(self) -> None:
        """Bring the database up to what the models currently declare."""
        self.create_tables()
        self.add_missing_columns()
        self.create_missing_indexes()

    def drop_tables(self) -> None:
        SQLModel.metadata.drop_all(self.engine)

    @property
    def session(self) -> Session:
        return Session(self.engine)


db_engine_manager = DBManager(in_memory=False, file_name=get_database_path())
db_test_engine_manager = DBManager(in_memory=True)


def create_db_if_not_exists(is_test: bool = False) -> None:
    manager = db_test_engine_manager if is_test else db_engine_manager
    manager.sync_schema()


def drop_test_db() -> None:
    db_test_engine_manager.drop_tables()


def get_db() -> Iterator[Session]:  # pragma: no cover
    db = db_engine_manager.session
    try:
        yield db
    finally:
        db.close()


def get_test_db() -> Iterator[Session]:
    db = db_test_engine_manager.session
    try:
        yield db
    finally:
        db.close()
