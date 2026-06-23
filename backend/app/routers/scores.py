import time
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import DbScore, get_db, score_to_dict
from ..models import ErrorResponse, GameMode, Score, SubmitScoreRequest
from ..security import CurrentUser, DbUser

router = APIRouter(tags=["scores"])


def _now_ms() -> int:
    return int(time.time() * 1000)


@router.post(
    "/scores",
    status_code=201,
    response_model=Score,
    responses={401: {"model": ErrorResponse}},
)
async def submit_score(
    body: SubmitScoreRequest,
    user: DbUser = CurrentUser,
    db: Session = Depends(get_db),
) -> Score:
    row = DbScore(
        id=str(uuid.uuid4()),
        user_id=user.id,
        username=user.username,
        mode=body.mode,
        score=body.score,
        created_at=_now_ms(),
    )
    db.add(row)
    db.commit()
    return Score(**score_to_dict(row))


@router.get("/leaderboard", response_model=list[Score])
async def get_leaderboard(
    mode: GameMode,
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[Score]:
    rows = (
        db.query(DbScore)
        .filter_by(mode=mode)
        .order_by(DbScore.score.desc())
        .limit(limit)
        .all()
    )
    return [Score(**score_to_dict(r)) for r in rows]
