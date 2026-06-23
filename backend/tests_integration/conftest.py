import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.store import store


@pytest.fixture
def client(tmp_path) -> TestClient:
    """TestClient backed by a temporary SQLite file — discarded after each test."""
    db_url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
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

    yield TestClient(app, raise_server_exceptions=True)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()
