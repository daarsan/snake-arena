import secrets

import bcrypt
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import DbSession, DbUser, get_db


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_session() -> str:
    return secrets.token_urlsafe(32)


async def get_current_user(
    session: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> DbUser:
    if session:
        row = db.query(DbSession).filter_by(token=session).first()
        if row:
            user = db.query(DbUser).filter_by(id=row.user_id).first()
            if user:
                return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


CurrentUser = Depends(get_current_user)
