import pytest
from unittest.mock import MagicMock, AsyncMock
import json
from uuid import uuid4

@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    mock_supabase = MagicMock()
    mock_redis = AsyncMock()
    
    # Simple mock implementations for endpoints
    monkeypatch.setattr("apps.api.routes.generation.get_supabase", lambda: mock_supabase)
    monkeypatch.setattr("apps.api.routes.generation.get_redis", AsyncMock(return_value=mock_redis))
    monkeypatch.setattr("apps.api.routes.quizzes.get_supabase", lambda: mock_supabase)
    monkeypatch.setattr("apps.api.services.quiz.get_supabase", lambda: mock_supabase)
    monkeypatch.setattr("apps.api.routes.progress.get_supabase", lambda: mock_supabase)
    monkeypatch.setattr("apps.api.services.generation.get_supabase", lambda: mock_supabase)
    
    return mock_supabase, mock_redis
