import pytest

from models.competition import CompetitionRequest


@pytest.mark.parametrize(
    "user_data_list, expected_status_code",
    [
        ([CompetitionRequest(url="MyURL", description="_")], [200]),
        (
            [
                CompetitionRequest(url="RepeatedURL", description="_"),
                CompetitionRequest(url="RepeatedURL", description="_"),
            ],
            [200, 500],
        ),
    ],
)
def test_competition_add(test_client, user_data_list, expected_status_code):
    for user_data, expected_status in zip(user_data_list, expected_status_code):
        response = test_client.post("/competition/add", json=user_data.dict())
        assert response.status_code == expected_status


@pytest.mark.parametrize(
    "user_data_to_add, desc_to_find, expected_len_result",
    [
        (
            [
                CompetitionRequest(url="DummyURL", description="MyDescription"),
                CompetitionRequest(url="DummyURL_2", description="DifferentDesc"),
            ],
            "Diff",
            1,
        ),
        ([], "MyDesc", 1),
        ([], "Worlds", 0),
    ],
)
def test_competition_get_by_desc(
    test_client, user_data_to_add, desc_to_find, expected_len_result
):
    for user_data in user_data_to_add:
        response = test_client.post("/competition/add", json=user_data.dict())
        assert response.status_code == 200
    response = test_client.get(
        "/competition/get_by_description", params={"description": desc_to_find}
    )
    assert response.status_code == 200
    assert len(response.json()) == expected_len_result
