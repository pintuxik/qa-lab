from pydantic import ConfigDict, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database components (used to construct DATABASE_URL if not provided)
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # Database connection URL - can be set directly or constructed from DB_* components
    DATABASE_URL: str | None = None

    # Application secrets - MUST be configured
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    FRONTEND_URL: str

    # Test mode settings
    TEST_MODE_ENABLED: bool = False
    TEST_API_KEY: str | None = None

    model_config = ConfigDict()

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        """Construct DATABASE_URL from components if not explicitly provided."""
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return self


settings = Settings()
