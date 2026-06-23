# Snake Arena — Backend

FastAPI REST API implementing [`openapi.yaml`](../openapi.yaml). Uses an in-memory store (no database).

## Running

```bash
uv sync                                            # install deps
uv run uvicorn app.main:app --reload --port 8000   # dev server with hot-reload
```

Or from the project root:

```bash
make backend
```

On startup the server seeds the store with three users (`alice`, `bob`, `carol`) and sample scores and active games so the frontend has something to display immediately.

## Testing

```bash
uv run pytest tests/ -v
```

## Module overview

| File | Purpose |
|------|---------|
| `app/main.py` | App factory, CORS, lifespan (seed), `{"message"}` error handler |
| `app/models.py` | Pydantic request/response models |
| `app/store.py` | In-memory singleton: users, sessions, scores, games, SSE queues |
| `app/security.py` | bcrypt password hashing, session tokens, `get_current_user` dependency |
| `app/seed.py` | Seed data |
| `app/routers/auth.py` | `/api/auth/*` |
| `app/routers/scores.py` | `/api/scores`, `/api/leaderboard` |
| `app/routers/games.py` | `/api/games/*` + SSE streams |

## Seed credentials

| Username | Password   |
|----------|------------|
| alice    | alice1234  |
| bob      | bob12345   |
| carol    | carol123   |

## Dependencies

Runtime: `fastapi`, `uvicorn[standard]`, `bcrypt`

Dev: `pytest`, `pytest-asyncio`, `anyio`, `httpx2`
