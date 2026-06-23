"""
Full-flow integration tests against a real SQLite file database.
Each test exercises a complete user journey end-to-end via the HTTP API.
"""
from fastapi.testclient import TestClient


# ── helpers ───────────────────────────────────────────────────────────────────

def signup(client: TestClient, username: str, password: str) -> dict:
    r = client.post("/api/auth/signup", json={"username": username, "password": password})
    assert r.status_code == 201, r.text
    return r.json()


def login(client: TestClient, username: str, password: str) -> dict:
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return r.json()


# ── sign-up flow ──────────────────────────────────────────────────────────────

def test_signup_creates_authenticated_session(client: TestClient):
    user = signup(client, "alice", "alice1234")

    assert user["username"] == "alice"
    assert "id" in user

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["id"] == user["id"]
    assert me.json()["username"] == "alice"


def test_signup_then_unauthenticated_after_logout(client: TestClient):
    signup(client, "alice", "alice1234")
    client.post("/api/auth/logout")

    r = client.get("/api/auth/me")
    assert r.status_code == 401


# ── log-in flow ───────────────────────────────────────────────────────────────

def test_login_restores_session_after_logout(client: TestClient):
    original = signup(client, "bob", "bob12345")
    client.post("/api/auth/logout")

    assert client.get("/api/auth/me").status_code == 401

    logged_in = login(client, "bob", "bob12345")
    assert logged_in["id"] == original["id"]

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["username"] == "bob"


def test_login_wrong_password_rejected(client: TestClient):
    signup(client, "carol", "carol123")
    client.post("/api/auth/logout")

    r = client.post("/api/auth/login", json={"username": "carol", "password": "wrong"})
    assert r.status_code == 401
    assert client.get("/api/auth/me").status_code == 401


# ── score submission flow ─────────────────────────────────────────────────────

def test_submit_score_persists_to_leaderboard(client: TestClient):
    signup(client, "alice", "alice1234")

    r = client.post("/api/scores", json={"mode": "walls", "score": 250})
    assert r.status_code == 201
    entry = r.json()
    assert entry["score"] == 250
    assert entry["mode"] == "walls"
    assert entry["username"] == "alice"
    assert "id" in entry
    assert "createdAt" in entry

    board = client.get("/api/leaderboard?mode=walls").json()
    assert len(board) == 1
    assert board[0]["score"] == 250
    assert board[0]["username"] == "alice"


def test_score_isolated_to_correct_mode(client: TestClient):
    signup(client, "alice", "alice1234")
    client.post("/api/scores", json={"mode": "walls", "score": 100})
    client.post("/api/scores", json={"mode": "wrap", "score": 200})

    walls = client.get("/api/leaderboard?mode=walls").json()
    wrap = client.get("/api/leaderboard?mode=wrap").json()

    assert len(walls) == 1 and walls[0]["score"] == 100
    assert len(wrap) == 1 and wrap[0]["score"] == 200


# ── leaderboard read-back flow ────────────────────────────────────────────────

def test_leaderboard_orders_by_score_descending(client: TestClient):
    signup(client, "alice", "alice1234")
    for score in [10, 50, 30, 90, 20]:
        client.post("/api/scores", json={"mode": "walls", "score": score})

    board = client.get("/api/leaderboard?mode=walls").json()
    scores = [e["score"] for e in board]
    assert scores == sorted(scores, reverse=True)
    assert scores[0] == 90


def test_leaderboard_respects_limit(client: TestClient):
    signup(client, "alice", "alice1234")
    for score in [10, 20, 30, 40, 50]:
        client.post("/api/scores", json={"mode": "wrap", "score": score})

    board = client.get("/api/leaderboard?mode=wrap&limit=3").json()
    assert len(board) == 3
    assert board[0]["score"] == 50


def test_leaderboard_spans_multiple_users(client: TestClient):
    signup(client, "alice", "alice1234")
    client.post("/api/scores", json={"mode": "walls", "score": 300})
    client.post("/api/auth/logout")

    signup(client, "bob", "bob12345")
    client.post("/api/scores", json={"mode": "walls", "score": 500})

    board = client.get("/api/leaderboard?mode=walls").json()
    assert len(board) == 2
    assert board[0]["username"] == "bob"
    assert board[1]["username"] == "alice"


def test_full_flow_signup_login_score_leaderboard(client: TestClient):
    """End-to-end: two users compete, leaderboard reflects both."""
    signup(client, "alice", "alice1234")
    client.post("/api/scores", json={"mode": "walls", "score": 150})
    client.post("/api/auth/logout")

    signup(client, "bob", "bob12345")
    client.post("/api/scores", json={"mode": "walls", "score": 400})
    client.post("/api/auth/logout")

    # alice logs back in and submits a higher score
    login(client, "alice", "alice1234")
    client.post("/api/scores", json={"mode": "walls", "score": 600})

    board = client.get("/api/leaderboard?mode=walls").json()
    assert board[0]["username"] == "alice"
    assert board[0]["score"] == 600
    assert board[1]["username"] == "bob"
    assert board[1]["score"] == 400
    assert board[2]["username"] == "alice"
    assert board[2]["score"] == 150
