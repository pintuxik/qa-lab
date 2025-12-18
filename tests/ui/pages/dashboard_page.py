"""Dashboard page object for task management tests."""

from __future__ import annotations

from dataclasses import dataclass

import allure
from playwright.sync_api import Locator, Page, expect

from tests.common.constants import Routes
from tests.ui.components import TaskCard, TaskModal
from tests.ui.pages.base_page import BasePage


@dataclass(frozen=True)
class DashboardSelectors:
    """Selectors specific to dashboard page."""

    HEADING = "#header"
    ADD_TASK_BUTTON = "#add-task"
    STATISTICS_SECTION = "#statistics"
    TASK_LIST = "#tasks-list"
    EMPTY_STATE = "#no-tasks"
    TASK_CARD_TEMPLATE = '.card:has-text("{title}")'


class DashboardPage(BasePage):
    """Page object for dashboard interactions."""

    URL_PATH = Routes.DASHBOARD

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.dashboard_selectors = DashboardSelectors()
        self._task_modal: TaskModal | None = None

    @property
    def task_modal(self) -> TaskModal:
        """Get task modal component (lazy initialization)."""
        if self._task_modal is None:
            self._task_modal = TaskModal(self.page)
        return self._task_modal

    def expect_loaded(self) -> DashboardPage:
        """Verify dashboard elements are visible."""
        with allure.step("Verify dashboard is loaded"):
            heading = self.page.locator(self.dashboard_selectors.HEADING)
            expect(heading).to_be_visible()

            add_button = self.page.locator(self.dashboard_selectors.ADD_TASK_BUTTON)
            expect(add_button).to_be_visible()
        return self

    def expect_statistics_visible(self) -> DashboardPage:
        """Verify statistics section is visible."""
        with allure.step("Verify statistics section is visible"):
            stats = self.page.locator(self.dashboard_selectors.STATISTICS_SECTION)
            expect(stats.first).to_be_visible()
        return self

    def open_add_task_modal(self) -> TaskModal:
        """Open the add task modal."""
        with allure.step("Click Add Task button"):
            self.page.click(self.dashboard_selectors.ADD_TASK_BUTTON)

        with allure.step("Wait for modal to appear"):
            self.task_modal.expect_visible()

        return self.task_modal

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        category: str = "",
    ) -> TaskCard:
        """Create a new task and return its card component.

        Args:
            title: Task title (required)
            description: Task description (optional)
            priority: Task priority - low/medium/high (default: medium)
            category: Task category (optional)

        Returns:
            TaskCard component for the created task
        """
        with allure.step(f"Create new task '{title}'"):
            modal = self.open_add_task_modal()
            modal.create_task(title, description, priority, category)

        return self.get_task_card(title)

    def get_task_card(self, title: str) -> TaskCard:
        """Get a task card by title.

        Args:
            title: Task title to find

        Returns:
            TaskCard component for interactions
        """
        return TaskCard.from_title(self.page, title)

    def expect_task_exists(self, title: str) -> DashboardPage:
        """Assert a task with given title exists and is visible."""
        with allure.step(f"Verify task '{title}' exists"):
            card = self.get_task_card(title)
            card.expect_visible()
        return self

    def expect_task_not_exists(self, title: str) -> DashboardPage:
        """Assert a task with given title does not exist."""
        with allure.step(f"Verify task '{title}' does not exist"):
            card = self.get_task_card(title)
            card.expect_not_visible()
        return self

    def expect_empty_state(self) -> DashboardPage:
        """Assert empty state message is displayed (no tasks)."""
        with allure.step("Verify empty state message"):
            # Look for the actual empty state text from dashboard.html
            empty_text = self.page.locator('text="No tasks yet"')
            expect(empty_text).to_be_visible()
        return self

    def get_all_task_cards(self) -> list[Locator]:
        """Get all visible task cards."""
        return self.page.locator(".card").all()

    def count_tasks(self) -> int:
        """Count visible tasks on dashboard."""
        return len(self.get_all_task_cards())
