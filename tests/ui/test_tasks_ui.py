"""
UI Integration tests for Task Management flows.

Uses Page Object Model with authenticated dashboard_page fixture:
- User creation happens via API
- Session authentication happens via Flask frontend
- Page navigates directly to dashboard
- All tests focus on UI feature behavior, not auth flows
"""

import allure
import pytest

from tests.common.factories import TaskFactory
from tests.ui.pages import DashboardPage


@allure.feature("Task Management UI")
@allure.story("Dashboard")
class TestDashboard:
    """Test cases for dashboard UI."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Dashboard loads successfully")
    @allure.description("Verify that dashboard loads with all elements")
    @pytest.mark.ui
    def test_dashboard_loads(self, dashboard_page: DashboardPage):
        """Test dashboard loads successfully."""
        dashboard_page.expect_loaded()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Dashboard shows statistics")
    @allure.description("Verify that dashboard displays task statistics")
    @pytest.mark.ui
    def test_dashboard_statistics(self, dashboard_page: DashboardPage):
        """Test dashboard statistics display."""
        dashboard_page.expect_statistics_visible()


@allure.feature("Task Management UI")
@allure.story("Task Creation")
class TestTaskCreation:
    """Test cases for task creation UI."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Create task through UI")
    @allure.description("Verify that user can create a new task")
    @pytest.mark.ui
    def test_create_task(self, dashboard_page: DashboardPage):
        """Test creating a new task."""
        task = TaskFactory.complete("UI Test Task")

        dashboard_page.create_task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            category=task.category,
        )
        dashboard_page.expect_task_exists(task.title)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create task with minimal data")
    @allure.description("Verify that task can be created with only required fields")
    @pytest.mark.ui
    def test_create_task_minimal(self, dashboard_page: DashboardPage):
        """Test creating task with minimal data."""
        task = TaskFactory.minimal("Minimal Task")

        dashboard_page.create_task(title=task.title)
        dashboard_page.expect_task_exists(task.title)

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Cancel task creation")
    @allure.description("Verify that task creation can be cancelled")
    @pytest.mark.ui
    def test_cancel_task_creation(self, dashboard_page: DashboardPage):
        """Test cancelling task creation."""
        modal = dashboard_page.open_add_task_modal()
        modal.fill_title("Cancelled Task")
        modal.cancel()
        modal.expect_hidden()

        dashboard_page.expect_task_not_exists("Cancelled Task")


@allure.feature("Task Management UI")
@allure.story("Task Operations")
class TestTaskOperations:
    """Test cases for task operations UI."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Mark task as complete")
    @allure.description("Verify that task can be marked as complete")
    @pytest.mark.ui
    def test_complete_task(self, dashboard_page: DashboardPage):
        """Test marking task as complete."""
        task = TaskFactory.simple("Task to Complete")

        # Create task
        task_card = dashboard_page.create_task(title=task.title)

        # Mark complete
        task_card.mark_complete()
        task_card.expect_completed()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Delete task")
    @allure.description("Verify that task can be deleted")
    @pytest.mark.ui
    def test_delete_task(self, dashboard_page: DashboardPage):
        """Test deleting a task."""
        task = TaskFactory.simple("Task to Delete")

        # Create task
        task_card = dashboard_page.create_task(title=task.title)

        # Delete task
        task_card.delete()

        # Verify removed
        dashboard_page.expect_task_not_exists(task.title)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("View task details")
    @allure.description("Verify that task details can be viewed")
    @pytest.mark.ui
    def test_view_task_details(self, dashboard_page: DashboardPage):
        """Test viewing task details."""
        task = TaskFactory.complete("Detailed Task")

        # Create task with all details
        task_card = dashboard_page.create_task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            category=task.category,
        )

        # Verify details visible on card
        task_card.verify_content(task)


@allure.feature("Task Management UI")
@allure.story("Empty State")
class TestEmptyState:
    """Test cases for empty state UI."""

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Empty dashboard shows message")
    @allure.description("Verify that empty dashboard shows appropriate message")
    @pytest.mark.ui
    def test_empty_dashboard(self, dashboard_page: DashboardPage):
        """Test empty dashboard state."""
        # Dashboard should load even without tasks
        dashboard_page.expect_loaded()
        # Verify empty state message is displayed for fresh user
        dashboard_page.expect_empty_state()
