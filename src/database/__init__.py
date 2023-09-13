from database.db_engine import db_engine_manager  # type: ignore


def create_db_if_not_exists() -> None:
    db_engine_manager.create_db_if_not_exists()


def db_session():
    return db_engine_manager.session
