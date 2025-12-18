"""
Integration tests for Authentication API endpoints.

Uses API client abstraction for clean, maintainable tests.
"""

import allure
import pytest

from tests.api.clients import AuthAPIClient, TasksAPIClient


@allure.feature("Authentication API")
@allure.story("User Login")
class TestUserLogin:
    """Test cases for user login endpoint."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login with valid credentials")
    @allure.description("Verify that user can login with correct username and password")
    @pytest.mark.integration
    def test_login_success(self, auth_api: AuthAPIClient, registered_user):
        """Test successful login with valid credentials."""
        response = auth_api.login(
            username=registered_user["username"],
            password=registered_user["password"],
        )

        response.assert_ok()
        response.assert_field_exists("access_token")
        response.assert_field_exists("token_type")
        response.assert_field_equals("token_type", "bearer")

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login with incorrect password")
    @allure.description("Verify that login fails with incorrect password")
    @pytest.mark.integration
    def test_login_wrong_password(self, auth_api: AuthAPIClient, registered_user):
        """Test login fails with wrong password."""
        response = auth_api.login(
            username=registered_user["username"],
            password="WrongPassword123!",
        )

        response.assert_unauthorized()
        response.assert_error_contains("Incorrect username or password")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login with non-existent user")
    @allure.description("Verify that login fails for non-existent user")
    @pytest.mark.integration
    def test_login_nonexistent_user(self, auth_api: AuthAPIClient):
        """Test login fails for non-existent user."""
        response = auth_api.login(
            username="nonexistentuser",
            password="SomePassword123!",
        )

        response.assert_unauthorized()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login requires form data format")
    @allure.description("Verify that login endpoint expects form data, not JSON")
    @pytest.mark.integration
    def test_login_requires_form_data(self, auth_api: AuthAPIClient, registered_user):
        """Test that login endpoint requires form data format."""
        response = auth_api.login_with_json(
            username=registered_user["username"],
            password=registered_user["password"],
        )

        response.assert_validation_error()


@allure.feature("Authentication API")
@allure.story("Token Authentication")
class TestTokenAuthentication:
    """Test cases for token-based authentication."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Access protected endpoint with valid token")
    @allure.description("Verify that authenticated requests work with valid token")
    @pytest.mark.integration
    def test_authenticated_request_success(self, authenticated_tasks_api: TasksAPIClient):
        """Test accessing protected endpoint with valid token."""
        response = authenticated_tasks_api.get_all_tasks()

        response.assert_ok()
        response.assert_is_list()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Access protected endpoint without token")
    @allure.description("Verify that requests without token are rejected")
    @pytest.mark.integration
    def test_unauthenticated_request_fails(self, tasks_api: TasksAPIClient):
        """Test accessing protected endpoint without token fails."""
        response = tasks_api.get_all_tasks()

        response.assert_unauthorized()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Access protected endpoint with invalid token")
    @allure.description("Verify that requests with invalid token are rejected")
    @pytest.mark.integration
    def test_invalid_token_fails(self, tasks_api: TasksAPIClient):
        """Test accessing protected endpoint with invalid token fails."""
        # Set invalid token
        tasks_api.set_auth_token("invalid_token_here")

        response = tasks_api.get_all_tasks()

        response.assert_unauthorized()
