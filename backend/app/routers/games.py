import asyncio
import json
import random
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import DbGame, DbUser, game_to_dict, get_db
from ..models import ActiveGame, ErrorResponse, StartGameRequest, UpdateGameRequest
from ..security import CurrentUser
from ..store import store

router = APIRouter(prefix="/games", tags=["games"])

_CLOSE = object()


def _now_ms() -> int:
    return int(time.time() * 1000)


def _serialize_games(db: Session) -> str:
    cutoff = _now_ms() - 30_000
    rows = db.query(DbGame).filter(DbGame.updated_at >= cutoff).all()
    return json.dumps([json.loads(ActiveGame(**game_to_dict(r)).model_dump_json()) for r in rows])


def _serialize_game(row: DbGame) -> str:
    return ActiveGame(**game_to_dict(row)).model_dump_json()


def _broadcast_all(db: Session) -> None:
    data = _serialize_games(db)
    for q in store.all_games_queues:
        q.put_nowait(("games", data))


def _broadcast_game(game_id: str, row: DbGame | None) -> None:
    data = _serialize_game(row) if row is not None else "null"
    for q in store.game_queues.get(game_id, []):
        q.put_nowait(("game", data))
    if row is None:
        for q in store.game_queues.get(game_id, []):
            q.put_nowait(_CLOSE)


# ── SSE: all games — must be declared before /{id} ───────────────────────────
@router.get("/events")
async def subscribe_active_games() -> StreamingResponse:
    queue: asyncio.Queue = asyncio.Queue()
    store.all_games_queues.append(queue)

    async def generate():
        try:
            while True:
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=15)
                    if item is _CLOSE:
                        break
                    event, data = item
                    yield f"event: {event}\ndata: {data}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            try:
                store.all_games_queues.remove(queue)
            except ValueError:
                pass

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── List active games ─────────────────────────────────────────────────────────
@router.get("", response_model=list[ActiveGame])
async def list_active_games(db: Session = Depends(get_db)) -> list[ActiveGame]:
    cutoff = _now_ms() - 30_000
    rows = db.query(DbGame).filter(DbGame.updated_at >= cutoff).all()
    return [ActiveGame(**game_to_dict(r)) for r in rows]


# ── Start game ────────────────────────────────────────────────────────────────
@router.post("", status_code=status.HTTP_201_CREATED, response_model=ActiveGame,
             responses={401: {"model": ErrorResponse}})
async def start_game(
    body: StartGameRequest,
    user: DbUser = CurrentUser,
    db: Session = Depends(get_db),
) -> ActiveGame:
    existing = db.query(DbGame).filter_by(user_id=user.id).first()
    if existing:
        store.game_queues.pop(existing.id, None)
        db.delete(existing)

    gs = body.gridSize
    cx, cy = gs // 2, gs // 2
    snake = [{"x": cx, "y": cy}, {"x": cx - 1, "y": cy}, {"x": cx - 2, "y": cy}]
    snake_set = {(s["x"], s["y"]) for s in snake}
    while True:
        fx, fy = random.randint(0, gs - 1), random.randint(0, gs - 1)
        if (fx, fy) not in snake_set:
            break

    row = DbGame(
        id=str(uuid.uuid4()),
        user_id=user.id,
        username=user.username,
        mode=body.mode,
        score=0,
        snake=snake,
        food={"x": fx, "y": fy},
        grid_size=gs,
        alive=True,
        updated_at=_now_ms(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    store.game_queues[row.id] = []
    _broadcast_all(db)
    return ActiveGame(**game_to_dict(row))


# ── Get single game ───────────────────────────────────────────────────────────
@router.get("/{id}", response_model=ActiveGame, responses={404: {"model": ErrorResponse}})
async def get_active_game(id: str, db: Session = Depends(get_db)) -> ActiveGame:
    row = db.query(DbGame).filter_by(id=id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Game not found")
    return ActiveGame(**game_to_dict(row))


# ── Update game ───────────────────────────────────────────────────────────────
@router.put("/{id}", response_model=ActiveGame,
            responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
async def update_game(
    id: str,
    body: UpdateGameRequest,
    user: DbUser = CurrentUser,
    db: Session = Depends(get_db),
) -> ActiveGame:
    row = db.query(DbGame).filter_by(id=id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Game not found")
    if row.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    row.mode = body.mode
    row.score = body.score
    row.snake = [p.model_dump() for p in body.snake]
    row.food = body.food.model_dump()
    row.grid_size = body.gridSize
    row.alive = body.alive
    row.updated_at = _now_ms()
    db.commit()
    db.refresh(row)

    _broadcast_all(db)
    _broadcast_game(id, row)
    return ActiveGame(**game_to_dict(row))


# ── End game ──────────────────────────────────────────────────────────────────
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT,
               responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
async def end_game(
    id: str,
    user: DbUser = CurrentUser,
    db: Session = Depends(get_db),
) -> Response:
    row = db.query(DbGame).filter_by(id=id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Game not found")
    if row.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(row)
    db.commit()

    _broadcast_all(db)
    _broadcast_game(id, None)
    store.game_queues.pop(id, None)
    return Response(status_code=204)


# ── SSE: single game ──────────────────────────────────────────────────────────
@router.get("/{id}/events", responses={404: {"model": ErrorResponse}})
async def subscribe_active_game(id: str, db: Session = Depends(get_db)) -> StreamingResponse:
    if not db.query(DbGame).filter_by(id=id).first():
        raise HTTPException(status_code=404, detail="Game not found")

    queue: asyncio.Queue = asyncio.Queue()
    store.game_queues.setdefault(id, []).append(queue)

    async def generate():
        try:
            while True:
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=15)
                    if item is _CLOSE:
                        break
                    event, data = item
                    yield f"event: {event}\ndata: {data}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            try:
                store.game_queues.get(id, []).remove(queue)
            except ValueError:
                pass

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
