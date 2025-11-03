"""
Pytest configuration and fixtures for frontend tests.
"""

import pytest
from app.main import create_app


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing
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
