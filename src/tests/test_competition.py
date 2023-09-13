import pytest


@pytest.mark.parametrize(
    "user_data_list, expected_status_code",
    [([{"url": "My strange string", "description": "My Description"}], 200)],
)
def test_competition(test_client, user_data_list, expected_status_code):
    for user_data in user_data_list:
        response = test_client.post("/competition/add", json=user_data)
        assert response.status_code == expected_status_code


if __name__ == "__main__":
    pytest.main(["-k", "test_competition"])
