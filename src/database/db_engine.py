from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists

from models.competition import CompetitionModel  # noqa

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)  # echo to print SQL statements
if not database_exists(sqlite_url):
    create_database(sqlite_url)
    logger.debug("creating db")
else:
    logger.debug("db already exists")
