"""Task card component for task interactions on dashboard."""

from __future__ import annotations

import re
from dataclasses import dataclass

import allure
from playwright.sync_api import Locator, Page, expect

from tests.common.factories.task import TaskData


@dataclass(frozen=True)
class TaskCardSelectors:
    """Selectors relative to task card."""

    DROPDOWN_TOGGLE = "#dropdown-toggle"
    COMPLETE_BUTTON = "#complete-button"
    DELETE_BUTTON = "#delete-button"
    CARD_TITLE = "#card-title"
    CARD_DESCRIPTION = "#card-description"
    PRIORITY_BADGE = "#card-priority"
    CATEGORY_BADGE = "#card-category"


class TaskCard:
    """Component for individual task card interactions."""

    COMPLETED_CLASS = "completed-task"

    def __init__(self, page: Page, card_selector: str) -> None:
        self.page = page
        self.card_selector = card_selector
        self.selectors = TaskCardSelectors()

    @classmethod
    def from_title(cls, page: Page, title: str) -> TaskCard:
        """Create TaskCard instance by finding card with given title.

        Uses a more specific selector that matches the card title element
        to avoid matching cards where the title appears in other text.
        """
        # Use card-title for more precise matching
        selector = f'.card:has(.card-title:text-is("{title}"))'
        return cls(page, selector)

    @property
    def card(self) -> Locator:
        """Get card locator."""
        return self.page.locator(self.card_selector).first

    def expect_visible(self) -> TaskCard:
        """Assert card is visible."""
        with allure.step("Verify task card is visible"):
            expect(self.card).to_be_visible()
        return self

    def expect_not_visible(self) -> TaskCard:
        """Assert card is not visible."""
        with allure.step("Verify task card is not visible"):
            expect(self.card).not_to_be_visible()
        return self

    def open_dropdown(self) -> TaskCard:
        """Open the task dropdown menu."""
        with allure.step("Open task dropdown menu"):
            dropdown = self.card.locator(self.selectors.DROPDOWN_TOGGLE)
            dropdown.click()
        return self

    def mark_complete(self) -> TaskCard:
        """Mark the task as complete."""
        with allure.step("Click Mark Complete"):
            self.open_dropdown()
            complete_btn = self.card.locator(self.selectors.COMPLETE_BUTTON)
            expect(complete_btn).to_be_visible()
            complete_btn.click()
        return self

    def expect_completed(self) -> TaskCard:
        """Assert task is marked as completed (has completed-task class)."""
        with allure.step("Verify task is completed"):
            expect(self.card).to_have_class(re.compile(self.COMPLETED_CLASS))
        return self

    def delete(self) -> TaskCard:
        """Delete the task and wait for removal."""
        # Set up dialog handler before opening dropdown to avoid race condition
        self.page.on("dialog", lambda dialog: dialog.accept())

        with allure.step("Click Delete and handle confirmation"):
            self.open_dropdown()
            delete_btn = self.card.locator(self.selectors.DELETE_BUTTON)
            expect(delete_btn).to_be_visible()
            delete_btn.click()
            expect(self.card).not_to_be_visible()

        return self

    def get_title(self) -> Locator:
        """Get the task title text."""
        return self.card.locator(self.selectors.CARD_TITLE)

    def expect_title(self, title: str) -> TaskCard:
        """Assert task has specific priority badge."""
        with allure.step(f"Verify task has '{title}' title"):
            card_title = self.get_title()
            expect(card_title).to_contain_text(title, ignore_case=True)
        return self

    def get_description(self) -> Locator:
        """Get the task description text."""
        return self.card.locator(self.selectors.CARD_DESCRIPTION)

    def expect_description(self, description: str) -> TaskCard:
        """Assert task has specific priority badge."""
        with allure.step(f"Verify task has '{description}' description"):
            card_description = self.get_description()
            expect(card_description).to_contain_text(description, ignore_case=True)
        return self

    def get_priority_badge(self) -> Locator:
        """Get priority badge with specific text."""
        return self.card.locator(f"{self.selectors.PRIORITY_BADGE}")

    def expect_priority(self, priority: str) -> TaskCard:
        """Assert task has specific priority badge."""
        with allure.step(f"Verify task has '{priority}' priority"):
            priority_badge = self.get_priority_badge()
            expect(priority_badge).to_contain_text(priority, ignore_case=True)
        return self

    def get_category_badge(self) -> Locator:
        """Get priority badge with specific text."""
        return self.card.locator(f"{self.selectors.CATEGORY_BADGE}")

    def expect_category(self, category: str) -> TaskCard:
        """Assert task has specific priority badge."""
        with allure.step(f"Verify task has '{category}' priority"):
            category_badge = self.get_category_badge()
            expect(category_badge).to_contain_text(category, ignore_case=True)
        return self

    def verify_content(self, task: TaskData):
        (
            self.expect_visible()
            .expect_title(task.title)
            .expect_description(task.description)
            .expect_priority(task.priority)
            .expect_category(task.category)
        )
