import os
from pathlib import Path


TEST_DB = Path(__file__).parent / "test_echo_trail.db"
os.environ["DATABASE_URL"] = "sqlite:///{}".format(TEST_DB)

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import engine
from app.main import app
from app.seed.run import seed_database


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    if TEST_DB.exists():
        TEST_DB.unlink()
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
    engine.dispose()
    if TEST_DB.exists():
        TEST_DB.unlink()


@pytest.fixture()
def client():
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers(client):
    response = client.post("/api/v1/sessions/anonymous")
    token = response.json()["data"]["access_token"]
    return {"Authorization": "Bearer {}".format(token)}

