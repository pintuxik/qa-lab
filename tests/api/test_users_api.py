"""
Integration tests for User Management API endpoints.

Uses API client abstraction for clean, maintainable tests.
"""

import allure
import pytest

from tests.api.clients import UsersAPIClient
from tests.common.factories import UserFactory


@allure.feature("User Management API")
@allure.story("User Registration")
class TestUserRegistration:
    """Test cases for user registration endpoint."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Register new user successfully")
    @allure.description("Verify that a new user can be registered with valid credentials")
    @pytest.mark.integration
    def test_register_user_success(self, users_api: UsersAPIClient):
        """Test successful user registration."""
        user = UserFactory.api_user()

        response = users_api.register(
            username=user.username,
            email=user.email,
            password=user.password,
        )

        response.assert_created()
        response.assert_field_exists("id")
        response.assert_field_equals("username", user.username)
        response.assert_field_equals("email", user.email)
        response.assert_field_not_exists("hashed_password")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Register user with duplicate email")
    @allure.description("Verify that registration fails when email is already registered")
    @pytest.mark.integration
    def test_register_duplicate_email(self, users_api: UsersAPIClient, registered_user):
        """Test registration with duplicate email fails."""
        response = users_api.register(
            username="differentuser",
            email=registered_user["email"],
            password="AnotherPass123!",
        )

        response.assert_bad_request()
        response.assert_error_contains("Email already registered")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Register user with duplicate username")
    @allure.description("Verify that registration fails when username is already taken")
    @pytest.mark.integration
    def test_register_duplicate_username(self, users_api: UsersAPIClient, registered_user):
        """Test registration with duplicate username fails."""
        response = users_api.register(
            username=registered_user["username"],
            email="different@example.com",
            password="AnotherPass123!",
        )

        response.assert_bad_request()
        response.assert_error_contains("Username already taken")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Register user with invalid data")
    @allure.description("Verify that registration fails with invalid or missing data")
    @pytest.mark.integration
    @pytest.mark.parametrize(
        "invalid_data,expected_field",
        [
            ({"email": "test@example.com", "password": "pass"}, "username"),
            ({"username": "api_user", "password": "pass"}, "email"),
            ({"username": "api_user", "email": "test@example.com"}, "password"),
        ],
    )
    def test_register_missing_fields(self, users_api: UsersAPIClient, invalid_data, expected_field):
        """Test registration with missing required fields."""
        with allure.step(f"Attempt registration without {expected_field}"):
            # Use raw post since we're testing malformed data
            response = users_api.post(json=invalid_data)

        response.assert_validation_error()
