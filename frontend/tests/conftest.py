"""
Pytest configuration and fixtures for frontend tests.

Environment variables are loaded from .env.test by pytest-dotenv plugin.
See pyproject.toml [tool.pytest.ini_options] env_files setting.
"""

import os

import pytest
from app.main import create_app

TESTING = os.getenv("TESTING")
SECRET_KEY = os.getenv("SECRET_KEY")
WTF_CSRF_ENABLED = os.getenv("WTF_CSRF_ENABLED")


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = create_app()
    app.config.update(
        {
            "TESTING": TESTING,
            "SECRET_KEY": SECRET_KEY,
            "WTF_CSRF_ENABLED": WTF_CSRF_ENABLED,
        }
    )

    yield app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture
def authenticated_client(client):
    """Create a test client with an authenticated session."""
    with client.session_transaction() as session:
        session["access_token"] = "test_token_123"
        session["username"] = "testuser"
    return client
