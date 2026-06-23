import asyncio
import json
import random
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse

from ..models import ActiveGame, ErrorResponse, StartGameRequest, UpdateGameRequest
from ..security import CurrentUser
from ..store import UserRecord, store

router = APIRouter(prefix="/games", tags=["games"])

_CLOSE = object()  # sentinel that signals SSE generator to stop


def _now_ms() -> int:
    return int(time.time() * 1000)


def _game_json(game: dict) -> str:
    return ActiveGame(**game).model_dump_json()


def _broadcast_all() -> None:
    cutoff = _now_ms() - 30_000
    games = [
        json.loads(_game_json(g))
        for g in store.games.values()
        if g["updatedAt"] >= cutoff
    ]
    data = json.dumps(games)
    for q in store.all_games_queues:
        q.put_nowait(("games", data))


def _broadcast_game(game_id: str, game: dict | None) -> None:
    data = _game_json(game) if game is not None else "null"
    for q in store.game_queues.get(game_id, []):
        q.put_nowait(("game", data))
    if game is None:
        for q in store.game_queues.get(game_id, []):
            q.put_nowait(_CLOSE)


# ── SSE: all games ────────────────────────────────────────────────────────────
# MUST be defined before /{id} to prevent "events" matching as a path param.
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
async def list_active_games() -> list[ActiveGame]:
    cutoff = _now_ms() - 30_000
    return [
        ActiveGame(**g)
        for g in store.games.values()
        if g["updatedAt"] >= cutoff
    ]


# ── Start game ────────────────────────────────────────────────────────────────
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ActiveGame,
    responses={401: {"model": ErrorResponse}},
)
async def start_game(
    body: StartGameRequest,
    user: UserRecord = CurrentUser,
) -> ActiveGame:
    # Replace any existing game for this user
    existing = next(
        (gid for gid, g in store.games.items() if g["userId"] == user.id), None
    )
    if existing:
        del store.games[existing]
        store.game_queues.pop(existing, None)

    game_id = str(uuid.uuid4())
    gs = body.gridSize
    cx, cy = gs // 2, gs // 2
    snake = [
        {"x": cx,     "y": cy},
        {"x": cx - 1, "y": cy},
        {"x": cx - 2, "y": cy},
    ]
    snake_set = {(s["x"], s["y"]) for s in snake}
    while True:
        fx, fy = random.randint(0, gs - 1), random.randint(0, gs - 1)
        if (fx, fy) not in snake_set:
            break

    game: dict = {
        "id": game_id,
        "userId": user.id,
        "username": user.username,
        "mode": body.mode,
        "score": 0,
        "snake": snake,
        "food": {"x": fx, "y": fy},
        "gridSize": gs,
        "alive": True,
        "updatedAt": _now_ms(),
    }
    store.games[game_id] = game
    store.game_queues[game_id] = []

    _broadcast_all()
    return ActiveGame(**game)


# ── Get single game ───────────────────────────────────────────────────────────
@router.get(
    "/{id}",
    response_model=ActiveGame,
    responses={404: {"model": ErrorResponse}},
)
async def get_active_game(id: str) -> ActiveGame:
    game = store.games.get(id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return ActiveGame(**game)


# ── Update game (called every tick) ──────────────────────────────────────────
@router.put(
    "/{id}",
    response_model=ActiveGame,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def update_game(
    id: str,
    body: UpdateGameRequest,
    user: UserRecord = CurrentUser,
) -> ActiveGame:
    game = store.games.get(id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game["userId"] != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    game.update(
        {
            "mode": body.mode,
            "score": body.score,
            "snake": [p.model_dump() for p in body.snake],
            "food": body.food.model_dump(),
            "gridSize": body.gridSize,
            "alive": body.alive,
            "updatedAt": _now_ms(),
        }
    )

    _broadcast_all()
    _broadcast_game(id, game)
    return ActiveGame(**game)


# ── End game ──────────────────────────────────────────────────────────────────
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def end_game(
    id: str,
    user: UserRecord = CurrentUser,
) -> Response:
    game = store.games.get(id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game["userId"] != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    del store.games[id]
    _broadcast_all()
    _broadcast_game(id, None)
    store.game_queues.pop(id, None)
    return Response(status_code=204)


# ── SSE: single game ──────────────────────────────────────────────────────────
@router.get(
    "/{id}/events",
    responses={404: {"model": ErrorResponse}},
)
async def subscribe_active_game(id: str) -> StreamingResponse:
    if id not in store.games:
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
