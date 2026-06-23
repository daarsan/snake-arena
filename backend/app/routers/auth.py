import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..models import ErrorResponse, LoginRequest, SignupRequest, User
from ..security import (
    CurrentUser,
    create_session,
    hash_password,
    verify_password,
)
from ..store import UserRecord, store

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="strict",
        path="/",
    )


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
    responses={409: {"model": ErrorResponse}},
)
async def signup(body: SignupRequest, response: Response) -> User:
    if body.username in store.usernames:
        raise HTTPException(status_code=409, detail="Username already taken")

    uid = str(uuid.uuid4())
    rec = UserRecord(
        id=uid,
        username=body.username,
        hashed_password=hash_password(body.password),
    )
    store.users[uid] = rec
    store.usernames[body.username] = uid

    token = create_session()
    store.sessions[token] = uid
    _set_session_cookie(response, token)

    return User(id=uid, username=body.username)


@router.post(
    "/login",
    response_model=User,
    responses={401: {"model": ErrorResponse}},
)
async def login(body: LoginRequest, response: Response) -> User:
    uid = store.usernames.get(body.username)
    user = store.users.get(uid) if uid else None
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_session()
    store.sessions[token] = uid
    _set_session_cookie(response, token)

    return User(id=user.id, username=user.username)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    user: UserRecord = CurrentUser,
) -> None:
    # Invalidate all sessions for this user
    dead = [t for t, uid in store.sessions.items() if uid == user.id]
    for t in dead:
        del store.sessions[t]
    response.delete_cookie("session", path="/")


@router.get(
    "/me",
    response_model=User,
    responses={401: {"model": ErrorResponse}},
)
async def me(user: UserRecord = CurrentUser) -> User:
    return User(id=user.id, username=user.username)
