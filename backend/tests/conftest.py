import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.store import store


@pytest.fixture(autouse=True)
def clean_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    store.reset()
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture
def alice() -> tuple[TestClient, dict]:
    c = TestClient(app, raise_server_exceptions=True)
    r = c.post("/api/auth/signup", json={"username": "alice", "password": "alice1234"})
    assert r.status_code == 201
    return c, r.json()


@pytest.fixture
def bob() -> tuple[TestClient, dict]:
    c = TestClient(app, raise_server_exceptions=True)
    r = c.post("/api/auth/signup", json={"username": "bob", "password": "bob12345"})
    assert r.status_code == 201
    return c, r.json()
