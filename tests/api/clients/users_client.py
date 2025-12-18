"""Users API client for user management."""

from __future__ import annotations

import allure

from tests.api.clients.base_client import APIResponse, BaseAPIClient
from tests.common.constants import Endpoints


class UsersAPIClient(BaseAPIClient):
    """Client for Users API endpoints.

    Handles user registration and management for the /api/users endpoints.

    Example:
        users = UsersAPIClient(client, base_url)
        response = users.register("newuser", "user@example.com", "Password123!")
        response.assert_created()
    """

    BASE_PATH = Endpoints.USERS

    def register(
        self,
        username: str,
        email: str,
        password: str,
    ) -> APIResponse:
        """Register a new user.

        Args:
            username: Desired username
            email: User's email address
            password: User's password

        Returns:
            APIResponse with created user data
        """
        user_data = {
            "username": username,
            "email": email,
            "password": password,
        }

        with allure.step(f"Register user: {username}"):
            allure.attach(
                str({"username": username, "email": email}),
                name="Registration Data",
                attachment_type=allure.attachment_type.JSON,
            )
            return self.post(
                step_name=f"POST {self.endpoint}",
                json=user_data,
            )

    def get_current_user(self) -> APIResponse:
        """Get current authenticated user info.

        Returns:
            APIResponse with user data
        """
        return self.get(
            path="me",
            step_name="Get current user",
        )

    def register_and_get_id(
        self,
        username: str,
        email: str,
        password: str,
    ) -> int:
        """Register a user and return their ID.

        Convenience method for test setup.

        Args:
            username: Desired username
            email: User's email
            password: User's password

        Returns:
            Created user ID

        Raises:
            AssertionError: If registration fails
            KeyError: If id not in response
        """
        response = self.register(username, email, password)
        response.assert_created()
        response.assert_field_exists("id")
        return response.data["id"]
