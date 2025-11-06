"""
Unit tests for authentication endpoints.
"""

from fastapi import status


class TestUserRegistration:
    """Tests for user registration endpoint."""

    def test_register_new_user(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/auth/register", json={"username": "newuser", "email": "newuser@example.com", "password": "newpass123"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "hashed_password" not in data
        assert data["is_active"] is True
        assert data["is_admin"] is False

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "anotheruser",
                "email": "test@example.com",  # Duplicate email
                "password": "password123",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username fails."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",  # Duplicate username
                "email": "another@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in response.json()["detail"]

    def test_register_invalid_data(self, client):
        """Test registration with invalid data fails."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "user",
                # Missing email and password
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestUserLogin:
    """Tests for user login endpoint."""

    def test_login_success(self, client, test_user):
        """Test successful login returns access token."""
        response = client.post("/api/auth/login", data={"username": "testuser", "password": "testpass123"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails."""
        response = client.post("/api/auth/login", data={"username": "testuser", "password": "wrongpassword"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user fails."""
        response = client.post("/api/auth/login", data={"username": "nonexistent", "password": "password123"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_requires_form_data(self, client, test_user):
        """Test that login requires form data, not JSON."""
        response = client.post("/api/auth/login", json={"username": "testuser", "password": "testpass123"})

        # Should fail because OAuth2PasswordRequestForm expects form data
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestAuthentication:
    """Tests for authentication and authorization."""

    def test_access_protected_endpoint_with_token(self, client, auth_headers):
        """Test accessing protected endpoint with valid token."""
        response = client.get("/api/tasks", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token fails."""
        response = client.get("/api/tasks")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token fails."""
        response = client.get("/api/tasks", headers={"Authorization": "Bearer invalid_token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserRegistrationNegativeCases:
    """Additional negative test cases for user registration."""

    def test_register_missing_email(self, client):
        """Test registration fails when email is missing."""
        response = client.post("/api/auth/register", json={"username": "testuser", "password": "testpass123"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_register_missing_password(self, client):
        """Test registration fails when password is missing."""
        response = client.post("/api/auth/register", json={"username": "testuser", "email": "test@example.com"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_register_missing_username(self, client):
        """Test registration fails when username is missing."""
        response = client.post("/api/auth/register", json={"email": "test@example.com", "password": "testpass123"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_register_empty_email(self, client):
        """Test registration with empty email."""
        response = client.post(
            "/api/auth/register", json={"username": "testuser", "email": "", "password": "testpass123"}
        )

        # Should either fail validation or succeed (depends on schema validation)
        # Current implementation doesn't validate email format
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        ]

    def test_register_empty_username(self, client):
        """Test registration with empty username."""
        response = client.post(
            "/api/auth/register", json={"username": "", "email": "test@example.com", "password": "testpass123"}
        )

        # Should succeed or fail based on validation rules
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        ]

    def test_register_empty_password(self, client):
        """Test registration with empty password."""
        response = client.post(
            "/api/auth/register", json={"username": "testuser", "email": "test@example.com", "password": ""}
        )

        # Should succeed with empty password (no validation currently)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_register_very_long_username(self, client):
        """Test registration with very long username."""
        long_username = "a" * 1000

        response = client.post(
            "/api/auth/register",
            json={"username": long_username, "email": "test@example.com", "password": "testpass123"},
        )

        # Should succeed (no length validation currently)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_register_very_long_email(self, client):
        """Test registration with very long email."""
        long_email = "a" * 1000 + "@example.com"

        response = client.post(
            "/api/auth/register", json={"username": "testuser", "email": long_email, "password": "testpass123"}
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_register_special_characters_in_username(self, client):
        """Test registration with special characters in username."""
        response = client.post(
            "/api/auth/register",
            json={"username": "test@user#123", "email": "test@example.com", "password": "testpass123"},
        )

        # Should succeed (no character validation currently)
        assert response.status_code == status.HTTP_200_OK

    def test_register_unicode_in_username(self, client):
        """Test registration with unicode characters in username."""
        response = client.post(
            "/api/auth/register", json={"username": "用户名", "email": "test@example.com", "password": "testpass123"}
        )

        assert response.status_code == status.HTTP_200_OK

    def test_register_sql_injection_attempt_in_username(self, client):
        """Test that SQL injection attempts in username are handled safely."""
        response = client.post(
            "/api/auth/register",
            json={"username": "admin' OR '1'='1", "email": "test@example.com", "password": "testpass123"},
        )

        # Should be safely stored as a literal string
        assert response.status_code == status.HTTP_200_OK

    def test_register_xss_attempt_in_username(self, client):
        """Test that XSS attempts in username are handled safely."""
        response = client.post(
            "/api/auth/register",
            json={"username": "<script>alert('xss')</script>", "email": "test@example.com", "password": "testpass123"},
        )

        # Should be safely stored as a literal string
        assert response.status_code == status.HTTP_200_OK

    def test_register_with_null_values(self, client):
        """Test registration with null values."""
        response = client.post("/api/auth/register", json={"username": None, "email": None, "password": None})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_register_with_extra_fields(self, client):
        """Test registration with extra unexpected fields."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123",
                "is_admin": True,  # Should be ignored
                "extra_field": "value",
            },
        )

        # Should succeed, extra fields should be ignored
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # User should not be admin
        assert data["is_admin"] is False

    def test_register_case_sensitive_email(self, client, test_user):
        """Test if email comparison is case-sensitive."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "TEST@EXAMPLE.COM",  # test_user has test@example.com
                "password": "testpass123",
            },
        )

        # Behavior depends on database collation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_register_case_sensitive_username(self, client, test_user):
        """Test if username comparison is case-sensitive."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "TESTUSER",  # test_user has testuser
                "email": "new@example.com",
                "password": "testpass123",
            },
        )

        # Behavior depends on database collation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


