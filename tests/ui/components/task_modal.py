"""Task modal component for task creation/editing."""

from __future__ import annotations

from dataclasses import dataclass

import allure
from playwright.sync_api import Locator, Page, expect


@dataclass(frozen=True)
class TaskModalSelectors:
    """Selectors for task modal."""

    MODAL = "#createTaskModal"
    TITLE_INPUT = "#title"
    DESCRIPTION_INPUT = "#description"
    PRIORITY_SELECT = "#priority"
    CATEGORY_INPUT = "#category"
    SUBMIT_BUTTON = 'button:has-text("Create Task")'
    CANCEL_BUTTON = 'button:has-text("Cancel")'


class TaskModal:
    """Component for task creation/edit modal interactions."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.selectors = TaskModalSelectors()

    @property
    def modal(self) -> Locator:
        """Get modal locator."""
        return self.page.locator(self.selectors.MODAL)

    def expect_visible(self) -> TaskModal:
        """Assert modal is visible."""
        with allure.step("Verify task modal is visible"):
            expect(self.modal).to_be_visible()
        return self

    def expect_hidden(self) -> TaskModal:
        """Assert modal is hidden."""
        with allure.step("Verify task modal is hidden"):
            expect(self.modal).to_be_hidden()
        return self

    def fill_title(self, title: str) -> TaskModal:
        """Fill the title field."""
        with allure.step(f"Fill title: {title}"):
            self.page.fill(self.selectors.TITLE_INPUT, title)
        return self

    def fill_description(self, description: str) -> TaskModal:
        """Fill the description field."""
        with allure.step(f"Fill description: {description[:50]}..."):
            self.page.fill(self.selectors.DESCRIPTION_INPUT, description)
        return self

    def select_priority(self, priority: str) -> TaskModal:
        """Select priority from dropdown."""
        with allure.step(f"Select priority: {priority}"):
            self.page.select_option(self.selectors.PRIORITY_SELECT, priority)
        return self

    def fill_category(self, category: str) -> TaskModal:
        """Fill the category field."""
        with allure.step(f"Fill category: {category}"):
            self.page.fill(self.selectors.CATEGORY_INPUT, category)
        return self

    def fill_task_form(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        category: str = "",
    ) -> TaskModal:
        """Fill the task form fields.

        Args:
            title: Task title (required)
            description: Task description (optional)
            priority: Task priority - low/medium/high (default: medium)
            category: Task category (optional)

        Returns:
            Self for method chaining
        """
        with allure.step("Fill task form"):
            self.fill_title(title)

            if description:
                self.fill_description(description)

            if priority:
                self.select_priority(priority)

            if category:
                self.fill_category(category)

        return self

    def submit(self) -> TaskModal:
        """Submit the task form."""
        with allure.step("Submit task form"):
            self.page.click(self.selectors.SUBMIT_BUTTON)
        return self

    def cancel(self) -> TaskModal:
        """Cancel and close the modal."""
        with allure.step("Click cancel button"):
            self.page.click(self.selectors.CANCEL_BUTTON)
        return self

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        category: str = "",
    ) -> TaskModal:
        """Fill form and submit to create task.

        Convenience method that fills and submits in one call.
        """
        self.fill_task_form(title, description, priority, category)
        self.submit()
        self.expect_hidden()
        return self
