import pytest
from fastapi.testclient import TestClient

from apps.api.core.db import get_supabase
from apps.api.main import app
from tests.mock_supabase import MockSupabaseClient


@pytest.fixture
def mock_db():
    return MockSupabaseClient()


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_supabase] = lambda: mock_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