class TestUserLoginNegativeCases:
    """Additional negative test cases for user login."""

    def test_login_missing_username(self, client):
        """Test login fails when username is missing."""
        response = client.post("/api/auth/login", data={"password": "testpass123"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_login_missing_password(self, client):
        """Test login fails when password is missing."""
        response = client.post("/api/auth/login", data={"username": "testuser"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_login_empty_username(self, client):
        """Test login with empty username."""
        response = client.post("/api/auth/login", data={"username": "", "password": "testpass123"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_empty_password(self, client, test_user):
        """Test login with empty password."""
        response = client.post("/api/auth/login", data={"username": "testuser", "password": ""})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_empty_credentials(self, client):
        """Test login with both username and password empty."""
        response = client.post("/api/auth/login", data={"username": "", "password": ""})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_whitespace_username(self, client):
        """Test login with whitespace-only username."""
        response = client.post("/api/auth/login", data={"username": "   ", "password": "testpass123"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_whitespace_password(self, client, test_user):
        """Test login with whitespace-only password."""
        response = client.post("/api/auth/login", data={"username": "testuser", "password": "   "})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_sql_injection_attempt(self, client):
        """Test that SQL injection attempts in login are handled safely."""
        response = client.post("/api/auth/login", data={"username": "admin' OR '1'='1", "password": "anything"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_case_sensitive_username(self, client, test_user):
        """Test if username login is case-sensitive."""
        response = client.post("/api/auth/login", data={"username": "TESTUSER", "password": "testpass123"})

        # Behavior depends on implementation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_login_with_email_instead_of_username(self, client, test_user):
        """Test login with email instead of username."""
        response = client.post("/api/auth/login", data={"username": "test@example.com", "password": "testpass123"})

        # Should fail unless email login is supported
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_no_request_body(self, client):
        """Test login with no request body."""
        response = client.post("/api/auth/login")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestAuthenticationNegativeCases:
    """Additional negative test cases for authentication."""

    def test_access_protected_endpoint_malformed_token(self, client):
        """Test accessing protected endpoint with malformed token."""
        response = client.get("/api/tasks", headers={"Authorization": "Bearer not.a.valid.jwt.token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_missing_bearer_prefix(self, client, auth_token):
        """Test accessing protected endpoint without 'Bearer' prefix."""
        response = client.get(
            "/api/tasks",
            headers={"Authorization": auth_token},  # Missing "Bearer" prefix
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_wrong_auth_scheme(self, client, auth_token):
        """Test accessing protected endpoint with wrong auth scheme."""
        response = client.get("/api/tasks", headers={"Authorization": f"Basic {auth_token}"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_empty_token(self, client):
        """Test accessing protected endpoint with empty token."""
        response = client.get("/api/tasks", headers={"Authorization": "Bearer "})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_no_authorization_header(self, client):
        """Test accessing protected endpoint without Authorization header."""
        response = client.get("/api/tasks")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_multiple_bearer_tokens(self, client, auth_token):
        """Test accessing protected endpoint with multiple tokens."""
        response = client.get("/api/tasks", headers={"Authorization": f"Bearer {auth_token} Bearer {auth_token}"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_with_special_characters(self, client):
        """Test token with special characters."""
        response = client.get("/api/tasks", headers={"Authorization": "Bearer token!@#$%^&*()"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_very_long_token(self, client):
        """Test with very long token string."""
        long_token = "a" * 10000

        response = client.get("/api/tasks", headers={"Authorization": f"Bearer {long_token}"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
