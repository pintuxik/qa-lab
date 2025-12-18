"""Base API client with common functionality and Allure integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import allure
import httpx


@dataclass
class APIResponse:
    """Wrapper for API responses with chainable assertion helpers.

    Provides fluent interface for response validation with automatic
    Allure step integration for test reporting.

    Example:
        response = client.get("/api/tasks")
        response.assert_ok().assert_field_exists("id").assert_field_equals("title", "Test")
    """

    response: httpx.Response

    @property
    def status_code(self) -> int:
        """HTTP status code."""
        return self.response.status_code

    @property
    def data(self) -> Any:
        """Parse JSON response data.

        Returns:
            Parsed JSON data, or None for empty responses (204 No Content)

        Raises:
            JSONDecodeError: If response is not valid JSON
        """
        # Handle empty responses (204 No Content, etc.)
        if not self.response.content:
            return None
        return self.response.json()

    @property
    def text(self) -> str:
        """Raw response text."""
        return self.response.text

    def attach_to_allure(self, name: str = "Response") -> APIResponse:
        """Attach response to Allure report.

        Args:
            name: Name for the attachment

        Returns:
            Self for method chaining
        """
        attachment_name = f"{name} Body" if self.status_code < 400 else f"{name} Error"
        allure.attach(
            self.text,
            name=attachment_name,
            attachment_type=allure.attachment_type.JSON,
        )
        return self

    # Status code assertions

    def assert_status(self, expected: int, message: str = "") -> APIResponse:
        """Assert response status code equals expected.

        Args:
            expected: Expected HTTP status code
            message: Optional custom error message

        Returns:
            Self for method chaining
        """
        msg = message or f"Expected status {expected}, got {self.status_code}"
        with allure.step(f"Verify response status code is {expected}"):
            assert self.status_code == expected, msg
        return self

    def assert_ok(self) -> APIResponse:
        """Assert successful response (200 OK)."""
        return self.assert_status(200)

    def assert_created(self) -> APIResponse:
        """Assert resource created (201 Created)."""
        return self.assert_status(201)

    def assert_no_content(self) -> APIResponse:
        """Assert no content response (204 No Content)."""
        return self.assert_status(204)

    def assert_bad_request(self) -> APIResponse:
        """Assert bad request (400 Bad Request)."""
        return self.assert_status(400)

    def assert_unauthorized(self) -> APIResponse:
        """Assert unauthorized (401 Unauthorized)."""
        return self.assert_status(401)

    def assert_forbidden(self) -> APIResponse:
        """Assert forbidden (403 Forbidden)."""
        return self.assert_status(403)

    def assert_not_found(self) -> APIResponse:
        """Assert not found (404 Not Found)."""
        return self.assert_status(404)

    def assert_validation_error(self) -> APIResponse:
        """Assert validation error (422 Unprocessable Entity)."""
        return self.assert_status(422)

    # Field assertions

    def assert_field_exists(self, field: str) -> APIResponse:
        """Assert a field exists in response JSON.

        Args:
            field: Field name to check

        Returns:
            Self for method chaining
        """
        with allure.step(f"Verify '{field}' exists in response"):
            assert field in self.data, f"Field '{field}' not found in response: {self.data}"
        return self

    def assert_field_not_exists(self, field: str) -> APIResponse:
        """Assert a field does not exist in response JSON.

        Args:
            field: Field name to check

        Returns:
            Self for method chaining
        """
        with allure.step(f"Verify '{field}' not in response"):
            assert field not in self.data, f"Field '{field}' should not be in response"
        return self

    def assert_field_equals(self, field: str, expected: Any) -> APIResponse:
        """Assert a field in response equals expected value.

        Args:
            field: Field name to check
            expected: Expected value

        Returns:
            Self for method chaining
        """
        with allure.step(f"Verify {field} equals {expected}"):
            actual = self.data.get(field)
            assert actual == expected, f"Expected {field}={expected}, got {actual}"
        return self

    def assert_field_contains(self, field: str, substring: str) -> APIResponse:
        """Assert a string field contains substring.

        Args:
            field: Field name to check
            substring: Expected substring

        Returns:
            Self for method chaining
        """
        with allure.step(f"Verify {field} contains '{substring}'"):
            actual = str(self.data.get(field, ""))
            assert substring in actual, f"Expected '{substring}' in {field}, got '{actual}'"
        return self

    def assert_field_is_true(self, field: str) -> APIResponse:
        """Assert a boolean field is True."""
        return self.assert_field_equals(field, True)

    def assert_field_is_false(self, field: str) -> APIResponse:
        """Assert a boolean field is False."""
        return self.assert_field_equals(field, False)

    # List assertions

    def assert_is_list(self) -> APIResponse:
        """Assert response is a list."""
        with allure.step("Verify response is a list"):
            assert isinstance(self.data, list), f"Response should be a list, got {type(self.data)}"
        return self

    def assert_list_length(self, expected: int) -> APIResponse:
        """Assert list response has exactly expected length.

        Args:
            expected: Expected number of items

        Returns:
            Self for method chaining
        """
        with allure.step(f"Verify response has {expected} items"):
            actual = len(self.data)
            assert actual == expected, f"Expected {expected} items, got {actual}"
        return self

    def assert_list_not_empty(self) -> APIResponse:
        """Assert list response is not empty."""
        with allure.step("Verify response list is not empty"):
            assert len(self.data) > 0, "Response list should not be empty"
        return self

    def assert_list_min_length(self, min_length: int) -> APIResponse:
        """Assert list response has at least min_length items.

        Args:
            min_length: Minimum number of items

        Returns:
            Self for method chaining
        """
        with allure.step(f"Verify response has at least {min_length} items"):
            actual = len(self.data)
            assert actual >= min_length, f"Expected at least {min_length} items, got {actual}"
        return self

    # Error assertions

    def assert_error_detail(self, expected: str) -> APIResponse:
        """Assert error detail message equals expected.

        Args:
            expected: Expected error detail message

        Returns:
            Self for method chaining
        """
        with allure.step(f"Verify error detail is '{expected}'"):
            detail = self.data.get("detail", "")
            assert detail == expected, f"Expected detail '{expected}', got '{detail}'"
        return self

    def assert_error_contains(self, text: str) -> APIResponse:
        """Assert error detail contains text.

        Args:
            text: Text to search for in error detail

        Returns:
            Self for method chaining
        """
        with allure.step(f"Verify error contains '{text}'"):
            detail = str(self.data.get("detail", ""))
            assert text in detail, f"Expected '{text}' in error detail, got '{detail}'"
        return self


class BaseAPIClient:
    """Base API client with common HTTP methods and Allure integration.

    Provides a clean interface for making HTTP requests with automatic
    response wrapping and Allure step integration.

    Subclasses should set BASE_PATH to their endpoint prefix.

    Example:
        class TasksAPIClient(BaseAPIClient):
            BASE_PATH = "/api/tasks"

            def create_task(self, title: str) -> APIResponse:
                return self.post(json={"title": title})
    """

    BASE_PATH: str = ""

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self.client = client
        self.base_url = base_url.rstrip("/")

    @property
    def endpoint(self) -> str:
        """Full endpoint URL."""
        return f"{self.base_url}{self.BASE_PATH}"

    def _make_url(self, path: str = "") -> str:
        """Build full URL from path.

        Args:
            path: Optional path to append to endpoint

        Returns:
            Full URL string
        """
        if path:
            # No trailing slash for paths (e.g., /api/tasks/123 or /api/auth/login)
            clean_path = path.strip("/")
            return f"{self.endpoint}/{clean_path}"
        # Base endpoint needs trailing slash (e.g., /api/tasks/)
        return f"{self.endpoint}/"

    def _request(
        self,
        method: str,
        path: str = "",
        step_name: str = "",
        attach_response: bool = True,
        **kwargs: Any,
    ) -> APIResponse:
        """Make HTTP request with Allure step.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: Optional path to append to endpoint
            step_name: Custom step name for Allure
            attach_response: Whether to attach response to Allure (default: True)
            **kwargs: Additional arguments passed to httpx

        Returns:
            APIResponse wrapper
        """
        url = self._make_url(path)
        step = step_name or f"{method.upper()} {url}"

        with allure.step(step):
            response = self.client.request(method, url, **kwargs)
            api_response = APIResponse(response)

            if attach_response:
                api_response.attach_to_allure()

            return api_response

    def get(
        self,
        path: str = "",
        step_name: str = "",
        **kwargs: Any,
    ) -> APIResponse:
        """Make GET request.

        Args:
            path: Optional path to append to endpoint
            step_name: Custom step name for Allure
            **kwargs: Additional arguments passed to httpx

        Returns:
            APIResponse wrapper
        """
        return self._request("GET", path, step_name, **kwargs)

    def post(
        self,
        path: str = "",
        step_name: str = "",
        **kwargs: Any,
    ) -> APIResponse:
        """Make POST request.

        Args:
            path: Optional path to append to endpoint
            step_name: Custom step name for Allure
            **kwargs: Additional arguments passed to httpx

        Returns:
            APIResponse wrapper
        """
        return self._request("POST", path, step_name, **kwargs)

    def put(
        self,
        path: str = "",
        step_name: str = "",
        **kwargs: Any,
    ) -> APIResponse:
        """Make PUT request.

        Args:
            path: Optional path to append to endpoint
            step_name: Custom step name for Allure
            **kwargs: Additional arguments passed to httpx

        Returns:
            APIResponse wrapper
        """
        return self._request("PUT", path, step_name, **kwargs)

    def patch(
        self,
        path: str = "",
        step_name: str = "",
        **kwargs: Any,
    ) -> APIResponse:
        """Make PATCH request.

        Args:
            path: Optional path to append to endpoint
            step_name: Custom step name for Allure
            **kwargs: Additional arguments passed to httpx

        Returns:
            APIResponse wrapper
        """
        return self._request("PATCH", path, step_name, **kwargs)

    def delete(
        self,
        path: str = "",
        step_name: str = "",
        **kwargs: Any,
    ) -> APIResponse:
        """Make DELETE request.

        Args:
            path: Optional path to append to endpoint
            step_name: Custom step name for Allure
            **kwargs: Additional arguments passed to httpx

        Returns:
            APIResponse wrapper
        """
        return self._request("DELETE", path, step_name, **kwargs)

    def set_auth_token(self, token: str) -> None:
        """Set authentication token in client headers.

        Args:
            token: JWT access token
        """
        self.client.headers.update({"Authorization": f"Bearer {token}"})

    def clear_auth(self) -> None:
        """Remove authentication from client."""
        self.client.headers.pop("Authorization", None)
