"""
UI Integration tests for Authentication flows.

Test structure:
- TestUserRegistration: Tests registration form (uses 'page' fixture)
- TestUserLogin: Tests login form (uses 'page' fixture)
- TestUserLogout: Tests logout functionality (uses 'authenticated_page' fixture)
- TestProtectedRoutes: Tests unauthenticated access (uses 'page' fixture)

Only registration/login form tests use basic 'page' fixture.
Logout and route protection tests use 'authenticated_page' to skip UI login.
"""

import os
import time

import allure
import pytest
from playwright.sync_api import Page, expect

# Frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5001")


@allure.feature("Authentication UI")
@allure.story("User Registration")
class TestUserRegistration:
    """Test cases for user registration UI."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Register new user through UI")
    @allure.description("Verify that a new user can register through the registration form")
    @pytest.mark.ui
    def test_register_new_user(self, page: Page):
        """Test successful user registration."""
        unique_id = f"{int(time.time() * 1000)}"

        with allure.step("Navigate to registration page"):
            page.goto(f"{FRONTEND_URL}/register")
            expect(page).to_have_url(f"{FRONTEND_URL}/register")

        with allure.step("Fill registration form"):
            page.fill('input[name="username"]', f"uitest_{unique_id}")
            page.fill('input[name="email"]', f"uitest_{unique_id}@example.com")
            page.fill('input[name="password"]', "TestPass123!")

        with allure.step("Submit registration form"):
            page.click('button[type="submit"]')

        with allure.step("Verify redirect to login page"):
            page.wait_for_url(f"{FRONTEND_URL}/login")
            expect(page).to_have_url(f"{FRONTEND_URL}/login")

        with allure.step("Verify success message"):
            # Check for success flash message
            success_message = page.locator(".alert-success")
            expect(success_message).to_be_visible()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Registration form validation")
    @allure.description("Verify that registration form validates required fields")
    @pytest.mark.ui
    def test_register_form_validation(self, page: Page):
        """Test registration form validation."""
        with allure.step("Navigate to registration page"):
            page.goto(f"{FRONTEND_URL}/register")

        with allure.step("Submit empty form"):
            page.click('button[type="submit"]')

        with allure.step("Verify form validation"):
            # HTML5 validation should prevent submission
            expect(page).to_have_url(f"{FRONTEND_URL}/register")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Navigate to login from registration")
    @allure.description("Verify that user can navigate to login page from registration")
    @pytest.mark.ui
    def test_navigate_to_login(self, page: Page):
        """Test navigation from registration to login."""
        with allure.step("Navigate to registration page"):
            page.goto(f"{FRONTEND_URL}/register")

        with allure.step("Click login link"):
            page.click('a[href="/login"]')

        with allure.step("Verify redirect to login page"):
            expect(page).to_have_url(f"{FRONTEND_URL}/login")


@allure.feature("Authentication UI")
@allure.story("User Login")
class TestUserLogin:
    """Test cases for user login UI."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login with valid credentials")
    @allure.description("Verify that user can login with valid credentials")
    @pytest.mark.ui
    def test_login_success(self, page: Page):
        """Test successful login."""
        unique_id = f"{int(time.time() * 1000)}"
        username = f"logintest_{unique_id}"
        password = "TestPass123!"

        with allure.step("Register a test user first"):
            page.goto(f"{FRONTEND_URL}/register")
            page.fill('input[name="username"]', username)
            page.fill('input[name="email"]', f"{username}@example.com")
            page.fill('input[name="password"]', password)
            page.click('button[type="submit"]')
            page.wait_for_url(f"{FRONTEND_URL}/login")

        with allure.step("Navigate to login page"):
            page.goto(f"{FRONTEND_URL}/login")
            expect(page).to_have_url(f"{FRONTEND_URL}/login")

        with allure.step("Fill login form"):
            page.fill('input[name="username"]', username)
            page.fill('input[name="password"]', password)

        with allure.step("Submit login form"):
            page.click('button[type="submit"]')

        with allure.step("Verify redirect to dashboard"):
            page.wait_for_url(f"{FRONTEND_URL}/dashboard")
            expect(page).to_have_url(f"{FRONTEND_URL}/dashboard")

        with allure.step("Verify dashboard is loaded"):
            dashboard_heading = page.locator('h2:has-text("Dashboard")')
            expect(dashboard_heading).to_be_visible()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login with invalid credentials")
    @allure.description("Verify that login fails with incorrect password")
    @pytest.mark.ui
    def test_login_invalid_credentials(self, page: Page):
        """Test login with invalid credentials."""
        with allure.step("Navigate to login page"):
            page.goto(f"{FRONTEND_URL}/login")

        with allure.step("Fill login form with invalid credentials"):
            page.fill('input[name="username"]', "nonexistent_user")
            page.fill('input[name="password"]', "WrongPassword123!")

        with allure.step("Submit login form"):
            page.click('button[type="submit"]')

        with allure.step("Verify error message is displayed"):
            error_message = page.locator(".alert-danger")
            expect(error_message).to_be_visible()

        with allure.step("Verify still on login page"):
            expect(page).to_have_url(f"{FRONTEND_URL}/login")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login form validation")
    @allure.description("Verify that login form validates required fields")
    @pytest.mark.ui
    def test_login_form_validation(self, page: Page):
        """Test login form validation."""
        with allure.step("Navigate to login page"):
            page.goto(f"{FRONTEND_URL}/login")

        with allure.step("Submit empty form"):
            page.click('button[type="submit"]')

        with allure.step("Verify form validation"):
            # HTML5 validation should prevent submission
            expect(page).to_have_url(f"{FRONTEND_URL}/login")


