def test_version(test_client):
    response = test_client.get("/version")
    assert response.status_code == 200
    from loguru import logger

    logger.debug(response.json())
    # assert isinstance(response, dict)
    # assert "code_version" in response.da
