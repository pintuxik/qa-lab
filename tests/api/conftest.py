"""
Global pytest configuration for API integration testing with Allure.
"""

import os

import allure
import pytest
import requests

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


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
    """Provide a requests session for API calls."""
    session = requests.Session()
    # Don't set default Content-Type - let requests handle it based on data type
    yield session
    session.close()


@pytest.fixture(scope="function")
def test_user_credentials():
    """Provide test user credentials."""
    import random
    import time

    # Use timestamp + random number for unique identifiers
    unique_id = f"{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
    return {
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@example.com",
        "password": "TestPass123!",
    }


@pytest.fixture(scope="function")
def registered_user(api_client, api_base_url, test_user_credentials):
    """Create and return a registered test user."""
    with allure.step("Register test user"):
        response = api_client.post(
            f"{api_base_url}/api/auth/register",
            json=test_user_credentials,
        )
        assert response.status_code == 200, f"Failed to register user: {response.text}"
        user_data = response.json()
        allure.attach(
            str(user_data),
            name="Registered User Data",
            attachment_type=allure.attachment_type.JSON,
        )
    return {**test_user_credentials, "id": user_data["id"]}


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


# Generate unique test ID for each test run
pytest.test_id = os.getpid()
