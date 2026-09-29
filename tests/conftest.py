import pytest
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
from jose import jwt

from apps.api.core.auth import get_current_user
from apps.api.core.config import settings
from apps.api.core.db import get_supabase
from apps.api.main import app
from tests.mock_supabase import MockSupabaseClient

bearer_scheme = HTTPBearer(auto_error=False)


@pytest.fixture
def mock_db():
    return MockSupabaseClient()


def override_get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: MockSupabaseClient = Depends(get_supabase),
):
    if credentials and credentials.credentials:
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            user_id = str(payload.get("sub"))
            res = db.table("users").select("*").eq("id", user_id).execute()
            if res.data:
                return res.data[0]
            return {
                "id": user_id,
                "email": payload.get("email", "user@example.com"),
                "username": payload.get("username", "testuser"),
            }
        except Exception:
            pass

    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "test@example.com",
        "username": "testuser",
    }


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_supabase] = lambda: mock_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
