"""
Integration tests for Authentication API endpoints.
"""

import allure
import pytest


@allure.feature("Authentication API")
@allure.story("User Login")
class TestUserLogin:
    """Test cases for user login endpoint."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login with valid credentials")
    @allure.description("Verify that user can login with correct username and password")
    @pytest.mark.integration
    def test_login_success(self, api_client, api_base_url, registered_user):
        """Test successful login with valid credentials."""
        with allure.step("Prepare login credentials"):
            login_data = {
                "username": registered_user["username"],
                "password": registered_user["password"],
            }

        with allure.step("Send login request"):
            response = api_client.post(f"{api_base_url}/api/auth/login", data=login_data)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 200"):
            assert response.status_code == 200

        with allure.step("Verify response contains access token"):
            response_data = response.json()
            assert "access_token" in response_data
            assert "token_type" in response_data
            assert response_data["token_type"] == "bearer"
            assert len(response_data["access_token"]) > 0

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login with incorrect password")
    @allure.description("Verify that login fails with incorrect password")
    @pytest.mark.integration
    def test_login_wrong_password(self, api_client, api_base_url, registered_user):
        """Test login fails with wrong password."""
        with allure.step("Attempt login with wrong password"):
            login_data = {
                "username": registered_user["username"],
                "password": "WrongPassword123!",
            }
            response = api_client.post(f"{api_base_url}/api/auth/login", data=login_data)
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 401"):
            assert response.status_code == 401

        with allure.step("Verify error message"):
            response_data = response.json()
            assert "Incorrect username or password" in response_data["detail"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login with non-existent user")
    @allure.description("Verify that login fails for non-existent user")
    @pytest.mark.integration
    def test_login_nonexistent_user(self, api_client, api_base_url):
        """Test login fails for non-existent user."""
        with allure.step("Attempt login with non-existent username"):
            login_data = {
                "username": "nonexistentuser",
                "password": "SomePassword123!",
            }
            response = api_client.post(f"{api_base_url}/api/auth/login", data=login_data)
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 401"):
            assert response.status_code == 401

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login requires form data format")
    @allure.description("Verify that login endpoint expects form data, not JSON")
    @pytest.mark.integration
    def test_login_requires_form_data(self, api_client, api_base_url, registered_user):
        """Test that login endpoint requires form data format."""
        with allure.step("Attempt login with JSON instead of form data"):
            login_data = {
                "username": registered_user["username"],
                "password": registered_user["password"],
            }
            response = api_client.post(f"{api_base_url}/api/auth/login", json=login_data)
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response indicates validation error"):
            assert response.status_code == 422


@allure.feature("Authentication API")
@allure.story("Token Authentication")
class TestTokenAuthentication:
    """Test cases for token-based authentication."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Access protected endpoint with valid token")
    @allure.description("Verify that authenticated requests work with valid token")
    @pytest.mark.integration
    def test_authenticated_request_success(self, authenticated_client, api_base_url):
        """Test accessing protected endpoint with valid token."""
        with allure.step("Send authenticated request to tasks endpoint"):
            response = authenticated_client.get(f"{api_base_url}/api/tasks/")
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 200"):
            assert response.status_code == 200

        with allure.step("Verify response is a list"):
            response_data = response.json()
            assert isinstance(response_data, list)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Access protected endpoint without token")
    @allure.description("Verify that requests without token are rejected")
    @pytest.mark.integration
    def test_unauthenticated_request_fails(self, api_client, api_base_url):
        """Test accessing protected endpoint without token fails."""
        with allure.step("Send request without authentication token"):
            response = api_client.get(f"{api_base_url}/api/tasks/")
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 401"):
            assert response.status_code == 401

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Access protected endpoint with invalid token")
    @allure.description("Verify that requests with invalid token are rejected")
    @pytest.mark.integration
    def test_invalid_token_fails(self, api_client, api_base_url):
        """Test accessing protected endpoint with invalid token fails."""
        with allure.step("Send request with invalid token"):
            api_client.headers.update({"Authorization": "Bearer invalid_token_here"})
            response = api_client.get(f"{api_base_url}/api/tasks/")
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 401"):
            assert response.status_code == 401
