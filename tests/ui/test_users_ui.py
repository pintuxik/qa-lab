"""
UI Integration tests for User Management flows.

Uses Page Object Model for clean, maintainable tests.
"""

import allure
import pytest

from tests.common.constants import Routes
from tests.common.factories import UserFactory
from tests.ui.pages import RegisterPage


@allure.feature("User Management UI")
@allure.story("User Registration")
class TestUserRegistration:
    """Test cases for user registration UI."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Register new user through UI")
    @allure.description("Verify that a new user can register through the registration form")
    @pytest.mark.ui
    def test_register_new_user(self, register_page: RegisterPage):
        """Test successful user registration."""
        user = UserFactory.ui_user()

        register_page.open()
        register_page.register_and_expect_success(
            username=user.username,
            email=user.email,
            password=user.password,
        )

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Registration form validation")
    @allure.description("Verify that registration form validates required fields")
    @pytest.mark.ui
    def test_register_form_validation(self, register_page: RegisterPage):
        """Test registration form validation."""
        register_page.open()
        register_page.click_register()
        register_page.expect_form_validation_error()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Navigate to login from registration")
    @allure.description("Verify that user can navigate to login page from registration")
    @pytest.mark.ui
    def test_navigate_to_login(self, register_page: RegisterPage):
        """Test navigation from registration to login."""
        register_page.open()
        register_page.go_to_login()
        register_page.wait_for_navigation(Routes.LOGIN)
