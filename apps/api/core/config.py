from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Noesis API"
    ENVIRONMENT: str = "development"

    SUPABASE_URL: str = "https://placeholder.supabase.co"
    SUPABASE_ANON_KEY: str = "placeholder-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    DATABASE_URL: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
