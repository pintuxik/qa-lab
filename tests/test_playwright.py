"""
Sample Playwright tests with Allure annotations.
"""

import allure
from playwright.sync_api import Page, expect


class TestPlaywrightSample:
    """Sample Playwright test class with Allure annotations."""

    @allure.feature("Web UI Testing")
    @allure.story("Basic Navigation")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Test basic navigation to example.com")
    def test_example_homepage(self, page: Page):
        """Test navigation to example.com."""
        with allure.step("Navigate to example.com"):
            page.goto("https://example.com")

        with allure.step("Verify page title"):
            expect(page).to_have_title("Example Domain")

        with allure.step("Verify main heading is visible"):
            heading = page.locator("h1")
            expect(heading).to_be_visible()
            expect(heading).to_contain_text("Example Domain")

    @allure.feature("Web UI Testing")
    @allure.story("Page Interaction")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Test page interaction and screenshot")
    def test_page_interaction(self, page: Page):
        """Test page interaction capabilities."""
        with allure.step("Navigate to example.com"):
            page.goto("https://example.com")

        with allure.step("Verify page content"):
            expect(page.locator("h1")).to_contain_text("Example Domain")

        with allure.step("Take screenshot for verification"):
            page.screenshot(path="example_page.png", full_page=True)

            # Attach screenshot to Allure
            with open("example_page.png", "rb") as f:
                allure.attach(f.read(), name="Example page screenshot", attachment_type=allure.attachment_type.PNG)

    @allure.feature("Web UI Testing")
    @allure.story("Error Handling")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("Test error handling with invalid URL")
    def test_error_handling(self, page: Page):
        """Test error handling capabilities."""
        with allure.step("Navigate to example.com"):
            page.goto("https://example.com")

        with allure.step("Verify page loads correctly"):
            expect(page.locator("h1")).to_contain_text("Example Domain")

        with allure.step("Test page navigation"):
            # This should work without issues
            expect(page).to_have_url("https://example.com/")

    @allure.feature("Web UI Testing")
    @allure.story("Screenshot on Failure")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("Test screenshot on failure functionality")
    def test_screenshot_on_failure(self, page: Page):
        """Test screenshot on failure functionality."""
        with allure.step("Navigate to example.com"):
            page.goto("https://example.com")

        with allure.step("Intentionally fail test to trigger screenshot"):
            # This assertion will fail and trigger screenshot
            expect(page.locator("h1")).to_contain_text("Wrong Text")
