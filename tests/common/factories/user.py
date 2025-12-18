"""Test data factories for generating unique test user data.

Provides dataclasses and factory methods for creating test users
with unique identifiers to support parallel test execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from tests.common.utils import generate_unique_id


@dataclass
class UserData:
    """Test user data container.

    Automatically generates unique username and email if not provided.

    Example:
        user = UserData.generate()
        response = api.register(user.username, user.email, user.password)

        # Or with custom prefix
        user = UserData.generate(prefix="admin_user")
    """

    username: str
    email: str
    password: str = "TestPass123!"
    id: int | None = None

    DEFAULT_PASSWORD: ClassVar[str] = "TestPass123!"

    @classmethod
    def generate(cls, prefix: str = "test_user") -> UserData:
        """Generate a unique test user.

        Args:
            prefix: Prefix for username/email (default: test_user)

        Returns:
            UserData with unique username and email
        """
        unique_id = generate_unique_id()
        return cls(
            username=f"{prefix}_{unique_id}",
            email=f"{prefix}_{unique_id}@example.com",
            password=cls.DEFAULT_PASSWORD,
        )

    @classmethod
    def api_user(cls) -> UserData:
        """Generate user for API tests (prefix: api_user)."""
        return cls.generate(prefix="api_user")

    @classmethod
    def ui_user(cls) -> UserData:
        """Generate user for UI tests (prefix: ui_user)."""
        return cls.generate(prefix="ui_user")

    def to_registration_dict(self) -> dict[str, str]:
        """Convert to registration API payload."""
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
        }

    def to_login_dict(self) -> dict[str, str]:
        """Convert to login form data."""
        return {
            "username": self.username,
            "password": self.password,
        }

    def to_credentials_dict(self) -> dict[str, str]:
        """Convert to credentials dict (for fixtures compatibility)."""
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
        }


@dataclass
class UserFactory:
    """Factory for creating various test user configurations.

    Example:
        user = UserFactory.api_user()
        user = UserFactory.ui_user()
        user = UserFactory.admin()
    """

    @staticmethod
    def api_user() -> UserData:
        """Create user for API tests."""
        return UserData.api_user()

    @staticmethod
    def ui_user() -> UserData:
        """Create user for UI tests."""
        return UserData.ui_user()

    @staticmethod
    def with_prefix(prefix: str) -> UserData:
        """Create user with custom prefix.

        Args:
            prefix: Prefix for username/email
        """
        return UserData.generate(prefix=prefix)
