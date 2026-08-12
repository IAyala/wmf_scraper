import pytest

from tests.conftest import (
    API,
    MANY_COMPETITIONS_DUMMY_DATA,
    ONE_COMPETITION_DUMMY_DATA,
)
from wmf_scraper.models.competition import CompetitionRequest


def add_user_data_and_assert(
    user_data_to_add: list[CompetitionRequest],
    test_client,
    expected_codes: list[int],
) -> None:
    for user_data, expected_code in zip(user_data_to_add, expected_codes, strict=True):
        response = test_client.post(
            f"{API}/competition/add_one",
            params={
                "competition_description": user_data.competition_description,
                "competition_url": user_data.competition_url,
            },
        )
        assert response.status_code == expected_code


@pytest.mark.parametrize(
    "user_data_list, expected_status_code",
    [
        (ONE_COMPETITION_DUMMY_DATA, [200]),
        (ONE_COMPETITION_DUMMY_DATA * 2, [200, 400]),
    ],
)
def test_competition_add_one(test_client, user_data_list, expected_status_code):
    add_user_data_and_assert(user_data_list, test_client, expected_status_code)


@pytest.mark.parametrize(
    "user_data_list, expected_status_code",
    [
        (MANY_COMPETITIONS_DUMMY_DATA, [200]),
    ],
)
def test_competition_add_many(test_client, user_data_list, expected_status_code):
    for user_data, expected_status in zip(user_data_list, expected_status_code, strict=True):
        response = test_client.post(
            f"{API}/competition/add_many",
            json=[x.model_dump() for x in user_data],
        )
        assert response.status_code == expected_status
        assert len(response.json()) == len(user_data)


user_data_to_add = [
    CompetitionRequest(competition_url="DummyURL", competition_description="MyDescription"),
    CompetitionRequest(competition_url="DummyURL_2", competition_description="DifferentDesc"),
]


@pytest.mark.parametrize(
    "user_data_to_add, expected_status_codes, competition_id_to_remove, expected_status_remove",
    [
        (user_data_to_add, [200, 200], 1, 200),
        (user_data_to_add, [200, 200], 5, 400),
    ],
)
def test_competition_remove_one(
    test_client,
    user_data_to_add,
    expected_status_codes,
    competition_id_to_remove,
    expected_status_remove,
):
    add_user_data_and_assert(user_data_to_add, test_client, expected_status_codes)
    response = test_client.post(
        f"{API}/competition/remove_one",
        params={"competition_id": competition_id_to_remove},
    )
    assert response.status_code == expected_status_remove


@pytest.mark.parametrize(
    "user_data_to_add, expected_len_result",
    [(user_data_to_add, 2)],
)
def test_competition_get_all(test_client, user_data_to_add, expected_len_result):
    add_user_data_and_assert(user_data_to_add, test_client, [200] * len(user_data_to_add))
    response = test_client.get(f"{API}/competition/get_all_competitions")
    assert response.status_code == 200
    assert len(response.json()) == expected_len_result


@pytest.mark.parametrize(
    "user_data_to_add, desc_to_find, expected_len_result",
    [
        (user_data_to_add, "Diff", 1),
        (user_data_to_add, "e", 2),
        (user_data_to_add, "Worlds", 0),
    ],
)
def test_competition_get_by_desc(test_client, user_data_to_add, desc_to_find, expected_len_result):
    add_user_data_and_assert(user_data_to_add, test_client, [200] * len(user_data_to_add))
    response = test_client.get(
        f"{API}/competition/get_competition_by_description",
        params={"description": desc_to_find},
    )
    assert response.status_code == 200
    assert len(response.json()) == expected_len_result


EDITED = {
    "competition_description": "Renamed Competition",
    "competition_url": "https://watchmefly.net/events/event.php?e=renamed&v=tt",
}


def test_competition_update_one(test_client):
    add_user_data_and_assert(ONE_COMPETITION_DUMMY_DATA, test_client, [200])

    response = test_client.post(f"{API}/competition/update_one", params={"competition_id": 1}, json=EDITED)
    assert response.status_code == 200
    assert response.json()["competition_description"] == EDITED["competition_description"]
    assert response.json()["competition_url"] == EDITED["competition_url"]

    stored = test_client.get(f"{API}/competition/get_all_competitions").json()
    assert [c["competition_description"] for c in stored] == [EDITED["competition_description"]]


def test_competition_update_unknown_id(test_client):
    response = test_client.post(f"{API}/competition/update_one", params={"competition_id": 99}, json=EDITED)
    assert response.status_code == 400
    assert response.json()["detail"] == "Competition ID: 99 not found"


@pytest.mark.parametrize("clashing_field", ["competition_description", "competition_url"])
def test_competition_update_rejects_a_duplicate(test_client, clashing_field):
    """Both fields are unique, so renaming onto another competition must fail."""
    add_user_data_and_assert(user_data_to_add, test_client, [200, 200])

    payload = {**EDITED, clashing_field: getattr(user_data_to_add[1], clashing_field)}
    response = test_client.post(f"{API}/competition/update_one", params={"competition_id": 1}, json=payload)
    assert response.status_code == 400
    assert "already uses that" in response.json()["detail"]


def test_competition_update_requires_superadmin(admin_client, test_client):
    add_user_data_and_assert(ONE_COMPETITION_DUMMY_DATA, test_client, [200])
    response = admin_client.post(f"{API}/competition/update_one", params={"competition_id": 1}, json=EDITED)
    assert response.status_code == 403


def test_competition_remove_requires_superadmin(admin_client, test_client):
    add_user_data_and_assert(ONE_COMPETITION_DUMMY_DATA, test_client, [200])
    response = admin_client.post(f"{API}/competition/remove_one", params={"competition_id": 1})
    assert response.status_code == 403


def test_competition_remove_deletes_tasks_and_results(test_client):
    """Removing a competition must take its whole subtree with it."""
    from sqlmodel import select

    from wmf_scraper.database import get_test_db
    from wmf_scraper.models.task import TaskModel
    from wmf_scraper.models.task_result import TaskResultModel

    add_user_data_and_assert(ONE_COMPETITION_DUMMY_DATA, test_client, [200])
    session = next(get_test_db())
    task = TaskModel(competition_id=1, task_url="u", task_name="Fly In", task_status="Final", task_order=1)
    session.add(task)
    session.commit()
    session.refresh(task)
    session.add(
        TaskResultModel(
            task_id=task.task_id,
            competitor_id=1,
            tr_result="1.0",
            tr_gross_score=1000,
            tr_task_penalty=0,
            tr_competition_penalty=0,
            tr_net_score=1000,
            tr_notes="",
        )
    )
    session.commit()

    response = test_client.post(f"{API}/competition/remove_one", params={"competition_id": 1})
    assert response.status_code == 200
    assert response.json()["number_tasks_removed"] == 1
    assert response.json()["number_task_results_removed"] == 1

    assert test_client.get(f"{API}/competition/get_all_competitions").json() == []
    assert session.exec(select(TaskModel)).all() == []
    assert session.exec(select(TaskResultModel)).all() == []
