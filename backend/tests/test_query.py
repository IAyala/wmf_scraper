from sqlmodel import Session

from tests.conftest import API, ONE_COMPETITION_DUMMY_DATA
from tests.test_competition import add_user_data_and_assert
from wmf_scraper.database import db_test_engine_manager
from wmf_scraper.models.competitor import CompetitorModel
from wmf_scraper.models.task import TaskModel
from wmf_scraper.models.task_result import TaskResultModel

COMPETITION_ID = 1

# Task 3 was cancelled and never published, so the task numbers have a hole in
# them. The two pilots swap places on the last task: whoever leads after task 2
# is not the winner of the competition.
TASK_ORDERS = [1, 2, 4]
SCORES = {
    "LEADER, Early": [1000, 100, 100],
    "WINNER, Late": [500, 500, 1000],
}


def store_competition_with_a_cancelled_task(session: Session) -> None:
    for position, task_order in enumerate(TASK_ORDERS, start=1):
        session.add(
            TaskModel(
                task_id=position,
                competition_id=COMPETITION_ID,
                task_url=f"MyTaskURL{task_order}",
                task_name="Fly On",
                task_status="Final",
                task_order=task_order,
            )
        )
    for competitor_id, (name, scores) in enumerate(SCORES.items(), start=1):
        session.add(CompetitorModel(competitor_id=competitor_id, competitor_name=name, competitor_country="ESP"))
        for task_id, score in enumerate(scores, start=1):
            session.add(
                TaskResultModel(
                    task_id=task_id,
                    competitor_id=competitor_id,
                    tr_result="10.5",
                    tr_gross_score=score,
                    tr_task_penalty=0,
                    tr_competition_penalty=0,
                    tr_net_score=score,
                    tr_notes="",
                )
            )
    session.commit()


def path_of(test_client, competitor_name: str) -> dict:
    response = test_client.get(
        f"{API}/query/position_path_in_competition",
        params={"competition_id": COMPETITION_ID, "competitor_name": competitor_name},
    )
    assert response.status_code == 200, response.text
    return response.json()


def overall_positions(test_client) -> dict[str, int]:
    response = test_client.get(f"{API}/query/overall_results_competition", params={"competition_id": COMPETITION_ID})
    assert response.status_code == 200, response.text
    return {row["competitor_name"]: row["position"] for row in response.json()}


def test_path_ends_on_the_overall_position(test_client):
    """The last point of the path is the final classification.

    Counting the tasks instead of reading their numbers used to cut the path
    short by exactly the number of cancelled tasks, so the chart ended on the
    standings of an earlier task and contradicted the overalls.
    """
    add_user_data_and_assert(ONE_COMPETITION_DUMMY_DATA, test_client, [200])
    with db_test_engine_manager.session as session:
        store_competition_with_a_cancelled_task(session)

    overall = overall_positions(test_client)
    assert overall == {"WINNER, Late": 1, "LEADER, Early": 2}

    for name, position in overall.items():
        assert path_of(test_client, name)["competitor_positions"][-1] == position


def test_path_is_labelled_with_the_published_task_numbers(test_client):
    add_user_data_and_assert(ONE_COMPETITION_DUMMY_DATA, test_client, [200])
    with db_test_engine_manager.session as session:
        store_competition_with_a_cancelled_task(session)

    path = path_of(test_client, "LEADER, Early")
    assert path["task_orders"] == TASK_ORDERS
    # Leads while the early tasks are all that count, loses on the last one.
    assert path["competitor_positions"] == [1, 1, 2]