@allure.feature("Authentication UI")
@allure.story("User Logout")
class TestUserLogout:
    """Test cases for user logout UI.

    Uses authenticated_page fixture - already logged in.
    Tests focus on logout behavior, not login form testing.
    """

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Logout functionality")
    @allure.description("Verify that user can logout successfully")
    @pytest.mark.ui
    def test_logout(self, authenticated_page: Page):
        """Test user logout."""
        with allure.step("Click logout button"):
            authenticated_page.click('a[href="/logout"]')

        with allure.step("Verify redirect to login page"):
            authenticated_page.wait_for_url(f"{FRONTEND_URL}/login")
            expect(authenticated_page).to_have_url(f"{FRONTEND_URL}/login")

        with allure.step("Verify cannot access dashboard without login"):
            authenticated_page.goto(f"{FRONTEND_URL}/dashboard")
            authenticated_page.wait_for_url(f"{FRONTEND_URL}/login")
            expect(authenticated_page).to_have_url(f"{FRONTEND_URL}/login")


@allure.feature("Authentication UI")
@allure.story("Protected Routes")
class TestProtectedRoutes:
    """Test cases for protected route access."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Dashboard requires authentication")
    @allure.description("Verify that dashboard redirects to login when not authenticated")
    @pytest.mark.ui
    def test_dashboard_requires_auth(self, page: Page):
        """Test that dashboard requires authentication."""
        with allure.step("Attempt to access dashboard without login"):
            page.goto(f"{FRONTEND_URL}/dashboard")

        with allure.step("Verify redirect to login page"):
            page.wait_for_url(f"{FRONTEND_URL}/login")
            expect(page).to_have_url(f"{FRONTEND_URL}/login")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Root redirects to login when not authenticated")
    @allure.description("Verify that root path redirects to login")
    @pytest.mark.ui
    def test_root_redirects_to_login(self, page: Page):
        """Test that root redirects to login."""
        with allure.step("Navigate to root path"):
            page.goto(f"{FRONTEND_URL}/")

        with allure.step("Verify redirect to login page"):
            page.wait_for_url(f"{FRONTEND_URL}/login")
            expect(page).to_have_url(f"{FRONTEND_URL}/login")
