import secrets

import bcrypt
from fastapi import Cookie, Depends, HTTPException, status

from .store import UserRecord, store


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_session() -> str:
    return secrets.token_urlsafe(32)


async def get_current_user(
    session: str | None = Cookie(default=None),
) -> UserRecord:
    if not session or session not in store.sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    user = store.users.get(store.sessions[session])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


CurrentUser = Depends(get_current_user)
