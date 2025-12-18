"""Login page object for authentication tests."""

from __future__ import annotations

from dataclasses import dataclass

import allure
from playwright.sync_api import Page, expect

from tests.common.constants import JsActions, Routes

from .base_page import BasePage


@dataclass(frozen=True)
class LoginSelectors:
    """Selectors specific to login page."""

    USERNAME_INPUT = 'input[name="username"]'
    PASSWORD_INPUT = 'input[name="password"]'
    LOGIN_BUTTON = "#login"
    REGISTER_LINK = "#register"


class LoginPage(BasePage):
    """Page object for login page interactions."""

    URL_PATH = Routes.LOGIN

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.login_selectors = LoginSelectors()

    def fill_username(self, username: str) -> LoginPage:
        """Fill the username field."""
        with allure.step(f"Fill username: {username}"):
            self.page.fill(self.login_selectors.USERNAME_INPUT, username)
        return self

    def fill_password(self, password: str) -> LoginPage:
        """Fill the password field."""
        with allure.step("Fill password"):
            self.page.fill(self.login_selectors.PASSWORD_INPUT, password)
        return self

    def click_login(self) -> LoginPage:
        """Click the submit button."""
        with allure.step("Click login button"):
            self.page.click(self.login_selectors.LOGIN_BUTTON)
        return self

    def login(self, username: str, password: str) -> LoginPage:
        """Perform login with credentials.

        Args:
            username: User's username
            password: User's password

        Returns:
            Self for method chaining
        """
        with allure.step(f"Login as {username}"):
            self.fill_username(username)
            self.fill_password(password)
            self.click_login()
        return self

    def login_and_expect_success(self, username: str, password: str) -> None:
        """Login and verify redirect to dashboard."""
        self.login(username, password)
        with allure.step("Verify redirect to dashboard"):
            self.wait_for_navigation(Routes.DASHBOARD)

    def login_and_expect_failure(self, username: str, password: str) -> LoginPage:
        """Login and verify error message displayed."""
        self.login(username, password)
        with allure.step("Verify login failure"):
            self.expect_error_alert()
            expect(self.page).to_have_url(self.url)
        return self

    def go_to_register(self) -> LoginPage:
        """Navigate to registration page via link."""
        with allure.step("Click register link"):
            self.page.click(self.login_selectors.REGISTER_LINK)
        return self

    def expect_form_validation_error(self) -> LoginPage:
        """Assert form validation error is displayed (HTML5 validation)."""
        with allure.step("Verify form validation error"):
            # Check that we're still on login page (form didn't submit)
            expect(self.page).to_have_url(self.url)
            # Verify at least one required field shows validation state
            # HTML5 validation makes invalid fields match :invalid pseudo-class
            username_input = self.page.locator(self.login_selectors.USERNAME_INPUT)
            password_input = self.page.locator(self.login_selectors.PASSWORD_INPUT)
            # At least one field should be invalid (have required attribute and be empty)
            is_username_invalid = username_input.evaluate(JsActions.ELEMENT_NOT_VALID)
            is_password_invalid = password_input.evaluate(JsActions.ELEMENT_NOT_VALID)
            assert is_username_invalid or is_password_invalid, "Expected at least one field to be invalid"
        return self
