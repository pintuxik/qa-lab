"""
Centralized test configuration.

Environment variables are loaded from .env.test by pytest-dotenv plugin.
See pyproject.toml [tool.pytest.ini_options] env_files setting.
"""

import os


class TestConfig:
    """Test environment configuration loaded from environment variables."""

    # API Configuration
    API_BASE_URL: str = os.getenv("API_BASE_URL")
    API_TIMEOUT: float = float(os.getenv("API_TIMEOUT"))
    TEST_API_KEY: str = os.getenv("TEST_API_KEY")

    # Frontend Configuration
    FRONTEND_URL: str = os.getenv("FRONTEND_URL")

    # Playwright Configuration
    HEADLESS: bool = os.getenv("HEADLESS").lower() == "true"
    SLOW_MO: float = float(os.getenv("SLOW_MO"))


config = TestConfig()
