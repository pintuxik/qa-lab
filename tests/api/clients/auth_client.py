"""Authentication API client."""

from __future__ import annotations

import allure

from tests.api.clients.base_client import APIResponse, BaseAPIClient
from tests.common.constants import Endpoints


class AuthAPIClient(BaseAPIClient):
    """Client for Authentication API endpoints.

    Handles login and token operations for the /api/auth endpoints.

    Example:
        auth = AuthAPIClient(client, base_url)
        response = auth.login("user", "password")
        response.assert_ok()
        token = response.data["access_token"]
    """

    BASE_PATH = Endpoints.AUTH

    def login(self, username: str, password: str) -> APIResponse:
        """Login with credentials.

        Args:
            username: User's username
            password: User's password

        Returns:
            APIResponse with access token on success
        """
        with allure.step(f"Login as {username}"):
            return self.post(
                path="login",
                step_name=f"POST {self.endpoint}/login",
                data={"username": username, "password": password},
            )

    def login_with_json(self, username: str, password: str) -> APIResponse:
        """Attempt login with JSON body instead of form data.

        Used for testing that endpoint correctly rejects JSON format.

        Args:
            username: User's username
            password: User's password

        Returns:
            APIResponse (should be error for wrong content type)
        """
        with allure.step("Attempt login with JSON (invalid)"):
            return self.post(
                path="login",
                step_name="POST /api/auth/login (JSON)",
                json={"username": username, "password": password},
            )

    def get_token(self, username: str, password: str) -> str:
        """Login and return just the access token.

        Convenience method for fixture usage.

        Args:
            username: User's username
            password: User's password

        Returns:
            Access token string

        Raises:
            AssertionError: If login fails
            KeyError: If access_token not in response
        """
        response = self.login(username, password)
        response.assert_ok()
        response.assert_field_exists("access_token")
        return response.data["access_token"]
