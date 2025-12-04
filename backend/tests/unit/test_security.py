"""
Unit tests for security utility functions.

Note: Tests for authentication logic (authenticate_user, create_access_token, get_current_user)
have been moved to service layer tests since those functions are now part of AuthService.
These functions are tested through:
- tests/unit/api/test_auth.py - Integration tests for auth endpoints
- Service layer tests would go in tests/unit/services/ (future enhancement)
"""

from app.core.security import get_password_hash, verify_password


class TestPasswordHashing:
    """Tests for password hashing functions."""

    async def test_password_hash_creates_hash(self):
        """Test that password hashing creates a hash."""
        password = "testpassword123"
        hashed = await get_password_hash(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    async def test_password_hash_is_different_each_time(self):
        """Test that same password produces different hashes (salt)."""
        password = "testpassword123"
        hash1 = await get_password_hash(password)
        hash2 = await get_password_hash(password)

        assert hash1 != hash2

    async def test_verify_correct_password(self):
        """Test verifying correct password returns True."""
        password = "testpassword123"
        hashed = await get_password_hash(password)

        assert await verify_password(password, hashed) is True

    async def test_verify_incorrect_password(self):
        """Test verifying incorrect password returns False."""
        password = "testpassword123"
        hashed = await get_password_hash(password)

        assert await verify_password("wrongpassword", hashed) is False

    async def test_hash_empty_password(self):
        """Test hashing empty password."""
        password = ""
        hashed = await get_password_hash(password)

        assert hashed is not None
        assert await verify_password("", hashed) is True

    async def test_hash_long_password(self):
        """Test hashing very long password."""
        password = "a" * 100
        hashed = await get_password_hash(password)

        assert hashed is not None
        assert await verify_password(password, hashed) is True

    async def test_hash_special_characters(self):
        """Test hashing password with special characters."""
        password = "p@ssw0rd!#$%^&*()"
        hashed = await get_password_hash(password)

        assert hashed is not None
        assert await verify_password(password, hashed) is True
