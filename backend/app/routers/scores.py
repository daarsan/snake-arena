import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..models import ErrorResponse, GameMode, Score, SubmitScoreRequest
from ..security import CurrentUser
from ..store import UserRecord, store

router = APIRouter(tags=["scores"])


def _now_ms() -> int:
    return int(time.time() * 1000)


@router.post(
    "/scores",
    status_code=status.HTTP_201_CREATED,
    response_model=Score,
    responses={401: {"model": ErrorResponse}},
)
async def submit_score(
    body: SubmitScoreRequest,
    user: UserRecord = CurrentUser,
) -> Score:
    entry = {
        "id": str(uuid.uuid4()),
        "userId": user.id,
        "username": user.username,
        "mode": body.mode,
        "score": body.score,
        "createdAt": _now_ms(),
    }
    store.scores.append(entry)
    return Score(**entry)


@router.get("/leaderboard", response_model=list[Score])
async def get_leaderboard(
    mode: GameMode,
    limit: int = Query(default=10, ge=1, le=100),
) -> list[Score]:
    filtered = [s for s in store.scores if s["mode"] == mode]
    filtered.sort(key=lambda s: s["score"], reverse=True)
    return [Score(**s) for s in filtered[:limit]]
