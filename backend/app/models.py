from enum import Enum
from pydantic import BaseModel, Field


class GameMode(str, Enum):
    walls = "walls"
    wrap = "wrap"


class Point(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)


class User(BaseModel):
    id: str
    username: str


class Score(BaseModel):
    id: str
    userId: str
    username: str
    mode: GameMode
    score: int = Field(ge=0)
    createdAt: int


class ActiveGame(BaseModel):
    id: str
    userId: str
    username: str
    mode: GameMode
    score: int = Field(ge=0)
    snake: list[Point]
    food: Point
    gridSize: int = Field(ge=5)
    alive: bool
    updatedAt: int


class ErrorResponse(BaseModel):
    message: str


# ── Request bodies ────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    username: str = Field(min_length=2)
    password: str = Field(min_length=4)


class LoginRequest(BaseModel):
    username: str
    password: str


class SubmitScoreRequest(BaseModel):
    mode: GameMode
    score: int = Field(ge=0)


class StartGameRequest(BaseModel):
    mode: GameMode
    gridSize: int = Field(ge=5)


class UpdateGameRequest(BaseModel):
    mode: GameMode
    score: int = Field(ge=0)
    snake: list[Point]
    food: Point
    gridSize: int = Field(ge=5)
    alive: bool
