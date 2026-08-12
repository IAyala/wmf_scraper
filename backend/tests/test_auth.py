import os

import pytest

from tests.conftest import API

PROTECTED_READ = f"{API}/competition/get_all_competitions"
PROTECTED_WRITE = f"{API}/competition/add_one"
WRITE_PARAMS = {
    "competition_description": "Test",
    "competition_url": "https://example.com",
}


def test_version_is_public(anonymous_client):
    assert anonymous_client.get(f"{API}/version").status_code == 200


@pytest.mark.parametrize("endpoint", [PROTECTED_READ, PROTECTED_WRITE])
def test_anonymous_is_rejected(anonymous_client, endpoint):
    method = anonymous_client.post if endpoint == PROTECTED_WRITE else anonymous_client.get
    response = method(endpoint, params=WRITE_PARAMS)
    assert response.status_code == 401


@pytest.mark.parametrize(
    "username_key, password_key",
    [
        ("SUPERADMIN_USERNAME", "ADMIN_PASSWORD"),
        ("ADMIN_USERNAME", "SUPERADMIN_PASSWORD"),
    ],
)
def test_login_with_wrong_password(anonymous_client, username_key, password_key):
    response = anonymous_client.post(
        f"{API}/auth/login",
        json={
            "username": os.environ[username_key],
            "password": os.environ[password_key],
        },
    )
    assert response.status_code == 401


def test_login_with_unknown_user(anonymous_client):
    response = anonymous_client.post(f"{API}/auth/login", json={"username": "nobody", "password": "nothing"})
    assert response.status_code == 401


def test_login_sets_session_and_me_reports_role(test_client):
    response = test_client.get(f"{API}/auth/me")
    assert response.status_code == 200
    assert response.json() == {
        "username": os.environ["SUPERADMIN_USERNAME"],
        "role": "superadmin",
    }


def test_logout_clears_the_session(test_client):
    assert test_client.post(f"{API}/auth/logout").status_code == 200
    assert test_client.get(f"{API}/auth/me").status_code == 401


def test_admin_can_read_but_not_write(admin_client):
    assert admin_client.get(PROTECTED_READ).status_code == 200
    response = admin_client.post(PROTECTED_WRITE, params=WRITE_PARAMS)
    assert response.status_code == 403


def test_superadmin_can_write(test_client):
    response = test_client.post(PROTECTED_WRITE, params=WRITE_PARAMS)
    assert response.status_code == 200


def test_api_key_grants_superadmin(anonymous_client):
    headers = {"Authorization": f"Bearer {os.environ['API_KEY']}"}
    assert anonymous_client.get(PROTECTED_READ, headers=headers).status_code == 200
    response = anonymous_client.post(PROTECTED_WRITE, params=WRITE_PARAMS, headers=headers)
    assert response.status_code == 200


def test_wrong_api_key_is_rejected(anonymous_client):
    headers = {"Authorization": "Bearer not-the-key"}
    assert anonymous_client.get(PROTECTED_READ, headers=headers).status_code == 401


def test_tampered_session_cookie_is_rejected(anonymous_client):
    anonymous_client.cookies.set("wmf_session", "forged.session.value")
    assert anonymous_client.get(f"{API}/auth/me").status_code == 401
