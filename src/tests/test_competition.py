import pytest

from models.competition import CompetitionRequest
from tests.conftest import ONE_COMPETITION_DUMMY_DATA


@pytest.mark.parametrize(
    "user_data_list, expected_status_code",
    [
        (ONE_COMPETITION_DUMMY_DATA, [200]),
        (ONE_COMPETITION_DUMMY_DATA * 2, [200, 400]),
    ],
)
def test_competition_add(test_client, user_data_list, expected_status_code):
    for user_data, expected_status in zip(user_data_list, expected_status_code):
        response = test_client.post("/competition/add_one", json=user_data.dict())
        assert response.status_code == expected_status


user_data_to_add = [
    CompetitionRequest(url="DummyURL", description="MyDescription"),
    CompetitionRequest(url="DummyURL_2", description="DifferentDesc"),
]


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
    for user_data in user_data_to_add:
        response = test_client.post("/competition/add_one", json=user_data.dict())
        assert response.status_code == 200
    response = test_client.get(
        "/competition/get_competition_by_description",
        params={"description": desc_to_find},
    )
    assert response.status_code == 200
    assert len(response.json()) == expected_len_result


@pytest.mark.parametrize(
    "user_data_to_add, expected_len_result",
    [(user_data_to_add, 2)],
)
def test_competition_get_all(test_client, user_data_to_add, expected_len_result):
    for user_data in user_data_to_add:
        response = test_client.post("/competition/add_one", json=user_data.dict())
        assert response.status_code == 200
    response = test_client.get("/competition/get_all_competitions")
    assert response.status_code == 200
    assert len(response.json()) == expected_len_result
