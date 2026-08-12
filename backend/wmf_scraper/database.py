from collections.abc import Iterator
from dataclasses import dataclass, field

from sqlalchemy import Engine
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

    def drop_tables(self) -> None:
        SQLModel.metadata.drop_all(self.engine)

    @property
    def session(self) -> Session:
        return Session(self.engine)


db_engine_manager = DBManager(in_memory=False, file_name=get_database_path())
db_test_engine_manager = DBManager(in_memory=True)


def create_db_if_not_exists(is_test: bool = False) -> None:
    manager = db_test_engine_manager if is_test else db_engine_manager
    manager.create_tables()


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
