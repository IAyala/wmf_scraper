def test_version(test_client):
    response = test_client.get("/api/version")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "code_version" in response.json()
