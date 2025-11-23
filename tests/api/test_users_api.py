"""
Integration tests for User Management API endpoints.
"""

import allure
import pytest
from conftest import TEST_API_KEY


@allure.feature("User Management API")
@allure.story("User Registration")
class TestUserRegistration:
    """Test cases for user registration endpoint."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Register new user successfully")
    @allure.description("Verify that a new user can be registered with valid credentials")
    @pytest.mark.integration
    def test_register_user_success(self, api_client, api_base_url, test_user_credentials):
        """Test successful user registration."""
        with allure.step("Prepare registration data"):
            user_data = test_user_credentials
            allure.attach(str(user_data), name="Registration Data", attachment_type=allure.attachment_type.JSON)

        with allure.step("Send registration request"):
            response = api_client.post(f"{api_base_url}/api/users/", json=user_data)
            allure.attach(
                response.text,
                name="Response Body",
                attachment_type=allure.attachment_type.JSON,
            )

        with allure.step("Verify response status code is 201"):
            assert response.status_code == 201, f"Expected 201, got {response.status_code}"

        with allure.step("Verify response contains user data"):
            response_data = response.json()
            assert "id" in response_data, "Response should contain user ID"
            assert response_data["username"] == user_data["username"]
            assert response_data["email"] == user_data["email"]
            assert "hashed_password" not in response_data, "Password should not be exposed"

        # Cleanup: Delete test user using secure test-cleanup endpoint
        if TEST_API_KEY:
            with allure.step("Cleanup test user via test-cleanup endpoint"):
                try:
                    response = api_client.post(
                        f"{api_base_url}/api/users/test-cleanup",
                        json={"user_ids": [response_data["id"]]},
                        headers={"X-Test-API-Key": TEST_API_KEY},
                    )
                    assert response.status_code == 200, f"Failed to cleanup user: {response.text}"
                    allure.attach(
                        f"Deleted user: {response_data['username']} (ID: {response_data['id']})",
                        name="Test User Cleanup",
                        attachment_type=allure.attachment_type.TEXT,
                    )
                except Exception as e:
                    # Log cleanup failure but don't fail the test
                    allure.attach(
                        f"Failed to cleanup user {response_data['username']}: {str(e)}",
                        name="Cleanup Warning",
                        attachment_type=allure.attachment_type.TEXT,
                    )

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Register user with duplicate email")
    @allure.description("Verify that registration fails when email is already registered")
    @pytest.mark.integration
    def test_register_duplicate_email(self, api_client, api_base_url, registered_user):
        """Test registration with duplicate email fails."""
        with allure.step("Attempt to register with existing email"):
            duplicate_data = {
                "username": "differentuser",
                "email": registered_user["email"],
                "password": "AnotherPass123!",
            }
            response = api_client.post(f"{api_base_url}/api/users/", json=duplicate_data)
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 400"):
            assert response.status_code == 400

        with allure.step("Verify error message"):
            response_data = response.json()
            assert "Email already registered" in response_data["detail"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Register user with duplicate username")
    @allure.description("Verify that registration fails when username is already taken")
    @pytest.mark.integration
    def test_register_duplicate_username(self, api_client, api_base_url, registered_user):
        """Test registration with duplicate username fails."""
        with allure.step("Attempt to register with existing username"):
            duplicate_data = {
                "username": registered_user["username"],
                "email": "different@example.com",
                "password": "AnotherPass123!",
            }
            response = api_client.post(f"{api_base_url}/api/users/", json=duplicate_data)
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 400"):
            assert response.status_code == 400

        with allure.step("Verify error message"):
            response_data = response.json()
            assert "Username already taken" in response_data["detail"]

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
    def test_register_missing_fields(self, api_client, api_base_url, invalid_data, expected_field):
        """Test registration with missing required fields."""
        with allure.step(f"Attempt registration without {expected_field}"):
            response = api_client.post(f"{api_base_url}/api/users/", json=invalid_data)
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response indicates validation error"):
            assert response.status_code == 422
