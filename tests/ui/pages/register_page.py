"""Register page object for user registration tests."""

from __future__ import annotations

from dataclasses import dataclass

import allure
from playwright.sync_api import Page, expect

from tests.common.constants import JsActions, Routes
from tests.ui.pages import BasePage


@dataclass(frozen=True)
class RegisterSelectors:
    """Selectors specific to registration page."""

    USERNAME_INPUT = 'input[name="username"]'
    EMAIL_INPUT = 'input[name="email"]'
    PASSWORD_INPUT = 'input[name="password"]'
    REGISTER_BUTTON = "#register"
    LOGIN_LINK = "#login"


class RegisterPage(BasePage):
    """Page object for registration page interactions."""

    URL_PATH = "/register"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.register_selectors = RegisterSelectors()

    def fill_username(self, username: str) -> RegisterPage:
        """Fill the username field."""
        with allure.step(f"Fill username: {username}"):
            self.page.fill(self.register_selectors.USERNAME_INPUT, username)
        return self

    def fill_email(self, email: str) -> RegisterPage:
        """Fill the email field."""
        with allure.step(f"Fill email: {email}"):
            self.page.fill(self.register_selectors.EMAIL_INPUT, email)
        return self

    def fill_password(self, password: str) -> RegisterPage:
        """Fill the password field."""
        with allure.step("Fill password"):
            self.page.fill(self.register_selectors.PASSWORD_INPUT, password)
        return self

    def click_register(self) -> RegisterPage:
        """Click the submit button."""
        with allure.step("Click register button"):
            self.page.click(self.register_selectors.REGISTER_BUTTON)
        return self

    def register(
        self,
        username: str,
        email: str,
        password: str,
    ) -> RegisterPage:
        """Fill registration form with credentials.

        Args:
            username: Desired username
            email: User's email
            password: User's password

        Returns:
            Self for method chaining
        """
        with allure.step(f"Register user: {username}"):
            self.fill_username(username)
            self.fill_email(email)
            self.fill_password(password)
            self.click_register()
        return self

    def register_and_expect_success(
        self,
        username: str,
        email: str,
        password: str,
    ) -> None:
        """Register and verify redirect to login with success message."""
        self.register(username, email, password)
        with allure.step("Verify redirect to login"):
            self.wait_for_navigation(Routes.LOGIN)
            self.expect_success_alert()

    def register_and_expect_failure(
        self,
        username: str,
        email: str,
        password: str,
        confirm_password: str | None = None,
    ) -> RegisterPage:
        """Register and verify error message displayed."""
        self.register(username, email, password)
        with allure.step("Verify registration failure"):
            self.expect_error_alert()
            expect(self.page).to_have_url(self.url)
        return self

    def go_to_login(self) -> RegisterPage:
        """Navigate to login page via link."""
        with allure.step("Click login link"):
            self.page.click(self.register_selectors.LOGIN_LINK)
        return self

    def expect_form_validation_error(self) -> RegisterPage:
        """Assert form validation error is displayed (HTML5 validation)."""
        with allure.step("Verify form validation error"):
            # Check that we're still on register page (form didn't submit)
            expect(self.page).to_have_url(self.url)
            # Verify at least one required field shows validation state
            username_input = self.page.locator(self.register_selectors.USERNAME_INPUT)
            email_input = self.page.locator(self.register_selectors.EMAIL_INPUT)
            password_input = self.page.locator(self.register_selectors.PASSWORD_INPUT)
            # At least one field should be invalid (have required attribute and be empty)
            is_username_invalid = username_input.evaluate(JsActions.ELEMENT_NOT_VALID)
            is_email_invalid = email_input.evaluate(JsActions.ELEMENT_NOT_VALID)
            is_password_invalid = password_input.evaluate(JsActions.ELEMENT_NOT_VALID)
            assert is_username_invalid or is_email_invalid or is_password_invalid, (
                "Expected at least one field to be invalid"
            )
        return self
