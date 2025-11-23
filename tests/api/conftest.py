"""
Global pytest configuration for API integration testing with Allure.
"""

import os

import allure
import pytest
import requests

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


@pytest.fixture(scope="function")
def api_client(api_base_url):
    """Provide a requests session for API calls with global timeout.

    Default timeout of 10 seconds per repo standards.
    Can be overridden per request by passing timeout parameter.
    """
    session = requests.Session()
    # Don't set default Content-Type - let requests handle it based on data type

    # Monkey-patch request methods to apply default timeout (10 seconds)
    original_request = session.request

    def request_with_timeout(method, url, **kwargs):
        # Only set timeout if not already specified
        if "timeout" not in kwargs:
            kwargs["timeout"] = 10  # 10 seconds
        return original_request(method, url, **kwargs)

    session.request = request_with_timeout

    yield session
    session.close()


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

    user_info = {**test_user_credentials, "id": user_data["id"]}
    yield user_info

    # Cleanup: Delete test user using secure test-cleanup endpoint
    if TEST_API_KEY:
        with allure.step("Cleanup test user via test-cleanup endpoint"):
            try:
                response = api_client.post(
                    f"{api_base_url}/api/users/test-cleanup",
                    json={"user_ids": [user_info["id"]]},
                    headers={"X-Test-API-Key": TEST_API_KEY},
                )
                assert response.status_code == 200, f"Failed to cleanup user: {response.text}"
                allure.attach(
                    f"Deleted user: {user_info['username']} (ID: {user_info['id']})",
                    name="Test User Cleanup",
                    attachment_type=allure.attachment_type.TEXT,
                )
            except Exception as e:
                # Log cleanup failure but don't fail the test
                allure.attach(
                    f"Failed to cleanup user {user_info['username']}: {str(e)}",
                    name="Cleanup Warning",
                    attachment_type=allure.attachment_type.TEXT,
                )


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
