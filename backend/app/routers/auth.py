import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..database import DbSession, DbUser, get_db
from ..models import ErrorResponse, LoginRequest, SignupRequest, User
from ..security import CurrentUser, create_session, hash_password, verify_password

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
async def signup(body: SignupRequest, response: Response, db: Session = Depends(get_db)) -> User:
    if db.query(DbUser).filter_by(username=body.username).first():
        raise HTTPException(status_code=409, detail="Username already taken")

    uid = str(uuid.uuid4())
    db.add(DbUser(id=uid, username=body.username, hashed_password=hash_password(body.password)))

    token = create_session()
    db.add(DbSession(token=token, user_id=uid))
    db.commit()

    _set_session_cookie(response, token)
    return User(id=uid, username=body.username)


@router.post(
    "/login",
    response_model=User,
    responses={401: {"model": ErrorResponse}},
)
async def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)) -> User:
    user = db.query(DbUser).filter_by(username=body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_session()
    db.add(DbSession(token=token, user_id=user.id))
    db.commit()

    _set_session_cookie(response, token)
    return User(id=user.id, username=user.username)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response, user: DbUser = CurrentUser, db: Session = Depends(get_db)) -> None:
    db.query(DbSession).filter_by(user_id=user.id).delete()
    db.commit()
    response.delete_cookie("session", path="/")


@router.get(
    "/me",
    response_model=User,
    responses={401: {"model": ErrorResponse}},
)
async def me(user: DbUser = CurrentUser) -> User:
    return User(id=user.id, username=user.username)
