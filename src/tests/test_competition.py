from typing import List

import pytest

from models.competition import CompetitionRequest
from tests.conftest import MANY_COMPETITIONS_DUMMY_DATA, ONE_COMPETITION_DUMMY_DATA


def add_user_data_and_assert(
    user_data_to_add: List[CompetitionRequest], test_client, expected_codes: List[int]
) -> None:
    for user_data, expected_code in zip(user_data_to_add, expected_codes):
        response = test_client.post(
            "/competition/add_one",
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
    for user_data, expected_status in zip(user_data_list, expected_status_code):
        response = test_client.post(
            "/competition/add_many", json=[x.model_dump() for x in user_data]
        )
        assert response.status_code == expected_status
        assert len(response.json()) == len(user_data)


user_data_to_add = [
    CompetitionRequest(
        competition_url="DummyURL", competition_description="MyDescription"
    ),
    CompetitionRequest(
        competition_url="DummyURL_2", competition_description="DifferentDesc"
    ),
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
        "/competition/remove_one", params={"competition_id": competition_id_to_remove}
    )
    assert response.status_code == expected_status_remove


@pytest.mark.parametrize(
    "user_data_to_add, expected_len_result",
    [(user_data_to_add, 2)],
)
def test_competition_get_all(test_client, user_data_to_add, expected_len_result):
    add_user_data_and_assert(
        user_data_to_add, test_client, [200] * len(user_data_to_add)
    )
    response = test_client.get("/competition/get_all_competitions")
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
def test_competition_get_by_desc(
    test_client, user_data_to_add, desc_to_find, expected_len_result
):
    add_user_data_and_assert(
        user_data_to_add, test_client, [200] * len(user_data_to_add)
    )
    response = test_client.get(
        "/competition/get_competition_by_description",
        params={"description": desc_to_find},
    )
    assert response.status_code == 200
    assert len(response.json()) == expected_len_result
