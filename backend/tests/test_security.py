"""
Unit tests for security functions.
"""

from datetime import timedelta

from app.core.security import authenticate_user, create_access_token, get_password_hash, verify_password


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_password_hash_creates_hash(self):
        """Test that password hashing creates a hash."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    def test_password_hash_is_different_each_time(self):
        """Test that same password produces different hashes (salt)."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2

    def test_verify_correct_password(self):
        """Test verifying correct password returns True."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Test verifying incorrect password returns False."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password("wrongpassword", hashed) is False

    def test_hash_empty_password(self):
        """Test hashing empty password."""
        password = ""
        hashed = get_password_hash(password)

        assert hashed is not None
        assert verify_password("", hashed) is True

    def test_hash_long_password(self):
        """Test hashing very long password."""
        password = "a" * 100
        hashed = get_password_hash(password)

        assert hashed is not None
        assert verify_password(password, hashed) is True

    def test_hash_special_characters(self):
        """Test hashing password with special characters."""
        password = "p@ssw0rd!#$%^&*()"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Tests for JWT token creation."""

    def test_create_access_token(self):
        """Test creating access token."""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_with_expiration(self):
        """Test creating token with custom expiration."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)

        assert token is not None
        assert isinstance(token, str)

    def test_token_contains_payload(self):
        """Test that token contains the payload data."""
        from app.core.config import settings
        from jose import jwt

        data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data)

        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "admin"
        assert "exp" in decoded


class TestUserAuthentication:
    """Tests for user authentication."""

    def test_authenticate_valid_user(self, db_session, test_user):
        """Test authenticating with valid credentials."""
        user = authenticate_user(db_session, "testuser", "testpass123")

        assert user is not False
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_authenticate_wrong_password(self, db_session, test_user):
        """Test authentication fails with wrong password."""
        user = authenticate_user(db_session, "testuser", "wrongpassword")

        assert user is False

    def test_authenticate_nonexistent_user(self, db_session):
        """Test authentication fails for nonexistent user."""
        user = authenticate_user(db_session, "nonexistent", "password123")

        assert user is False

    def test_authenticate_empty_credentials(self, db_session):
        """Test authentication fails with empty credentials."""
        user = authenticate_user(db_session, "", "")

        assert user is False
