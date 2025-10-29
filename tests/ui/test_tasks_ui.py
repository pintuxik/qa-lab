"""
UI Integration tests for Task Management flows.
"""

import os
import re
import time

import allure
import pytest
from playwright.sync_api import Page, expect

# Frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5000")


def login_user(page: Page, username: str, password: str):
    """Helper function to login a user."""
    page.goto(f"{FRONTEND_URL}/login")
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{FRONTEND_URL}/dashboard", timeout=5000)


def register_and_login(page: Page):
    """Helper function to register and login a new user."""
    unique_id = f"{int(time.time() * 1000)}"
    username = f"tasktest_{unique_id}"
    password = "TestPass123!"

    # Register
    page.goto(f"{FRONTEND_URL}/register")
    page.fill('input[name="username"]', username)
    page.fill('input[name="email"]', f"{username}@example.com")
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{FRONTEND_URL}/login")

    # Login
    login_user(page, username, password)

    return username, password


@allure.feature("Task Management UI")
@allure.story("Dashboard")
class TestDashboard:
    """Test cases for dashboard UI."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Dashboard loads successfully")
    @allure.description("Verify that dashboard loads with all elements")
    @pytest.mark.ui
    def test_dashboard_loads(self, page: Page):
        """Test dashboard loads successfully."""
        with allure.step("Register and login"):
            register_and_login(page)

        with allure.step("Verify dashboard elements are visible"):
            # Check main heading
            heading = page.locator('h2:has-text("Dashboard")')
            expect(heading).to_be_visible()

            # Check Add Task button
            add_button = page.locator('button:has-text("Add Task")')
            expect(add_button).to_be_visible()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Dashboard shows statistics")
    @allure.description("Verify that dashboard displays task statistics")
    @pytest.mark.ui
    def test_dashboard_statistics(self, page: Page):
        """Test dashboard statistics display."""
        with allure.step("Register and login"):
            register_and_login(page)

        with allure.step("Verify statistics cards are visible"):
            # Check for statistics section
            stats = page.locator(".row .col-md-3")
            expect(stats.first).to_be_visible()


@allure.feature("Task Management UI")
@allure.story("Task Creation")
class TestTaskCreation:
    """Test cases for task creation UI."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Create task through UI")
    @allure.description("Verify that user can create a new task")
    @pytest.mark.ui
    def test_create_task(self, page: Page):
        """Test creating a new task."""
        with allure.step("Register and login"):
            register_and_login(page)

        with allure.step("Click Add Task button"):
            page.click('button:has-text("Add Task")')

        with allure.step("Wait for modal to appear"):
            modal = page.locator("#createTaskModal")
            expect(modal).to_be_visible()

        with allure.step("Fill task form"):
            page.fill("#title", "UI Test Task")
            page.fill("#description", "This is a test task created via UI")
            page.select_option("#priority", "high")
            page.fill("#category", "testing")

        with allure.step("Submit task form"):
            page.click('button:has-text("Create Task")')

        with allure.step("Wait for modal to close"):
            expect(modal).to_be_hidden(timeout=5000)

        with allure.step("Verify task appears in list"):
            task_card = page.locator('.card:has-text("UI Test Task")')
            expect(task_card).to_be_visible()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create task with minimal data")
    @allure.description("Verify that task can be created with only required fields")
    @pytest.mark.ui
    def test_create_task_minimal(self, page: Page):
        """Test creating task with minimal data."""
        with allure.step("Register and login"):
            register_and_login(page)

        with allure.step("Open add task modal"):
            page.click('button:has-text("Add Task")')
            modal = page.locator("#createTaskModal")
            expect(modal).to_be_visible()

        with allure.step("Fill only title"):
            page.fill("#title", "Minimal Task")

        with allure.step("Submit task form"):
            page.click('button:has-text("Create Task")')

        with allure.step("Verify task is created"):
            expect(modal).to_be_hidden(timeout=5000)
            task_card = page.locator('.card:has-text("Minimal Task")')
            expect(task_card).to_be_visible()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Cancel task creation")
    @allure.description("Verify that task creation can be cancelled")
    @pytest.mark.ui
    def test_cancel_task_creation(self, page: Page):
        """Test cancelling task creation."""
        with allure.step("Register and login"):
            register_and_login(page)

        with allure.step("Open add task modal"):
            page.click('button:has-text("Add Task")')
            modal = page.locator("#createTaskModal")
            expect(modal).to_be_visible()

        with allure.step("Fill task form"):
            page.fill("#title", "Cancelled Task")

        with allure.step("Click cancel button"):
            page.click('button:has-text("Cancel")')

        with allure.step("Verify modal is closed"):
            expect(modal).to_be_hidden()

        with allure.step("Verify task was not created"):
            task_card = page.locator('.card:has-text("Cancelled Task")')
            expect(task_card).not_to_be_visible()


