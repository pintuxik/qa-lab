"""
UI Integration tests for User Management flows.
"""

import os
import time

import allure
import pytest
from conftest import TEST_API_KEY
from playwright.sync_api import Page, expect

# Frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5001")


@allure.feature("User Management UI")
@allure.story("User Registration")
class TestUserRegistration:
    """Test cases for user registration UI."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Register new user through UI")
    @allure.description("Verify that a new user can register through the registration form")
    @pytest.mark.ui
    def test_register_new_user(self, page: Page, api_client, api_base_url):
        """Test successful user registration."""
        unique_id = f"{int(time.time() * 1000)}"

        with allure.step("Navigate to registration page"):
            page.goto(f"{FRONTEND_URL}/register")
            expect(page).to_have_url(f"{FRONTEND_URL}/register")

        with allure.step("Fill registration form"):
            page.fill('input[name="username"]', f"ui_user_{unique_id}")
            page.fill('input[name="email"]', f"ui_user_{unique_id}@example.com")
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

        with allure.step("Cleanup test user"):
            if TEST_API_KEY:
                response = api_client.post(
                    f"{api_base_url}/api/users/test-cleanup",
                    json={"username_patterns": [unique_id]},
                    headers={"X-Test-API-Key": TEST_API_KEY},
                )
                assert response.status_code == 200, f"Failed to cleanup user: {response.text}"

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
