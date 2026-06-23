from fastapi.testclient import TestClient

from app.main import app


def test_submit_score_authenticated(alice: tuple):
    client, _ = alice
    r = client.post("/api/scores", json={"mode": "walls", "score": 150})
    assert r.status_code == 201
    data = r.json()
    assert data["score"] == 150
    assert data["mode"] == "walls"
    assert data["username"] == "alice"
    assert "id" in data
    assert "createdAt" in data


def test_submit_score_unauthenticated(client: TestClient):
    r = client.post("/api/scores", json={"mode": "walls", "score": 100})
    assert r.status_code == 401


def test_leaderboard_walls(alice: tuple, bob: tuple):
    alice_client, _ = alice
    bob_client, _ = bob

    alice_client.post("/api/scores", json={"mode": "walls", "score": 300})
    bob_client.post("/api/scores", json={"mode": "walls", "score": 500})

    r = alice_client.get("/api/leaderboard?mode=walls")
    assert r.status_code == 200
    scores = r.json()
    assert len(scores) == 2
    assert scores[0]["score"] >= scores[1]["score"]


def test_leaderboard_wrap_separate(alice: tuple):
    client, _ = alice
    client.post("/api/scores", json={"mode": "walls", "score": 100})
    client.post("/api/scores", json={"mode": "wrap", "score": 200})

    assert len(client.get("/api/leaderboard?mode=walls").json()) == 1
    assert len(client.get("/api/leaderboard?mode=wrap").json()) == 1
    assert client.get("/api/leaderboard?mode=wrap").json()[0]["score"] == 200


def test_leaderboard_limit(alice: tuple):
    client, _ = alice
    for s in [10, 20, 30, 40, 50]:
        client.post("/api/scores", json={"mode": "walls", "score": s})

    r = client.get("/api/leaderboard?mode=walls&limit=3")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3
    assert data[0]["score"] == 50


def test_leaderboard_sorted_desc(alice: tuple):
    client, _ = alice
    for s in [10, 50, 30]:
        client.post("/api/scores", json={"mode": "wrap", "score": s})

    scores = [s["score"] for s in client.get("/api/leaderboard?mode=wrap").json()]
    assert scores == sorted(scores, reverse=True)


def test_leaderboard_no_auth_required(client: TestClient):
    r = client.get("/api/leaderboard?mode=walls")
    assert r.status_code == 200
    assert r.json() == []


def test_leaderboard_invalid_mode(client: TestClient):
    r = client.get("/api/leaderboard?mode=invalid")
    assert r.status_code == 422
