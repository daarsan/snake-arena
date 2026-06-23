import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import store


@pytest.fixture(autouse=True)
def clean_store():
    store.reset()
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture
def alice() -> tuple[TestClient, dict]:
    """Fresh client already signed up as alice."""
    c = TestClient(app, raise_server_exceptions=True)
    r = c.post("/api/auth/signup", json={"username": "alice", "password": "alice1234"})
    assert r.status_code == 201
    return c, r.json()


@pytest.fixture
def bob() -> tuple[TestClient, dict]:
    """Fresh client already signed up as bob."""
    c = TestClient(app, raise_server_exceptions=True)
    r = c.post("/api/auth/signup", json={"username": "bob", "password": "bob12345"})
    assert r.status_code == 201
    return c, r.json()
