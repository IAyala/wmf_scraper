from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

from wmf_scraper.security import (
    User,
    authenticate,
    clear_session,
    issue_session,
    require_user,
)

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    role: str


@router.post("/login", summary="Exchange credentials for a session cookie")
async def login(req: LoginRequest, response: Response) -> UserResponse:
    user = authenticate(req.username, req.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    issue_session(response, user)
    return UserResponse(username=user.username, role=user.role)


@router.post("/logout", summary="Clear the session cookie")
async def logout(response: Response) -> dict:
    clear_session(response)
    return {"status": "ok"}


@router.get("/me", summary="Details of the currently authenticated user")
async def me(user: User = Depends(require_user)) -> UserResponse:
    return UserResponse(username=user.username, role=user.role)
