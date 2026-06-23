from fastapi.testclient import TestClient

from app.main import app

GAME_BODY = {"mode": "walls", "gridSize": 20}

UPDATE_BODY = {
    "mode": "walls",
    "score": 10,
    "snake": [{"x": 10, "y": 10}, {"x": 9, "y": 10}],
    "food": {"x": 5, "y": 5},
    "gridSize": 20,
    "alive": True,
}


def _start(client: TestClient, body: dict = GAME_BODY) -> dict:
    r = client.post("/api/games", json=body)
    assert r.status_code == 201
    return r.json()


# ── list ──────────────────────────────────────────────────────────────────────

def test_list_games_empty(client: TestClient):
    r = client.get("/api/games")
    assert r.status_code == 200
    assert r.json() == []


def test_list_games_shows_active(alice: tuple):
    client, _ = alice
    _start(client)
    r = client.get("/api/games")
    assert len(r.json()) == 1


def test_list_no_auth_required(alice: tuple):
    alice_client, _ = alice
    _start(alice_client)

    anon = TestClient(app)
    r = anon.get("/api/games")
    assert r.status_code == 200
    assert len(r.json()) == 1


# ── start ─────────────────────────────────────────────────────────────────────

def test_start_game_requires_auth(client: TestClient):
    r = client.post("/api/games", json=GAME_BODY)
    assert r.status_code == 401


def test_start_game_returns_active_game(alice: tuple):
    client, user = alice
    game = _start(client)
    assert game["userId"] == user["id"]
    assert game["username"] == "alice"
    assert game["mode"] == "walls"
    assert game["gridSize"] == 20
    assert game["alive"] is True
    assert game["score"] == 0
    assert len(game["snake"]) >= 1
    assert "food" in game
    assert "id" in game


def test_start_game_replaces_existing(alice: tuple):
    client, _ = alice
    g1 = _start(client)
    g2 = _start(client)
    assert g1["id"] != g2["id"]
    assert client.get(f"/api/games/{g1['id']}").status_code == 404


def test_start_game_wrap_mode(alice: tuple):
    client, _ = alice
    game = _start(client, {"mode": "wrap", "gridSize": 15})
    assert game["mode"] == "wrap"
    assert game["gridSize"] == 15


# ── get ───────────────────────────────────────────────────────────────────────

def test_get_game_found(alice: tuple):
    client, _ = alice
    game = _start(client)
    r = client.get(f"/api/games/{game['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == game["id"]


def test_get_game_not_found(client: TestClient):
    r = client.get("/api/games/nonexistent")
    assert r.status_code == 404


# ── update ────────────────────────────────────────────────────────────────────

def test_update_game(alice: tuple):
    client, _ = alice
    game = _start(client)
    r = client.put(f"/api/games/{game['id']}", json=UPDATE_BODY)
    assert r.status_code == 200
    data = r.json()
    assert data["score"] == 10
    assert data["snake"] == UPDATE_BODY["snake"]
    assert data["food"] == UPDATE_BODY["food"]


def test_update_game_requires_auth(alice: tuple):
    alice_client, _ = alice
    game = _start(alice_client)

    anon = TestClient(app)
    r = anon.put(f"/api/games/{game['id']}", json=UPDATE_BODY)
    assert r.status_code == 401


def test_update_game_wrong_owner(alice: tuple, bob: tuple):
    alice_client, _ = alice
    bob_client, _ = bob
    game = _start(alice_client)

    r = bob_client.put(f"/api/games/{game['id']}", json=UPDATE_BODY)
    assert r.status_code == 403


def test_update_game_not_found(alice: tuple):
    client, _ = alice
    r = client.put("/api/games/nonexistent", json=UPDATE_BODY)
    assert r.status_code == 404


# ── delete ────────────────────────────────────────────────────────────────────

def test_end_game(alice: tuple):
    client, _ = alice
    game = _start(client)
    r = client.delete(f"/api/games/{game['id']}")
    assert r.status_code == 204
    assert client.get(f"/api/games/{game['id']}").status_code == 404


def test_end_game_requires_auth(alice: tuple):
    alice_client, _ = alice
    game = _start(alice_client)

    anon = TestClient(app)
    r = anon.delete(f"/api/games/{game['id']}")
    assert r.status_code == 401


def test_end_game_wrong_owner(alice: tuple, bob: tuple):
    alice_client, _ = alice
    bob_client, _ = bob
    game = _start(alice_client)

    r = bob_client.delete(f"/api/games/{game['id']}")
    assert r.status_code == 403


def test_end_game_not_found(alice: tuple):
    client, _ = alice
    r = client.delete("/api/games/nonexistent")
    assert r.status_code == 404
