"""Authentication for the WMF Scraper API.

Two ways to authenticate, both accepted on protected endpoints:

* **Session cookie** — the browser posts to ``/api/auth/login``; on success it
  receives a signed, HttpOnly cookie. No credential ever reaches the frontend
  bundle.
* **Bearer API key** — ``Authorization: Bearer <API_KEY>`` for scripts and
  automation. Treated as ``superadmin``.
"""

import secrets
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, Response, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from wmf_scraper.settings import (
    get_api_key,
    get_credentials,
    get_session_secret,
    is_development_mode,
)

SESSION_COOKIE = "wmf_session"
SESSION_MAX_AGE_SECONDS = 12 * 60 * 60
ROLE_RANK = {"admin": 1, "superadmin": 2}

# Only used when SESSION_SECRET is unset, which is refused outside development.
_DEV_FALLBACK_SECRET = "development-only-not-a-secret"


@dataclass(frozen=True)
class User:
    username: str
    role: str

    def has_role(self, required: str) -> bool:
        return ROLE_RANK.get(self.role, 0) >= ROLE_RANK[required]


def _serializer() -> URLSafeTimedSerializer:
    secret = get_session_secret()
    if not secret:
        if not is_development_mode():  # pragma: no cover - guarded at startup
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SESSION_SECRET is not configured on the server",
            )
        secret = _DEV_FALLBACK_SECRET
    return URLSafeTimedSerializer(secret, salt=SESSION_COOKIE)


def authenticate(username: str, password: str) -> User | None:
    """Check credentials in constant time. Returns the user, or None."""
    credentials = get_credentials()
    expected = credentials.get(username)
    if expected is None:
        # Still burn a comparison so a missing user is not measurably faster.
        secrets.compare_digest(password, password)
        return None
    expected_password, role = expected
    if not secrets.compare_digest(password, expected_password):
        return None
    return User(username=username, role=role)


def issue_session(response: Response, user: User) -> None:
    token = _serializer().dumps({"username": user.username, "role": user.role})
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
        secure=not is_development_mode(),
        path="/",
    )


def clear_session(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/")


def _user_from_cookie(request: Request) -> User | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    try:
        payload = _serializer().loads(token, max_age=SESSION_MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return None
    username, role = payload.get("username"), payload.get("role")
    if not username or role not in ROLE_RANK:
        return None
    return User(username=username, role=role)


def _user_from_bearer(request: Request) -> User | None:
    configured = get_api_key()
    if not configured:
        return None
    header = request.headers.get("Authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    if not secrets.compare_digest(token, configured):
        return None
    return User(username="api-key", role="superadmin")


def current_user(request: Request) -> User | None:
    """The authenticated user for this request, or None. Never raises."""
    return _user_from_cookie(request) or _user_from_bearer(request)


def require_user(user: User | None = Depends(current_user)) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user


def require_superadmin(user: User = Depends(require_user)) -> User:
    if not user.has_role("superadmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This operation requires the superadmin role",
        )
    return user
