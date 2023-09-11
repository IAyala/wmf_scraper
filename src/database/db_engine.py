from loguru import logger
from sqlalchemy_utils import database_exists
from sqlmodel import SQLModel, create_engine

from models.competition import CompetitionModel  # noqa

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


def create_db_if_not_exists() -> None:
    if not database_exists(sqlite_url):
        SQLModel.metadata.create_all(engine)
        logger.debug("creating db")
    else:
        logger.debug("db already exists")
