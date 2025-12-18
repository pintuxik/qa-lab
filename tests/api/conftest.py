"""
API-specific pytest fixtures for integration testing.

Shared fixtures (api_client, api_base_url, credentials) are inherited from
tests/conftest.py. This file contains only API-specific fixtures:
- User registration and authentication
- API client instances (AuthAPI, UsersAPI, TasksAPI)

Environment variables are loaded from .env.test by pytest-dotenv plugin.
"""

import allure
import pytest

from tests.api.clients import AuthAPIClient, TasksAPIClient, UsersAPIClient

# ============================================================================
# Credential Fixture - Alias for API tests
# ============================================================================


@pytest.fixture(scope="function")
def test_user_credentials(api_test_user_credentials):
    """Alias api_test_user_credentials for backward compatibility.

    API tests use the 'api_user_' prefix for test users.
    """
    return api_test_user_credentials


# ============================================================================
# User Registration and Authentication Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def registered_user(api_client, api_base_url, test_user_credentials):
    """Create and return a registered test user.

    Returns dict with credentials and user ID.
    Cleanup is handled by pytest_sessionfinish in root conftest.
    """
    with allure.step(f"Register test user: {test_user_credentials['username']}"):
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
def auth_token(api_client, api_base_url, registered_user) -> str:
    """Get JWT authentication token for registered user."""
    with allure.step(f"Login and get auth token: {registered_user['username']}"):
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
    """Provide an httpx client with Authorization header set."""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


# ============================================================================
# API Client Fixtures - Use these for clean, maintainable tests
# ============================================================================


@pytest.fixture(scope="function")
def auth_api(api_client, api_base_url) -> AuthAPIClient:
    """Provide AuthAPIClient for authentication tests.

    Example:
        def test_login(auth_api):
            response = auth_api.login("user", "password")
            response.assert_ok()
    """
    return AuthAPIClient(api_client, api_base_url)


@pytest.fixture(scope="function")
def users_api(api_client, api_base_url) -> UsersAPIClient:
    """Provide UsersAPIClient for user management tests.

    Example:
        def test_register(users_api):
            response = users_api.register("user", "email@test.com", "password")
            response.assert_created()
    """
    return UsersAPIClient(api_client, api_base_url)


@pytest.fixture(scope="function")
def tasks_api(api_client, api_base_url) -> TasksAPIClient:
    """Provide unauthenticated TasksAPIClient.

    Use this for testing auth requirements (expect 401 responses).

    Example:
        def test_tasks_require_auth(tasks_api):
            response = tasks_api.get_all_tasks()
            response.assert_unauthorized()
    """
    return TasksAPIClient(api_client, api_base_url)


@pytest.fixture(scope="function")
def authenticated_tasks_api(authenticated_client, api_base_url) -> TasksAPIClient:
    """Provide authenticated TasksAPIClient for task CRUD tests.

    Example:
        def test_create_task(authenticated_tasks_api):
            response = authenticated_tasks_api.create_task(title="My Task")
            response.assert_ok().assert_field_equals("title", "My Task")
    """
    return TasksAPIClient(authenticated_client, api_base_url)


@pytest.fixture(scope="function")
def authenticated_users_api(authenticated_client, api_base_url) -> UsersAPIClient:
    """Provide authenticated UsersAPIClient for protected user endpoints.

    Example:
        def test_get_current_user(authenticated_users_api):
            response = authenticated_users_api.get_current_user()
            response.assert_ok()
    """
    return UsersAPIClient(authenticated_client, api_base_url)
