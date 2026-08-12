from sqlmodel import Session, select

from tests.conftest import ONE_COMPETITION_DUMMY_DATA
from tests.test_competition import add_user_data_and_assert
from wmf_scraper.actions.load import competition_fingerprint
from wmf_scraper.database import db_test_engine_manager
from wmf_scraper.models.competitor import CompetitorModel
from wmf_scraper.models.task import TaskModel
from wmf_scraper.models.task_result import TaskResultModel

COMPETITION_ID = 1


def store_one_task_with_result(session: Session, task_id: int, net_score: int) -> None:
    session.add(
        TaskModel(
            task_id=task_id,
            competition_id=COMPETITION_ID,
            task_url="MyTaskURL",
            task_name="Task 1 - Pilot Declared Goal",
            task_status="Final",
            task_order=1,
        )
    )
    session.add(
        TaskResultModel(
            task_id=task_id,
            competitor_id=1,
            tr_result="10.5",
            tr_gross_score=net_score,
            tr_task_penalty=0,
            tr_competition_penalty=0,
            tr_net_score=net_score,
            tr_notes="",
        )
    )
    session.commit()


def purge(session: Session) -> None:
    for model in (TaskResultModel, TaskModel):
        for row in session.exec(select(model)).all():
            session.delete(row)
    session.commit()


def test_fingerprint_ignores_row_ids(test_client):
    """Reloading identical data must not look like a change, even though the
    purge-and-insert gives every task a brand new id."""
    add_user_data_and_assert(ONE_COMPETITION_DUMMY_DATA, test_client, [200])
    with db_test_engine_manager.session as session:
        session.add(CompetitorModel(competitor_id=1, competitor_name="A Pilot", competitor_country="ESP"))
        store_one_task_with_result(session, task_id=1, net_score=1000)
        before = competition_fingerprint(competition_id=COMPETITION_ID, session=session)

        purge(session)
        store_one_task_with_result(session, task_id=2, net_score=1000)
        assert competition_fingerprint(competition_id=COMPETITION_ID, session=session) == before

        purge(session)
        store_one_task_with_result(session, task_id=3, net_score=999)
        assert competition_fingerprint(competition_id=COMPETITION_ID, session=session) != before


def test_fingerprint_of_unloaded_competition(test_client):
    add_user_data_and_assert(ONE_COMPETITION_DUMMY_DATA, test_client, [200])
    with db_test_engine_manager.session as session:
        empty = competition_fingerprint(competition_id=COMPETITION_ID, session=session)
        session.add(CompetitorModel(competitor_id=1, competitor_name="A Pilot", competitor_country="ESP"))
        store_one_task_with_result(session, task_id=1, net_score=1000)
        assert competition_fingerprint(competition_id=COMPETITION_ID, session=session) != empty
