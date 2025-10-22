from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://shinobi:shinobi@localhost:5432/shinobi"
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_URL: str = "redis://localhost:6379"
    RECORDINGS_PATH: str = "/var/shinobi/recordings"
    STREAM_PATH: str = "/var/shinobi/streams"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
