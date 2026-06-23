from fastapi.testclient import TestClient


def test_signup_creates_user(client: TestClient):
    r = client.post("/api/auth/signup", json={"username": "alice", "password": "pass1234"})
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "alice"
    assert "id" in data
    assert "session" in r.cookies


def test_signup_duplicate_username(client: TestClient):
    client.post("/api/auth/signup", json={"username": "alice", "password": "pass1234"})
    r = client.post("/api/auth/signup", json={"username": "alice", "password": "other123"})
    assert r.status_code == 409
    assert "message" in r.json()


def test_signup_short_username(client: TestClient):
    r = client.post("/api/auth/signup", json={"username": "x", "password": "pass1234"})
    assert r.status_code == 422


def test_signup_short_password(client: TestClient):
    r = client.post("/api/auth/signup", json={"username": "alice", "password": "pw"})
    assert r.status_code == 422


def test_login_success(client: TestClient):
    client.post("/api/auth/signup", json={"username": "alice", "password": "pass1234"})
    client.cookies.clear()
    r = client.post("/api/auth/login", json={"username": "alice", "password": "pass1234"})
    assert r.status_code == 200
    assert r.json()["username"] == "alice"
    assert "session" in r.cookies


def test_login_wrong_password(client: TestClient):
    client.post("/api/auth/signup", json={"username": "alice", "password": "pass1234"})
    client.cookies.clear()
    r = client.post("/api/auth/login", json={"username": "alice", "password": "wrong"})
    assert r.status_code == 401


def test_login_unknown_user(client: TestClient):
    r = client.post("/api/auth/login", json={"username": "nobody", "password": "pass1234"})
    assert r.status_code == 401


def test_me_authenticated(alice: tuple):
    client, user = alice
    r = client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["username"] == "alice"


def test_me_unauthenticated(client: TestClient):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_logout_clears_session(alice: tuple):
    client, _ = alice
    r = client.post("/api/auth/logout")
    assert r.status_code == 204
    r2 = client.get("/api/auth/me")
    assert r2.status_code == 401
