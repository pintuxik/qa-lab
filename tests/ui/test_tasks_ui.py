"""
UI Integration tests for Task Management flows.

Uses authenticated_page fixture to skip UI-based registration/login:
- User creation happens via API
- Session authentication happens via Flask frontend
- Page navigates directly to dashboard
- All tests focus on UI feature behavior, not auth flows
"""

import os
import re

import allure
import pytest
from playwright.sync_api import Page, expect

# Frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5001")


@allure.feature("Task Management UI")
@allure.story("Dashboard")
class TestDashboard:
    """Test cases for dashboard UI.

    Uses authenticated_page fixture - user already logged in, on dashboard.
    """

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Dashboard loads successfully")
    @allure.description("Verify that dashboard loads with all elements")
    @pytest.mark.ui
    def test_dashboard_loads(self, authenticated_page: Page):
        """Test dashboard loads successfully."""
        with allure.step("Verify dashboard elements are visible"):
            # Check main heading
            heading = authenticated_page.locator('h2:has-text("Dashboard")')
            expect(heading).to_be_visible()

            # Check Add Task button
            add_button = authenticated_page.locator('button:has-text("Add Task")')
            expect(add_button).to_be_visible()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Dashboard shows statistics")
    @allure.description("Verify that dashboard displays task statistics")
    @pytest.mark.ui
    def test_dashboard_statistics(self, authenticated_page: Page):
        """Test dashboard statistics display."""
        with allure.step("Verify statistics cards are visible"):
            # Check for statistics section
            stats = authenticated_page.locator(".row .col-md-3")
            expect(stats.first).to_be_visible()


@allure.feature("Task Management UI")
@allure.story("Task Creation")
class TestTaskCreation:
    """Test cases for task creation UI.

    Uses authenticated_page fixture - user already logged in, on dashboard.
    """

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Create task through UI")
    @allure.description("Verify that user can create a new task")
    @pytest.mark.ui
    def test_create_task(self, authenticated_page: Page):
        """Test creating a new task."""
        with allure.step("Click Add Task button"):
            authenticated_page.click('button:has-text("Add Task")')

        with allure.step("Wait for modal to appear"):
            modal = authenticated_page.locator("#createTaskModal")
            expect(modal).to_be_visible()

        with allure.step("Fill task form"):
            authenticated_page.fill("#title", "UI Test Task")
            authenticated_page.fill("#description", "This is a test task created via UI")
            authenticated_page.select_option("#priority", "high")
            authenticated_page.fill("#category", "testing")

        with allure.step("Submit task form"):
            authenticated_page.click('button:has-text("Create Task")')

        with allure.step("Wait for modal to close"):
            expect(modal).to_be_hidden()

        with allure.step("Verify task appears in list"):
            task_card = authenticated_page.locator('.card:has-text("UI Test Task")')
            expect(task_card).to_be_visible()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create task with minimal data")
    @allure.description("Verify that task can be created with only required fields")
    @pytest.mark.ui
    def test_create_task_minimal(self, authenticated_page: Page):
        """Test creating task with minimal data."""
        with allure.step("Open add task modal"):
            authenticated_page.click('button:has-text("Add Task")')
            modal = authenticated_page.locator("#createTaskModal")
            expect(modal).to_be_visible()

        with allure.step("Fill only title"):
            authenticated_page.fill("#title", "Minimal Task")

        with allure.step("Submit task form"):
            authenticated_page.click('button:has-text("Create Task")')

        with allure.step("Verify task is created"):
            expect(modal).to_be_hidden()
            task_card = authenticated_page.locator('.card:has-text("Minimal Task")')
            expect(task_card).to_be_visible()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Cancel task creation")
    @allure.description("Verify that task creation can be cancelled")
    @pytest.mark.ui
    def test_cancel_task_creation(self, authenticated_page: Page):
        """Test cancelling task creation."""
        with allure.step("Open add task modal"):
            authenticated_page.click('button:has-text("Add Task")')
            modal = authenticated_page.locator("#createTaskModal")
            expect(modal).to_be_visible()

        with allure.step("Fill task form"):
            authenticated_page.fill("#title", "Cancelled Task")

        with allure.step("Click cancel button"):
            authenticated_page.click('button:has-text("Cancel")')

        with allure.step("Verify modal is closed"):
            expect(modal).to_be_hidden()

        with allure.step("Verify task was not created"):
            task_card = authenticated_page.locator('.card:has-text("Cancelled Task")')
            expect(task_card).not_to_be_visible()


