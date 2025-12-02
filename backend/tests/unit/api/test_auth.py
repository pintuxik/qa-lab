"""
Unit tests for authentication endpoints.
"""

from fastapi import status
from tests.test_data import Endpoints, TestHelpers, TestUsers


class TestUserRegistration:
    """Tests for user registration endpoint."""

    async def test_register_new_user(self, client):
        """Test successful user registration."""
        response = await client.post(Endpoints.AUTH_REGISTER, json=TestUsers.NEW_USER)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        TestHelpers.assert_valid_user_response(data)
        assert data["username"] == TestUsers.NEW_USER["username"]
        assert data["email"] == TestUsers.NEW_USER["email"]
        assert data["is_admin"] is False

    async def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails."""
        response = await client.post(
            Endpoints.AUTH_REGISTER,
            json=TestHelpers.create_user_payload(
                username="anotheruser",
                email=TestUsers.VALID_USER["email"],  # Duplicate email
            ),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]

    async def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username fails."""
        response = await client.post(
            Endpoints.AUTH_REGISTER,
            json=TestHelpers.create_user_payload(
                username=TestUsers.VALID_USER["username"],  # Duplicate username
                email="another@example.com",
            ),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in response.json()["detail"]

    async def test_register_invalid_data(self, client):
        """Test registration with invalid data fails."""
        response = await client.post(
            Endpoints.AUTH_REGISTER,
            json={"username": "user"},  # Missing email and password
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestUserLogin:
    """Tests for user login endpoint."""

    async def test_login_success(self, client, test_user):
        """Test successful login returns access token."""
        response = await client.post(
            Endpoints.AUTH_LOGIN,
            data={"username": TestUsers.VALID_USER["username"], "password": TestUsers.VALID_USER["password"]},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    async def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails."""
        response = await client.post(
            Endpoints.AUTH_LOGIN, data={"username": TestUsers.VALID_USER["username"], "password": "wrongpassword"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    async def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user fails."""
        response = await client.post(Endpoints.AUTH_LOGIN, data={"username": "nonexistent", "password": "Password123!"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_requires_form_data(self, client, test_user):
        """Test that login requires form data, not JSON."""
        response = await client.post(
            Endpoints.AUTH_LOGIN,
            json={"username": TestUsers.VALID_USER["username"], "password": TestUsers.VALID_USER["password"]},
        )

        # Should fail because OAuth2PasswordRequestForm expects form data
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestAuthentication:
    """Tests for authentication and authorization."""

    async def test_access_protected_endpoint_with_token(self, client, auth_headers):
        """Test accessing protected endpoint with valid token."""
        response = await client.get(Endpoints.TASKS, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

    async def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token fails."""
        response = await client.get(Endpoints.TASKS)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_access_protected_endpoint_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token fails."""
        invalid_headers = TestHelpers.create_auth_headers("invalid_token")
        response = await client.get(Endpoints.TASKS, headers=invalid_headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserRegistrationNegativeCases:
    """Additional negative test cases for user registration."""

    async def test_register_missing_email(self, client):
        """Test registration fails when email is missing."""
        response = await client.post(
            Endpoints.AUTH_REGISTER,
            json={"username": TestUsers.VALID_USER["username"], "password": TestUsers.VALID_USER["password"]},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_missing_password(self, client):
        """Test registration fails when password is missing."""
        response = await client.post(
            Endpoints.AUTH_REGISTER,
            json={"username": TestUsers.VALID_USER["username"], "email": TestUsers.VALID_USER["email"]},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_missing_username(self, client):
        """Test registration fails when username is missing."""
        response = await client.post(
            Endpoints.AUTH_REGISTER,
            json={"email": TestUsers.VALID_USER["email"], "password": TestUsers.VALID_USER["password"]},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_empty_email(self, client):
        """Test registration with empty email."""
        response = await client.post(
            Endpoints.AUTH_REGISTER, json=TestHelpers.create_user_payload(email=TestUsers.INVALID_EMAILS["empty"])
        )

        # Empty email should fail EmailStr validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_empty_username(self, client):
        """Test registration with empty username."""
        response = await client.post(
            Endpoints.AUTH_REGISTER, json=TestHelpers.create_user_payload(username=TestUsers.INVALID_USERNAMES["empty"])
        )

        # Empty username should fail min_length validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_empty_password(self, client):
        """Test registration with empty password."""
        response = await client.post(
            Endpoints.AUTH_REGISTER, json=TestHelpers.create_user_payload(password=TestUsers.WEAK_PASSWORDS["empty"])
        )

        # With min_length=8 validation, empty password should be rejected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_very_long_username(self, client):
        """Test registration with very long username."""
        response = await client.post(
            Endpoints.AUTH_REGISTER,
            json=TestHelpers.create_user_payload(username=TestUsers.INVALID_USERNAMES["too_long"]),
        )

        # With max_length=30 validation, very long username should be rejected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_very_long_email(self, client):
        """Test registration with very long email."""
        long_email = "a" * 1000 + "@example.com"
        response = await client.post(Endpoints.AUTH_REGISTER, json=TestHelpers.create_user_payload(email=long_email))

        # EmailStr validation should reject invalid/very long emails
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_special_characters_in_username(self, client):
        """Test registration with special characters in username."""
        response = await client.post(
            Endpoints.AUTH_REGISTER,
            json=TestHelpers.create_user_payload(username=TestUsers.INVALID_USERNAMES["special_chars"]),
        )

        # With pattern validation, special characters like @ and # should be rejected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_unicode_in_username(self, client):
        """Test registration with unicode characters in username."""
        response = await client.post(
            Endpoints.AUTH_REGISTER,
            json=TestHelpers.create_user_payload(username=TestUsers.INVALID_USERNAMES["unicode"]),
        )

        # With pattern validation [a-zA-Z0-9_-]+, unicode should be rejected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_sql_injection_attempt_in_username(self, client):
        """Test that SQL injection attempts in username are rejected by validation."""
        response = await client.post(
            Endpoints.AUTH_REGISTER,
            json=TestHelpers.create_user_payload(username=TestUsers.INVALID_USERNAMES["sql_injection"]),
        )

        # Pattern validation rejects special characters, preventing SQL injection attempts
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_xss_attempt_in_username(self, client):
        """Test that XSS attempts in username are rejected by validation."""
        response = await client.post(
            Endpoints.AUTH_REGISTER, json=TestHelpers.create_user_payload(username=TestUsers.INVALID_USERNAMES["xss"])
        )

        # Pattern validation rejects special characters like < and >, preventing XSS attempts
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_with_null_values(self, client):
        """Test registration with null values."""
        response = await client.post(Endpoints.AUTH_REGISTER, json={"username": None, "email": None, "password": None})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_with_extra_fields(self, client):
        """Test registration with extra unexpected fields."""
        response = await client.post(
            Endpoints.AUTH_REGISTER,
            json={
                **TestUsers.VALID_USER,
                "is_admin": True,  # Should be ignored
                "extra_field": "value",
            },
        )

        # Should succeed, extra fields should be ignored
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # User should not be admin
        assert data["is_admin"] is False

    async def test_register_case_sensitive_email(self, client, test_user):
        """Test if email comparison is case-sensitive."""
        response = await client.post(
            Endpoints.AUTH_REGISTER,
            json=TestHelpers.create_user_payload(
                username="newuser",
                email="TEST@EXAMPLE.COM",  # test_user has test@example.com
            ),
        )

        # SQLite is case-sensitive, so this should succeed
        assert response.status_code == status.HTTP_201_CREATED

    async def test_register_case_sensitive_username(self, client, test_user):
        """Test if username comparison is case-sensitive."""
        response = await client.post(
            Endpoints.AUTH_REGISTER,
            json=TestHelpers.create_user_payload(
                username="TESTUSER",  # test_user has testuser
                email="new@example.com",
            ),
        )

        # SQLite is case-sensitive, so this should succeed
        assert response.status_code == status.HTTP_201_CREATED


class TestUserLoginNegativeCases:
    """Additional negative test cases for user login."""

    async def test_login_missing_username(self, client):
        """Test login fails when username is missing."""
        response = await client.post(Endpoints.AUTH_LOGIN, data={"password": TestUsers.VALID_USER["password"]})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_login_missing_password(self, client):
        """Test login fails when password is missing."""
        response = await client.post(Endpoints.AUTH_LOGIN, data={"username": TestUsers.VALID_USER["username"]})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_login_empty_username(self, client):
        """Test login with empty username."""
        response = await client.post(
            Endpoints.AUTH_LOGIN, data={"username": "", "password": TestUsers.VALID_USER["password"]}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_login_empty_password(self, client, test_user):
        """Test login with empty password."""
        response = await client.post(
            Endpoints.AUTH_LOGIN, data={"username": TestUsers.VALID_USER["username"], "password": ""}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_login_empty_credentials(self, client):
        """Test login with both username and password empty."""
        response = await client.post(Endpoints.AUTH_LOGIN, data={"username": "", "password": ""})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_login_whitespace_username(self, client):
        """Test login with whitespace-only username."""
        response = await client.post(
            Endpoints.AUTH_LOGIN, data={"username": "   ", "password": TestUsers.VALID_USER["password"]}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_whitespace_password(self, client, test_user):
        """Test login with whitespace-only password."""
        response = await client.post(
            Endpoints.AUTH_LOGIN, data={"username": TestUsers.VALID_USER["username"], "password": "   "}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_sql_injection_attempt(self, client):
        """Test that SQL injection attempts in login are handled safely."""
        response = await client.post(
            Endpoints.AUTH_LOGIN, data={"username": "admin' OR '1'='1", "password": "anything"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_case_sensitive_username(self, client, test_user):
        """Test if username login is case-sensitive."""
        response = await client.post(
            Endpoints.AUTH_LOGIN,
            data={
                "username": "TESTUSER",  # Uppercase version of testuser
                "password": TestUsers.VALID_USER["password"],
            },
        )

        # SQLite is case-sensitive, login should fail
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_with_email_instead_of_username(self, client, test_user):
        """Test login with email instead of username."""
        response = await client.post(
            Endpoints.AUTH_LOGIN,
            data={"username": TestUsers.VALID_USER["email"], "password": TestUsers.VALID_USER["password"]},
        )

        # Should fail unless email login is supported
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_no_request_body(self, client):
        """Test login with no request body."""
        response = await client.post(Endpoints.AUTH_LOGIN)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestAuthenticationNegativeCases:
    """Additional negative test cases for authentication."""

    async def test_access_protected_endpoint_malformed_token(self, client):
        """Test accessing protected endpoint with malformed token."""
        response = await client.get(Endpoints.TASKS, headers={"Authorization": "Bearer not.a.valid.jwt.token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_access_protected_endpoint_missing_bearer_prefix(self, client, auth_token):
        """Test accessing protected endpoint without 'Bearer' prefix."""
        response = await client.get(
            Endpoints.TASKS,
            headers={"Authorization": auth_token},  # Missing "Bearer" prefix
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_access_protected_endpoint_wrong_auth_scheme(self, client, auth_token):
        """Test accessing protected endpoint with wrong auth scheme."""
        response = await client.get(Endpoints.TASKS, headers={"Authorization": f"Basic {auth_token}"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_access_protected_endpoint_empty_token(self, client):
        """Test accessing protected endpoint with empty token."""
        response = await client.get(Endpoints.TASKS, headers={"Authorization": "Bearer "})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_access_protected_endpoint_no_authorization_header(self, client):
        """Test accessing protected endpoint without Authorization header."""
        response = await client.get(Endpoints.TASKS)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_access_protected_endpoint_multiple_bearer_tokens(self, client, auth_token):
        """Test accessing protected endpoint with multiple tokens."""
        response = await client.get(
            Endpoints.TASKS, headers={"Authorization": f"Bearer {auth_token} Bearer {auth_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_token_with_special_characters(self, client):
        """Test token with special characters."""
        response = await client.get(Endpoints.TASKS, headers={"Authorization": "Bearer token!@#$%^&*()"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_very_long_token(self, client):
        """Test with very long token string."""
        long_token = "a" * 10000

        response = await client.get(Endpoints.TASKS, headers={"Authorization": f"Bearer {long_token}"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
