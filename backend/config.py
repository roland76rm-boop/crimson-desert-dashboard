from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/crimson_desert"
    api_key: str = "dev-key-change-me"
    cors_origins: str = "http://localhost:5173,https://crimsondesert.haus543.at"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
