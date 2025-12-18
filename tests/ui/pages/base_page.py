"""Base page class providing common functionality for all page objects."""

from __future__ import annotations

from dataclasses import dataclass

import allure
from playwright.sync_api import Locator, Page, expect

from tests.common.constants import Routes


@dataclass(frozen=True)
class CommonSelectors:
    """Common selectors shared across pages."""

    ALERT_SUCCESS = "#alert.alert-success"
    ALERT_DANGER = "#alert.alert-danger"
    LOGOUT_LINK = "#logout"


class BasePage:
    """Base class for all page objects.

    Provides:
    - Navigation with URL verification
    - Common element interactions with Allure steps
    - Alert message handling
    - Wait utilities
    """

    URL_PATH: str = Routes.ROOT

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.selectors = CommonSelectors()

    @property
    def url(self) -> str:
        """Full URL for this page."""
        return f"{self.base_url}{self.URL_PATH}"

    def open(self) -> BasePage:
        """Navigate to this page and verify URL."""
        with allure.step(f"Navigate to {self.URL_PATH}"):
            self.page.goto(self.url)
            expect(self.page).to_have_url(self.url)
        return self

    def try_to_navigate(self, expected_route: str | None = None) -> BasePage:
        """Try to navigate to this page or expected route"""
        target_url = f"{self.base_url}{expected_route}" if expected_route else self.url
        with allure.step(f"Try to navigate to {expected_route}"):
            self.page.goto(target_url)
        return self

    def wait_for_navigation(self, expected_path: str | None = None) -> None:
        """Wait for navigation to complete."""
        target_url = f"{self.base_url}{expected_path}" if expected_path else self.url
        self.page.wait_for_url(target_url)
        expect(self.page).to_have_url(target_url)

    def get_alert_success(self) -> Locator:
        """Get success alert locator."""
        return self.page.locator(self.selectors.ALERT_SUCCESS)

    def get_alert_danger(self) -> Locator:
        """Get danger/error alert locator."""
        return self.page.locator(self.selectors.ALERT_DANGER)

    def expect_success_alert(self, message: str | None = None) -> BasePage:
        """Assert success alert is visible, optionally with specific message."""
        with allure.step("Verify success message"):
            alert = self.get_alert_success()
            expect(alert).to_be_visible()
            if message:
                expect(alert).to_contain_text(message)
        return self

    def expect_error_alert(self, message: str | None = None) -> BasePage:
        """Assert error alert is visible, optionally with specific message."""
        with allure.step("Verify error message"):
            alert = self.get_alert_danger()
            expect(alert).to_be_visible()
            if message:
                expect(alert).to_contain_text(message)
        return self

    def fill_field(self, selector: str, value: str, field_name: str = "") -> BasePage:
        """Fill a form field with Allure step."""
        step_name = f"Fill {field_name}" if field_name else f"Fill {selector}"
        with allure.step(step_name):
            self.page.fill(selector, value)
        return self

    def click_element(self, selector: str, element_name: str = "") -> BasePage:
        """Click an element with Allure step."""
        step_name = f"Click {element_name}" if element_name else f"Click {selector}"
        with allure.step(step_name):
            self.page.click(selector)
        return self

    def select_option(self, selector: str, value: str, field_name: str = "") -> BasePage:
        """Select an option from dropdown with Allure step."""
        step_name = f"Select {value} for {field_name}" if field_name else f"Select {value}"
        with allure.step(step_name):
            self.page.select_option(selector, value)
        return self

    def is_on_page(self) -> bool:
        """Check if currently on this page."""
        return self.page.url == self.url

    def expect_heading(self, text: str) -> BasePage:
        """Assert page has a heading with given text."""
        with allure.step(f"Verify heading: {text}"):
            heading = self.page.locator(f'h1:has-text("{text}"), h2:has-text("{text}")')
            expect(heading).to_be_visible()
        return self

    def logout(self) -> None:
        """Logout and redirect to login page."""
        with allure.step("Click logout"):
            self.page.click(self.selectors.LOGOUT_LINK)
        with allure.step("Verify redirect to login"):
            self.wait_for_navigation(Routes.LOGIN)
