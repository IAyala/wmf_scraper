from dataclasses import dataclass
from typing import Optional

from sqlalchemy.pool import StaticPool
from sqlalchemy_utils import database_exists
from sqlmodel import Session, SQLModel, create_engine

from models.competition import CompetitionModel  # noqa
from models.competitor import CompetitorModel  # noqa
from models.task import TaskModel  # noqa
from models.task_result import TaskResultModel  # noqa


@dataclass
class DBManager:
    in_memory: bool
    must_show_debug_messages: bool
    file_name: Optional[str] = None

    def __post_init__(self):
        self.engine = create_engine(
            self.url,
            connect_args={"check_same_thread": False},
            echo=self.must_show_debug_messages,
            poolclass=StaticPool,
        )

    @property
    def url(self) -> str:
        if self.in_memory:
            return "sqlite:///:memory:"
        return f"sqlite:///{self.file_name}"

    def create_db_if_not_exists(self) -> None:
        if self.in_memory or not database_exists(self.url):
            SQLModel.metadata.create_all(self.engine)

    def drop_db(self) -> None:
        SQLModel.metadata.drop_all(self.engine)

    @property
    def session(self) -> Session:
        return Session(self.engine)


db_engine_manager = DBManager(
    in_memory=False, must_show_debug_messages=False, file_name="database.db"
)  # pragma: no cover


db_test_engine_manager = DBManager(in_memory=True, must_show_debug_messages=False)


def _db_session(is_test: bool = False) -> Session:
    if is_test:
        return db_test_engine_manager.session
    else:
        return db_engine_manager.session  # pragma: no cover
