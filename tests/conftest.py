"""
Root conftest for all tests - shared fixtures and pytest configuration.

This module contains fixtures and hooks used by both API and UI tests:
- Test failure detection hook (for screenshots/traces)
- Session cleanup hook (removes test users after all tests)
- Shared fixtures: api_base_url, api_client, credential generators
- Allure environment labeling

Environment variables are loaded from .env.test by pytest-dotenv plugin.
"""

import uuid

import allure
import httpx
import pytest

from tests.config import config

# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests",
    )
    config.addinivalue_line(
        "markers",
        "ui: marks tests as UI integration tests",
    )
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )


# ============================================================================
# Pytest Hooks - Shared across all test types
# ============================================================================


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test results for screenshot/trace on failure.

    Sets rep_call attribute on test item for use in fixtures.
    Used by both API (future) and UI (screenshot_on_failure, page trace).
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_sessionfinish(session, exitstatus):
    """
    Cleanup test users after all tests complete.

    This runs only on the master process (not xdist workers) to avoid
    race conditions where cleanup deletes users while tests are running.

    Cleans up both api_user_* and ui_user_* patterns.
    """
    # Skip cleanup if running in xdist worker process
    if hasattr(session.config, "workerinput"):
        return

    if not config.TEST_API_KEY:
        return

    # Clean up both API and UI test users
    patterns = ["api_user_*", "ui_user_*"]

    try:
        with httpx.Client(timeout=config.API_TIMEOUT) as client:
            response = client.post(
                f"{config.API_BASE_URL}/api/users/test-cleanup",
                json={"username_patterns": patterns},
                headers={"X-Test-API-Key": config.TEST_API_KEY},
            )
            if response.status_code != 200:
                print(f"Warning: Failed to cleanup test users: {response.text}")
    except Exception as e:
        # Log cleanup failure but don't fail the test run
        print(f"Warning: Failed to cleanup test users: {e}")


# ============================================================================
# Shared Fixtures - Used by both API and UI tests
# ============================================================================


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Provide the base URL for API requests."""
    return config.API_BASE_URL


@pytest.fixture(scope="function")
def api_client():
    """Provide an httpx client for API calls with global timeout.

    Uses httpx.Client (sync) for consistency with async backend.
    Default timeout from config (typically 10 seconds).
    """
    with httpx.Client(timeout=config.API_TIMEOUT) as client:
        yield client


def _generate_test_credentials(prefix: str) -> dict[str, str]:
    """Generate unique test user credentials with given prefix.

    Uses UUID for guaranteed uniqueness across parallel test execution.
    """
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"{prefix}_{unique_id}",
        "email": f"{prefix}_{unique_id}@example.com",
        "password": "TestPass123!",
    }


@pytest.fixture(scope="function")
def api_test_user_credentials() -> dict[str, str]:
    """Generate unique credentials for API tests (prefix: api_user)."""
    return _generate_test_credentials("api_user")


@pytest.fixture(scope="function")
def ui_test_user_credentials() -> dict[str, str]:
    """Generate unique credentials for UI tests (prefix: ui_user)."""
    return _generate_test_credentials("ui_user")


# ============================================================================
# Allure Integration - Environment labels
# ============================================================================


@pytest.fixture(autouse=True)
def allure_environment_info(request):
    """Add environment information to Allure report.

    Automatically detects test type from file path and adds appropriate labels.
    """
    allure.dynamic.label("framework", "pytest")

    # Detect test type from path and add appropriate labels
    test_path = str(request.fspath)
    if "/api/" in test_path:
        allure.dynamic.label("test_type", "api")
        allure.dynamic.label("api_base_url", config.API_BASE_URL)
    elif "/ui/" in test_path:
        allure.dynamic.label("test_type", "ui")
        allure.dynamic.label("browser", "chromium")
