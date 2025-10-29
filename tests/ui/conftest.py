"""
Global pytest configuration for Playwright testing with Allure integration.
"""

from typing import Generator

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from utils.utils import get_screenshot_path


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Configure browser launch arguments for Chrome."""
    import os

    headless = os.getenv("HEADLESS", "false").lower() == "true"
    return {
        "headless": headless,  # Set via HEADLESS env var
        "slow_mo": 500 if not headless else 0,  # Slow down for visibility in headed mode
        "args": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--window-size=1920,1080"],
    }


@pytest.fixture(scope="session")
def browser_type():
    """Set default browser type to Chrome."""
    return "chromium"


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context arguments."""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "accept_downloads": True,
    }


@pytest.fixture(scope="session")
def playwright_browser(browser_type_launch_args, browser_type) -> Generator[Browser, None, None]:
    """Session-scoped browser fixture."""
    with sync_playwright() as p:
        browser = p.chromium.launch(**browser_type_launch_args)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def browser_context(playwright_browser: Browser, browser_context_args) -> Generator[BrowserContext, None, None]:
    """Function-scoped browser context fixture."""
    context = playwright_browser.new_context(**browser_context_args)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(browser_context: BrowserContext) -> Generator[Page, None, None]:
    """Function-scoped page fixture."""
    page = browser_context.new_page()
    yield page
    page.close()


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, page):
    """Automatically take screenshot on test failure and attach to Allure."""
    yield

    if request.node.rep_call.failed:
        test_name = request.node.name
        screenshot_path = get_screenshot_path(f"{test_name}_failure.png")

        # Take screenshot
        page.screenshot(path=screenshot_path, full_page=True)

        # Attach to Allure report
        with open(screenshot_path, "rb") as screenshot_file:
            allure.attach(
                screenshot_file.read(),
                name=f"Screenshot on failure: {test_name}",
                attachment_type=allure.attachment_type.PNG,
            )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for screenshot on failure."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def allure_environment_info():
    """Add environment information to Allure report."""
    allure.dynamic.label("framework", "pytest")
    allure.dynamic.label("browser", "chromium")
    allure.dynamic.label("test_type", "ui")
