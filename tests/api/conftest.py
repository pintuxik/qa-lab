"""
Global pytest configuration for API integration testing with Allure.
"""

import os

import allure
import httpx
import pytest

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_API_KEY = os.getenv("TEST_API_KEY", "your-super-secret-key-change-in-production")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for screenshot on failure."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def allure_environment_info():
    """Add environment information to Allure report."""
    allure.dynamic.label("framework", "pytest")
    allure.dynamic.label("test_type", "api")
    allure.dynamic.label("api_base_url", API_BASE_URL)


@pytest.fixture(scope="session")
def api_base_url():
    """Provide the base URL for API requests."""
    return API_BASE_URL


def pytest_sessionfinish(session, exitstatus):
    """
    Hook called after all tests complete (including all xdist workers).

    This ensures cleanup happens only once after all parallel workers finish,
    avoiding race conditions where cleanup deletes users while tests are running.
    """
    # Skip cleanup if running in xdist worker process
    # Only the master process (or non-xdist runs) should do cleanup
    if hasattr(session.config, "workerinput"):
        return

    # Cleanup: Delete test users using secure test-cleanup endpoint
    if TEST_API_KEY:
        try:
            api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
            with httpx.Client() as api_client:
                response = api_client.post(
                    f"{api_base_url}/api/users/test-cleanup",
                    json={"username_patterns": ["api_user_*"]},
                    headers={"X-Test-API-Key": TEST_API_KEY},
                )
                if response.status_code != 200:
                    print(f"Warning: Failed to cleanup users: {response.text}")
        except Exception as e:
            # Log cleanup failure but don't fail the test run
            print(f"Warning: Failed to cleanup users by pattern 'api_user_*': {str(e)}")


@pytest.fixture(scope="function")
def api_client(api_base_url):
    """Provide an httpx client for API calls with global timeout.

    Uses httpx.Client (sync) for consistency with async backend.
    Benefits over requests:
    - Better HTTP/2 support
    - More modern API
    - Consistent with httpx.AsyncClient if we go async later

    Default timeout of 10 seconds per repo standards.
    Can be overridden per request by passing timeout parameter.
    """
    # httpx.Client with default timeout
    with httpx.Client(timeout=10.0) as client:
        yield client


@pytest.fixture(scope="function")
def test_user_credentials():
    """Provide truly unique test user credentials per test."""
    import uuid

    # Use UUID for guaranteed uniqueness across all contexts (parallel, sequential, etc.)
    unique_id = str(uuid.uuid4())[:8]  # First 8 chars of UUID
    return {
        "username": f"api_user_{unique_id}",
        "email": f"api_user_{unique_id}@example.com",
        "password": "TestPass123!",
    }


@pytest.fixture(scope="function")
def registered_user(api_client, api_base_url, test_user_credentials):
    """Create and return a registered test user. Cleans up after test completes."""
    with allure.step("Register test user"):
        response = api_client.post(
            f"{api_base_url}/api/users/",
            json=test_user_credentials,
        )
        assert response.status_code == 201, f"Failed to register user: {response.text}"
        user_data = response.json()
        allure.attach(
            str(user_data),
            name="Registered User Data",
            attachment_type=allure.attachment_type.JSON,
        )

    yield {**test_user_credentials, "id": user_data["id"]}


@pytest.fixture(scope="function")
def auth_token(api_client, api_base_url, registered_user):
    """Get authentication token for registered user."""
    with allure.step("Login and get auth token"):
        response = api_client.post(
            f"{api_base_url}/api/auth/login",
            data={
                "username": registered_user["username"],
                "password": registered_user["password"],
            },
        )
        assert response.status_code == 200, f"Failed to login: {response.text}"
        token_data = response.json()
        allure.attach(
            str(token_data),
            name="Auth Token Response",
            attachment_type=allure.attachment_type.JSON,
        )
    return token_data["access_token"]


@pytest.fixture(scope="function")
def authenticated_client(api_client, auth_token):
    """Provide an authenticated API client."""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client
