from sqlmodel import create_engine

from models import Competition  # noqa

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)  # echo to print SQL statements
