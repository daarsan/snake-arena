# Snake Arena

A multiplayer snake game where players can compete and spectate each other's games in real time.

## Quick start

```bash
make install   # install all deps (backend + frontend)
make dev       # start both servers — Ctrl-C stops both
```

The backend starts on **http://localhost:8000** and the frontend on the port shown in the terminal.

## Running individually

```bash
make backend      # FastAPI on :8000 with hot-reload
make frontend     # Vite dev server (port shown in terminal)
```

## Tests

```bash
make test            # backend (pytest)
make test-frontend   # frontend (vitest)
```

## Project structure

```
snake-arena/
  backend/        FastAPI app — see backend/README.md
  frontend/       TanStack Start + Vite app
  openapi.yaml    REST API contract (source of truth)
  Makefile        Common dev tasks
```

## API

The full API contract is in [`openapi.yaml`](./openapi.yaml). The backend serves everything under `/api`:

| Tag    | Endpoints |
|--------|-----------|
| auth   | `POST /api/auth/signup`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me` |
| scores | `POST /api/scores`, `GET /api/leaderboard?mode=walls\|wrap` |
| games  | `GET/POST /api/games`, `GET/PUT/DELETE /api/games/{id}` |
| SSE    | `GET /api/games/events`, `GET /api/games/{id}/events` |

Authentication uses an HttpOnly session cookie (`session`) issued on login/signup.
