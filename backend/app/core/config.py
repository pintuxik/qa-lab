from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/taskmanager"
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_URL: str = "http://localhost:5001"

    # Test mode settings
    TEST_MODE_ENABLED: bool = False
    TEST_API_KEY: str | None = None

    model_config = ConfigDict(env_file=".env")


settings = Settings()
