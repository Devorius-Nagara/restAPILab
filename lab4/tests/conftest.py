import asyncio

# Patch connect/close/get_database BEFORE importing main
import database

async def _noop():
    pass

database.connect_db = _noop
database.close_db = _noop

# In-memory MongoDB via mongomock_motor
from mongomock_motor import AsyncMongoMockClient

_test_client = AsyncMongoMockClient()
_test_db = _test_client["test_library"]


async def _get_test_database():
    return _test_db


# Patch the module-level function so _seed() in main.py uses the test DB
database.get_database = _get_test_database

import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_database


app.dependency_overrides[get_database] = _get_test_database


@pytest.fixture(scope="session", autouse=True)
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clean_db(client):
    yield
    asyncio.run(_wipe())


async def _wipe():
    await _test_db["books"].delete_many({})
