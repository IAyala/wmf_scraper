from datetime import date

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

# Two flights: the first morning set tasks 1 and 2, the second set task 4.
# Whoever wins a flight is not necessarily anywhere near the top overall.
FLIGHT_OF_TASK = {
    1: (1, date(2026, 8, 10), "AM"),
    2: (1, date(2026, 8, 10), "AM"),
    4: (2, date(2026, 8, 11), "PM"),
}


def store_competition_with_a_cancelled_task(session: Session) -> None:
    for position, task_order in enumerate(TASK_ORDERS, start=1):
        flight_number, flight_date, flight_period = FLIGHT_OF_TASK[task_order]
        session.add(
            TaskModel(
                task_id=position,
                competition_id=COMPETITION_ID,
                task_url=f"MyTaskURL{task_order}",
                task_name="Fly On",
                task_status="Final",
                task_order=task_order,
                flight_number=flight_number,
                flight_date=flight_date,
                flight_period=flight_period,
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


def stored_competition(test_client) -> None:
    add_user_data_and_assert(ONE_COMPETITION_DUMMY_DATA, test_client, [200])
    with db_test_engine_manager.session as session:
        store_competition_with_a_cancelled_task(session)


def flight_positions(test_client, flight_number: int) -> dict[str, int]:
    response = test_client.get(
        f"{API}/query/flight_results_competition",
        params={"competition_id": COMPETITION_ID, "flight_number": flight_number},
    )
    assert response.status_code == 200, response.text
    return {row["competitor_name"]: row["position"] for row in response.json()}


def test_flights_of_a_competition_are_listed_with_their_tasks(test_client):
    stored_competition(test_client)

    response = test_client.get(f"{API}/query/flights_in_competition", params={"competition_id": COMPETITION_ID})
    assert response.status_code == 200, response.text
    assert response.json() == [
        {"flight_number": 1, "flight_date": "2026-08-10", "flight_period": "AM", "task_orders": [1, 2]},
        {"flight_number": 2, "flight_date": "2026-08-11", "flight_period": "PM", "task_orders": [4]},
    ]


def test_a_flight_is_scored_on_its_own_tasks(test_client):
    """Winning a flight and winning the competition are different things."""
    stored_competition(test_client)

    assert flight_positions(test_client, 1) == {"LEADER, Early": 1, "WINNER, Late": 2}
    assert flight_positions(test_client, 2) == {"WINNER, Late": 1, "LEADER, Early": 2}
    assert overall_positions(test_client) == {"WINNER, Late": 1, "LEADER, Early": 2}


def test_a_flight_that_was_never_flown_has_no_classification(test_client):
    stored_competition(test_client)

    assert flight_positions(test_client, 9) == {}


def test_competitor_results_carry_the_flight_and_can_be_filtered_by_it(test_client):
    stored_competition(test_client)

    def results(**params):
        response = test_client.get(
            f"{API}/query/results_competitor_in_competition",
            params={"competition_id": COMPETITION_ID, "competitor_name": "LEADER, Early", **params},
        )
        assert response.status_code == 200, response.text
        return response.json()

    every_task = results()
    assert [row["task_order"] for row in every_task] == TASK_ORDERS
    assert [row["flight_number"] for row in every_task] == [1, 1, 2]
    assert every_task[0]["flight_date"] == "2026-08-10"
    assert every_task[0]["flight_period"] == "AM"

    second_flight = results(flight_number=2)
    assert [row["task_order"] for row in second_flight] == [4]


def test_flights_are_absent_for_a_competition_loaded_without_them(test_client):
    """Tasks with no flight are left out rather than grouped under a fake one."""
    add_user_data_and_assert(ONE_COMPETITION_DUMMY_DATA, test_client, [200])
    with db_test_engine_manager.session as session:
        session.add(
            TaskModel(
                task_id=1,
                competition_id=COMPETITION_ID,
                task_url="MyTaskURL",
                task_name="Fly On",
                task_status="Final",
                task_order=1,
            )
        )
        session.commit()

    response = test_client.get(f"{API}/query/flights_in_competition", params={"competition_id": COMPETITION_ID})
    assert response.status_code == 200, response.text
    assert response.json() == []


TIED_SCORES = {"WINNER, Clear": 1000, "TIED, One": 500, "TIED, Two": 500, "LAST, Place": 250}


def store_one_task_with_tied_scores(session: Session) -> None:
    session.add(
        TaskModel(
            task_id=1,
            competition_id=COMPETITION_ID,
            task_url="MyTaskURL",
            task_name="Hesitation Waltz",
            task_status="Final",
            task_order=1,
            flight_number=1,
            flight_date=date(2026, 8, 10),
            flight_period="AM",
        )
    )
    for competitor_id, (name, score) in enumerate(TIED_SCORES.items(), start=1):
        session.add(CompetitorModel(competitor_id=competitor_id, competitor_name=name, competitor_country="ESP"))
        session.add(
            TaskResultModel(
                task_id=1,
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


def task_results(test_client, task_order: int) -> list[dict]:
    response = test_client.get(
        f"{API}/query/task_results_competition",
        params={"competition_id": COMPETITION_ID, "task_order": task_order},
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_tasks_of_a_competition_are_listed_in_order(test_client):
    stored_competition(test_client)

    response = test_client.get(f"{API}/query/tasks_in_competition", params={"competition_id": COMPETITION_ID})
    assert response.status_code == 200, response.text
    assert [task["task_order"] for task in response.json()] == TASK_ORDERS
    assert [task["flight_number"] for task in response.json()] == [1, 1, 2]
    assert response.json()[0]["task_name"] == "Fly On"


def test_a_task_is_ranked_on_its_own_scores(test_client):
    stored_competition(test_client)

    # Task 1: LEADER scored 1000, WINNER 500.
    assert [(row["position"], row["competitor_name"]) for row in task_results(test_client, 1)] == [
        (1, "LEADER, Early"),
        (2, "WINNER, Late"),
    ]
    # Task 4, the one that decided the competition, went the other way.
    assert [(row["position"], row["competitor_name"]) for row in task_results(test_client, 4)] == [
        (1, "WINNER, Late"),
        (2, "LEADER, Early"),
    ]


def test_tied_scores_share_a_position(test_client):
    """Half a field scoring the same is normal in a single task, so equal
    scores share the better position and the next score skips past them."""
    add_user_data_and_assert(ONE_COMPETITION_DUMMY_DATA, test_client, [200])
    with db_test_engine_manager.session as session:
        store_one_task_with_tied_scores(session)

    ranked = [(row["position"], row["competitor_name"]) for row in task_results(test_client, 1)]
    assert ranked == [
        (1, "WINNER, Clear"),
        (2, "TIED, One"),
        (2, "TIED, Two"),
        (4, "LAST, Place"),
    ]


def test_a_task_that_was_never_flown_has_no_results(test_client):
    stored_competition(test_client)

    assert task_results(test_client, 3) == []
