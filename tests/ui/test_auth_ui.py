"""
UI Integration tests for Authentication flows.

Test structure:
- TestUserLogin: Tests login form (uses 'login_page' fixture)
- TestUserLogout: Tests logout functionality (uses 'dashboard_page' fixture)
- TestProtectedRoutes: Tests unauthenticated access (uses 'login_page' fixture)
"""

import allure
import pytest

from tests.common.constants import Routes
from tests.ui.pages import DashboardPage, LoginPage


@allure.feature("Authentication UI")
@allure.story("User Login")
class TestUserLogin:
    """Test cases for user login UI."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login with valid credentials")
    @allure.description("Verify that user can login with valid credentials")
    @pytest.mark.ui
    def test_login_success(self, login_page: LoginPage, registered_test_user):
        """Test successful login."""
        login_page.open()
        login_page.login_and_expect_success(
            username=registered_test_user["username"],
            password=registered_test_user["password"],
        )

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login with invalid credentials")
    @allure.description("Verify that login fails with incorrect password")
    @pytest.mark.ui
    def test_login_invalid_credentials(self, login_page: LoginPage):
        """Test login with invalid credentials."""
        login_page.open()
        login_page.login_and_expect_failure(
            username="nonexistent_user",
            password="WrongPassword123!",
        )

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login form validation")
    @allure.description("Verify that login form validates required fields")
    @pytest.mark.ui
    def test_login_form_validation(self, login_page: LoginPage):
        """Test login form validation."""
        login_page.open()
        login_page.click_login()
        login_page.expect_form_validation_error()


@allure.feature("Authentication UI")
@allure.story("User Logout")
class TestUserLogout:
    """Test cases for user logout UI.

    Tests focus on logout behavior, not login form testing.
    """

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Logout functionality")
    @allure.description("Verify that user can logout successfully")
    @pytest.mark.ui
    def test_logout(self, dashboard_page: DashboardPage):
        """Test user logout."""
        dashboard_page.logout()
        dashboard_page.try_to_navigate(Routes.LOGOUT)
        dashboard_page.wait_for_navigation(Routes.LOGIN)


@allure.feature("Authentication UI")
@allure.story("Protected Routes")
class TestProtectedRoutes:
    """Test cases for protected route access."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Dashboard requires authentication")
    @allure.description("Verify that dashboard redirects to login when not authenticated")
    @pytest.mark.ui
    def test_dashboard_requires_auth(self, login_page: LoginPage):
        """Test that dashboard requires authentication and redirect to login."""
        login_page.try_to_navigate(Routes.DASHBOARD)
        login_page.wait_for_navigation(Routes.LOGIN)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Root redirects to login when not authenticated")
    @allure.description("Verify that root path redirects to login")
    @pytest.mark.ui
    def test_root_redirects_to_login(self, login_page: LoginPage):
        """Test that root redirects to login."""
        login_page.try_to_navigate(Routes.ROOT)
        login_page.wait_for_navigation(Routes.LOGIN)
