"""
Integration tests for Authentication API endpoints.
"""

import allure
import pytest


@allure.feature("Authentication API")
@allure.story("User Registration")
class TestUserRegistration:
    """Test cases for user registration endpoint."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Register new user successfully")
    @allure.description("Verify that a new user can be registered with valid credentials")
    @pytest.mark.integration
    def test_register_user_success(self, api_client, api_base_url):
        """Test successful user registration."""
        with allure.step("Prepare registration data"):
            user_data = {
                "username": f"newuser_{pytest.test_id}",
                "email": f"newuser_{pytest.test_id}@example.com",
                "password": "SecurePass123!",
            }
            allure.attach(str(user_data), name="Registration Data", attachment_type=allure.attachment_type.JSON)

        with allure.step("Send registration request"):
            response = api_client.post(f"{api_base_url}/api/auth/register", json=user_data)
            allure.attach(
                response.text,
                name="Response Body",
                attachment_type=allure.attachment_type.JSON,
            )

        with allure.step("Verify response status code is 200"):
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        with allure.step("Verify response contains user data"):
            response_data = response.json()
            assert "id" in response_data, "Response should contain user ID"
            assert response_data["username"] == user_data["username"]
            assert response_data["email"] == user_data["email"]
            assert "hashed_password" not in response_data, "Password should not be exposed"

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
            response = api_client.post(f"{api_base_url}/api/auth/register", json=duplicate_data)
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
            response = api_client.post(f"{api_base_url}/api/auth/register", json=duplicate_data)
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
            ({"username": "testuser", "password": "pass"}, "email"),
            ({"username": "testuser", "email": "test@example.com"}, "password"),
        ],
    )
    def test_register_missing_fields(self, api_client, api_base_url, invalid_data, expected_field):
        """Test registration with missing required fields."""
        with allure.step(f"Attempt registration without {expected_field}"):
            response = api_client.post(f"{api_base_url}/api/auth/register", json=invalid_data)
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response indicates validation error"):
            assert response.status_code == 422


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
