# Backend

FastAPI app in `backend/`. Uses `uv` for dependency management.

## Useful commands

```bash
uv sync                        # install deps (incl. dev)
uv add <PACKAGE>               # add runtime dep
uv add --dev <PACKAGE>         # add dev-only dep
uv run uvicorn app.main:app --reload   # start dev server on :8000
uv run pytest tests/ -v        # run tests
```

Do not add `from __future__ import annotations`.

## Module structure

```
backend/
  app/
    main.py       # FastAPI app, CORS, lifespan (seeds store), custom error handler
    models.py     # Pydantic models and request bodies
    store.py      # In-memory singleton: users, sessions, scores, games, SSE queues
    security.py   # bcrypt helpers, session tokens, get_current_user dependency
    seed.py       # Seed data: alice/bob/carol with scores and two live games
    routers/
      auth.py     # POST /auth/signup|login|logout, GET /auth/me
      scores.py   # POST /scores, GET /leaderboard
      games.py    # GET|POST /games, GET|PUT|DELETE /games/{id}, SSE endpoints
  tests/
    conftest.py   # clean_store (autouse), client, alice, bob fixtures
    test_auth.py
    test_scores.py
    test_games.py
```

## Key conventions

- All routes are mounted under `/api` (matches openapi.yaml `servers.url`).
- Auth uses an HttpOnly session cookie named `session` (cookie value is a random token stored in `store.sessions`).
- Error responses always use `{"message": "..."}` (custom HTTPException handler in main.py maps FastAPI's `detail` field).
- The store is a module-level singleton; call `store.reset()` in tests to get a clean state.
- `alice` and `bob` test fixtures each own their own `TestClient` so session cookies don't collide.
- SSE routes (`/games/events`, `/games/{id}/events`) must be declared before `/{id}` in the router to prevent the literal `events` being matched as a path parameter.

## Regularly commit code to git