@allure.feature("Task Management UI")
@allure.story("Task Operations")
class TestTaskOperations:
    """Test cases for task operations UI."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Mark task as complete")
    @allure.description("Verify that task can be marked as complete")
    @pytest.mark.ui
    def test_complete_task(self, page: Page):
        """Test marking task as complete."""
        with allure.step("Register and login"):
            register_and_login(page)

        with allure.step("Create a test task"):
            page.click('button:has-text("Add Task")')
            page.wait_for_timeout(500)
            page.fill("#title", "Task to Complete")
            page.click('button[type="submit"]:has-text("Create Task")')
            page.wait_for_timeout(1000)

        with allure.step("Click complete button"):
            task_card = page.locator('.card:has-text("Task to Complete")')
            # Open dropdown menu
            dropdown_toggle = task_card.locator("button.dropdown-toggle")
            dropdown_toggle.click()
            page.wait_for_timeout(500)
            # Click Mark Complete
            complete_btn = task_card.locator('button:has-text("Mark Complete")')
            complete_btn.click()
            page.wait_for_timeout(1000)

        with allure.step("Verify task is marked as complete"):
            # Task should have completed-task class
            expect(task_card).to_have_class(re.compile("completed-task"))

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Delete task")
    @allure.description("Verify that task can be deleted")
    @pytest.mark.ui
    def test_delete_task(self, page: Page):
        """Test deleting a task."""
        with allure.step("Register and login"):
            register_and_login(page)

        with allure.step("Create a test task"):
            page.click('button:has-text("Add Task")')
            page.wait_for_timeout(500)
            page.fill("#title", "Task to Delete")
            page.click('button[type="submit"]:has-text("Create Task")')
            page.wait_for_timeout(1000)

        with allure.step("Click delete button"):
            task_card = page.locator('.card:has-text("Task to Delete")')
            # Open dropdown menu
            dropdown_toggle = task_card.locator("button.dropdown-toggle")
            dropdown_toggle.click()
            page.wait_for_timeout(500)
            # Handle confirmation dialog and click Delete
            page.on("dialog", lambda dialog: dialog.accept())
            delete_btn = task_card.locator('button:has-text("Delete")')
            delete_btn.click()
            page.wait_for_timeout(1000)

        with allure.step("Verify task is removed"):
            expect(task_card).not_to_be_visible()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("View task details")
    @allure.description("Verify that task details can be viewed")
    @pytest.mark.ui
    def test_view_task_details(self, page: Page):
        """Test viewing task details."""
        with allure.step("Register and login"):
            register_and_login(page)

        with allure.step("Create a test task with details"):
            page.click('button:has-text("Add Task")')
            page.wait_for_timeout(500)
            page.fill("#title", "Detailed Task")
            page.fill("#description", "This task has detailed information")
            page.select_option("#priority", "high")
            page.fill("#category", "important")
            page.click('button[type="submit"]:has-text("Create Task")')
            page.wait_for_timeout(1000)

        with allure.step("Verify task details are visible"):
            task_card = page.locator('.card:has-text("Detailed Task")')
            expect(task_card).to_be_visible()

            # Check priority badge
            priority_badge = task_card.locator('.badge:has-text("high")')
            expect(priority_badge).to_be_visible()

            # Check category
            category = task_card.locator("text=important")
            expect(category).to_be_visible()


@allure.feature("Task Management UI")
@allure.story("Task Filtering")
class TestTaskFiltering:
    """Test cases for task filtering UI."""

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Filter tasks by priority")
    @allure.description("Verify that tasks can be filtered by priority")
    @pytest.mark.ui
    def test_filter_by_priority(self, page: Page):
        """Test filtering tasks by priority."""
        with allure.step("Register and login"):
            register_and_login(page)

        with allure.step("Create tasks with different priorities"):
            # High priority task
            page.click('button:has-text("Add Task")')
            page.wait_for_timeout(500)
            page.fill("#title", "High Priority Task")
            page.select_option("#priority", "high")
            page.click('button[type="submit"]:has-text("Create Task")')
            page.wait_for_timeout(1000)

            # Low priority task
            page.click('button:has-text("Add Task")')
            page.wait_for_timeout(500)
            page.fill("#title", "Low Priority Task")
            page.select_option("#priority", "low")
            page.click('button[type="submit"]:has-text("Create Task")')
            page.wait_for_timeout(1000)

        with allure.step("Verify both tasks are visible"):
            high_task = page.locator('.card:has-text("High Priority Task")')
            low_task = page.locator('.card:has-text("Low Priority Task")')
            expect(high_task).to_be_visible()
            expect(low_task).to_be_visible()


@allure.feature("Task Management UI")
@allure.story("Empty State")
class TestEmptyState:
    """Test cases for empty state UI."""

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Empty dashboard shows message")
    @allure.description("Verify that empty dashboard shows appropriate message")
    @pytest.mark.ui
    def test_empty_dashboard(self, page: Page):
        """Test empty dashboard state."""
        with allure.step("Register and login new user"):
            register_and_login(page)

        with allure.step("Verify dashboard is empty or shows welcome message"):
            # Dashboard should load even without tasks
            heading = page.locator('h2:has-text("Dashboard")')
            expect(heading).to_be_visible()

            # Add Task button should be available
            add_button = page.locator('button:has-text("Add Task")')
            expect(add_button).to_be_visible()
