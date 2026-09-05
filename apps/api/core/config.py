from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Noesis API"
    SUPABASE_URL: str = "http://localhost:8000"
    SUPABASE_KEY: str = "anon-key"
    REDIS_URL: str = "redis://localhost:6379/0"
    GEMINI_API_KEY: str = "test-key"
    MAX_LLM_RETRIES: int = 2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings():
    return Settings()