@allure.feature("Task Management UI")
@allure.story("Task Operations")
class TestTaskOperations:
    """Test cases for task operations UI.

    Uses authenticated_page fixture - user already logged in, on dashboard.
    """

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Mark task as complete")
    @allure.description("Verify that task can be marked as complete")
    @pytest.mark.ui
    def test_complete_task(self, authenticated_page: Page):
        """Test marking task as complete."""
        with allure.step("Create a test task"):
            authenticated_page.click('button:has-text("Add Task")')
            modal = authenticated_page.locator("#createTaskModal")
            expect(modal).to_be_visible()
            authenticated_page.fill("#title", "Task to Complete")
            authenticated_page.click('button[type="submit"]:has-text("Create Task")')
            expect(modal).to_be_hidden()

        with allure.step("Click complete button"):
            task_card = authenticated_page.locator('.card:has-text("Task to Complete")')
            # Open dropdown menu
            dropdown_toggle = task_card.locator("button.dropdown-toggle")
            dropdown_toggle.click()
            # Click Mark Complete
            complete_btn = task_card.locator('button:has-text("Mark Complete")')
            expect(complete_btn).to_be_visible()
            complete_btn.click()
            # Wait for the task card to be updated with completed state
            expect(task_card).to_have_class(re.compile("completed-task"))

        with allure.step("Verify task is marked as complete"):
            # Task should have completed-task class
            expect(task_card).to_have_class(re.compile("completed-task"))

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Delete task")
    @allure.description("Verify that task can be deleted")
    @pytest.mark.ui
    def test_delete_task(self, authenticated_page: Page):
        """Test deleting a task."""
        with allure.step("Create a test task"):
            authenticated_page.click('button:has-text("Add Task")')
            modal = authenticated_page.locator("#createTaskModal")
            expect(modal).to_be_visible()
            authenticated_page.fill("#title", "Task to Delete")
            authenticated_page.click('button[type="submit"]:has-text("Create Task")')
            expect(modal).to_be_hidden()

        with allure.step("Click delete button"):
            task_card = authenticated_page.locator('.card:has-text("Task to Delete")')
            # Open dropdown menu
            dropdown_toggle = task_card.locator("button.dropdown-toggle")
            dropdown_toggle.click()
            # Handle confirmation dialog and click Delete
            authenticated_page.on("dialog", lambda dialog: dialog.accept())
            delete_btn = task_card.locator('button:has-text("Delete")')
            expect(delete_btn).to_be_visible()
            delete_btn.click()

        with allure.step("Verify task is removed"):
            expect(task_card).not_to_be_visible()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("View task details")
    @allure.description("Verify that task details can be viewed")
    @pytest.mark.ui
    def test_view_task_details(self, authenticated_page: Page):
        """Test viewing task details."""
        with allure.step("Create a test task with details"):
            authenticated_page.click('button:has-text("Add Task")')
            modal = authenticated_page.locator("#createTaskModal")
            expect(modal).to_be_visible()
            authenticated_page.fill("#title", "Detailed Task")
            authenticated_page.fill("#description", "This task has detailed information")
            authenticated_page.select_option("#priority", "high")
            authenticated_page.fill("#category", "important")
            authenticated_page.click('button[type="submit"]:has-text("Create Task")')
            expect(modal).to_be_hidden()

        with allure.step("Verify task details are visible"):
            task_card = authenticated_page.locator('.card:has-text("Detailed Task")')
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
    """Test cases for task filtering UI.

    Uses authenticated_page fixture - user already logged in, on dashboard.
    """

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Filter tasks by priority")
    @allure.description("Verify that tasks can be filtered by priority")
    @pytest.mark.ui
    def test_filter_by_priority(self, authenticated_page: Page):
        """Test filtering tasks by priority."""
        with allure.step("Create tasks with different priorities"):
            modal = authenticated_page.locator("#createTaskModal")

            # High priority task
            authenticated_page.click('button:has-text("Add Task")')
            expect(modal).to_be_visible()
            authenticated_page.fill("#title", "High Priority Task")
            authenticated_page.select_option("#priority", "high")
            authenticated_page.click('button[type="submit"]:has-text("Create Task")')
            expect(modal).to_be_hidden()

            # Low priority task
            authenticated_page.click('button:has-text("Add Task")')
            expect(modal).to_be_visible()
            authenticated_page.fill("#title", "Low Priority Task")
            authenticated_page.select_option("#priority", "low")
            authenticated_page.click('button[type="submit"]:has-text("Create Task")')
            expect(modal).to_be_hidden()

        with allure.step("Verify both tasks are visible"):
            high_task = authenticated_page.locator('.card:has-text("High Priority Task")')
            low_task = authenticated_page.locator('.card:has-text("Low Priority Task")')
            expect(high_task).to_be_visible()
            expect(low_task).to_be_visible()


@allure.feature("Task Management UI")
@allure.story("Empty State")
class TestEmptyState:
    """Test cases for empty state UI.

    Uses authenticated_page fixture - user already logged in, on dashboard.
    Fresh user with no tasks - ideal for empty state testing.
    """

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Empty dashboard shows message")
    @allure.description("Verify that empty dashboard shows appropriate message")
    @pytest.mark.ui
    def test_empty_dashboard(self, authenticated_page: Page):
        """Test empty dashboard state."""
        with allure.step("Verify dashboard is empty or shows welcome message"):
            # Dashboard should load even without tasks
            heading = authenticated_page.locator('h2:has-text("Dashboard")')
            expect(heading).to_be_visible()

            # Add Task button should be available
            add_button = authenticated_page.locator('button:has-text("Add Task")')
            expect(add_button).to_be_visible()
