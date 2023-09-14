from database.db_engine import _db_session, db_engine_manager, db_test_engine_manager


def create_db_if_not_exists(is_test: bool = False) -> None:
    if is_test:
        db_test_engine_manager.create_db_if_not_exists()
    else:
        db_engine_manager.create_db_if_not_exists()


def get_db():  # pragma: no cover
    db = _db_session(is_test=False)
    try:
        yield db
    finally:
        db.close()


def get_test_db():
    db = _db_session(is_test=True)
    try:
        yield db
    finally:
        db.close()
