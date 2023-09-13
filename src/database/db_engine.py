from dataclasses import dataclass
from typing import Optional

from loguru import logger
from sqlalchemy_utils import database_exists
from sqlmodel import Session, SQLModel, create_engine

from models.competition import CompetitionModel  # noqa


@dataclass
class DBManager:
    in_memory: bool = True
    must_show_debug_messages: bool = False
    file_name: Optional[str] = None

    def __post_init__(self):
        self.engine = create_engine(self.url, echo=True)

    @property
    def url(self) -> str:
        if self.in_memory:
            return "sqlite://"
        return f"sqlite:///{self.file_name}"

    def create_db_if_not_exists(self) -> None:
        if not database_exists(self.url):
            SQLModel.metadata.create_all(self.engine)
            logger.debug("Creating Fresh DB")
        else:
            logger.debug(f"DB {self.url} already exists")

    @property
    def session(self) -> Session:
        return Session(self.engine)


db_engine_manager = DBManager(
    in_memory=False, must_show_debug_messages=True, file_name="database.db"
)
