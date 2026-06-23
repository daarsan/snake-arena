import os

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, JSON, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./snake_arena.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class DbUser(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)


class DbSession(Base):
    __tablename__ = "sessions"

    token = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)


class DbScore(Base):
    __tablename__ = "scores"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    username = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(BigInteger, nullable=False)  # ms epoch


class DbGame(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    username = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    score = Column(Integer, nullable=False, default=0)
    snake = Column(JSON, nullable=False)   # list[{"x": int, "y": int}]
    food = Column(JSON, nullable=False)    # {"x": int, "y": int}
    grid_size = Column(Integer, nullable=False)
    alive = Column(Boolean, nullable=False, default=True)
    updated_at = Column(BigInteger, nullable=False)  # ms epoch


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(engine)


def game_to_dict(g: DbGame) -> dict:
    return {
        "id": g.id,
        "userId": g.user_id,
        "username": g.username,
        "mode": g.mode,
        "score": g.score,
        "snake": g.snake,
        "food": g.food,
        "gridSize": g.grid_size,
        "alive": g.alive,
        "updatedAt": g.updated_at,
    }


def score_to_dict(s: DbScore) -> dict:
    return {
        "id": s.id,
        "userId": s.user_id,
        "username": s.username,
        "mode": s.mode,
        "score": s.score,
        "createdAt": s.created_at,
    }
