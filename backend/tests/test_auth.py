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

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


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
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


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
