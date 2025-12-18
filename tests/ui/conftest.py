"""
UI-specific pytest fixtures for Playwright testing with Allure integration.

Shared fixtures (api_client, api_base_url, credentials) are inherited from
tests/conftest.py. This file contains only UI-specific fixtures:
- Playwright browser, context, page management
- Screenshot and trace capture on failure
- Page Object fixtures (LoginPage, RegisterPage, DashboardPage)

Environment variables are loaded from .env.test by pytest-dotenv plugin.

Fixture scopes:
- Playwright session (singleton): Reused across all tests
- Browser (session): Reused across all tests
- Browser context (function): Fresh context per test
- Page (function): Fresh page per test with global timeouts

This enables:
- Full test isolation (no state bleed between tests)
- Parallel execution (4+ workers via pytest-xdist)
- Trace recording on failure for debugging
- Fast authenticated UI tests (API-based login, no UI registration/login)
"""

from pathlib import Path
from typing import Generator

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from tests.common.constants import Routes
from tests.common.utils import get_screenshot_path
from tests.config import config
from tests.ui.pages import DashboardPage, LoginPage, RegisterPage

# ============================================================================
# Playwright Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def playwright_session():
    """Session-scoped Playwright instance - reused across all tests."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser_type_launch_args() -> dict:
    """Browser launch arguments"""
    return {
        "headless": config.HEADLESS,
        "slow_mo": config.SLOW_MO if not config.HEADLESS else 0,
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080",
        ],
    }


@pytest.fixture(scope="session")
def browser(playwright_session, browser_type_launch_args) -> Generator[Browser, None, None]:
    """One browser instance per session."""
    browser = playwright_session.chromium.launch(**browser_type_launch_args)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def browser_context_args() -> dict:
    """Browser context arguments - fresh per test."""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "accept_downloads": True,
        "color_scheme": "dark",
    }


@pytest.fixture(scope="function")
def browser_context(browser: Browser, browser_context_args) -> Generator[BrowserContext, None, None]:
    """Fresh browser context per test."""
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(browser_context: BrowserContext, request) -> Generator[Page, None, None]:
    """Page fixture with tracing, screenshot on failure, and timeout configuration.

    Features:
    - Global timeout of 10 seconds per repo standards
    - Trace recording (saved on failure for debugging)
    - Screenshot capture on failure
    - Traces include: network, DOM, screenshot snapshots
    """
    # Start trace recording
    browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)

    page = browser_context.new_page()
    page.set_default_timeout(10000)  # 10 seconds
    page.set_default_navigation_timeout(10000)

    yield page

    # Handle failure artifacts (screenshot + trace)
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
        test_name = request.node.name

        # Take screenshot on failure
        screenshot_path = get_screenshot_path(f"{test_name}_failure.png")
        page.screenshot(path=screenshot_path, full_page=True)
        with open(screenshot_path, "rb") as screenshot_file:
            allure.attach(
                screenshot_file.read(),
                name=f"Screenshot on failure: {test_name}",
                attachment_type=allure.attachment_type.PNG,
            )

        # Save trace on failure
        trace_path = Path(get_screenshot_path(f"{test_name}_trace.zip"))
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        browser_context.tracing.stop(path=str(trace_path))
        with open(trace_path, "rb") as f:
            allure.attach(
                f.read(),
                name=f"Trace: {test_name}",
                attachment_type="application/zip",
            )
    else:
        browser_context.tracing.stop()

    page.close()


# ============================================================================
# Credential Fixture - Alias for UI tests
# ============================================================================


@pytest.fixture(scope="function")
def test_user_credentials(ui_test_user_credentials):
    """Alias ui_test_user_credentials for backward compatibility.

    UI tests use the 'ui_user_' prefix for test users.
    """
    return ui_test_user_credentials


# ============================================================================
# User Registration and Authentication Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def registered_test_user(api_client, api_base_url, test_user_credentials):
    """Register a new test user via API (fast, deterministic).

    Returns dict with user credentials and ID.
    Cleanup is handled by pytest_sessionfinish in root conftest.
    """
    with allure.step(f"Register test user via API: {test_user_credentials['username']}"):
        response = api_client.post(
            f"{api_base_url}/api/users/",
            json=test_user_credentials,
            timeout=10,
        )
        assert response.status_code == 201, f"Failed to register user: {response.text}"
        user_data = response.json()
        allure.attach(
            f"Username: {test_user_credentials['username']}\nEmail: {test_user_credentials['email']}",
            name="Test User Created",
            attachment_type=allure.attachment_type.TEXT,
        )

    yield {**test_user_credentials, "id": user_data.get("id")}


@pytest.fixture(scope="function")
def authenticated_page(page: Page, registered_test_user) -> Page:
    """Provide an authenticated Playwright page ready for testing.

    This fixture:
    1. Registers user via API (fast, ~1 second)
    2. Authenticates via API using page.request context (no UI interactions)
    3. Navigates to dashboard
    4. Returns page already logged in and ready for testing

    Benefits:
    - Faster than UI login: No form filling/clicking, pure HTTP
    - Reliable: Uses Playwright's page.request for proper cookie/session handling
    - Tests Flask session: Flask /login endpoint is called with credentials
    - Deterministic: No timing-dependent UI waits

    Use this for all feature tests (task creation, filtering, etc).
    Only use plain 'page' fixture for form validation tests.
    """
    with allure.step("Login via API (page.request context)"):
        login_response = page.request.post(
            f"{config.FRONTEND_URL}/login",
            form={
                "username": registered_test_user["username"],
                "password": registered_test_user["password"],
            },
        )
        assert login_response.status == 200, f"Login failed with status {login_response.status}: {login_response.text}"
        allure.attach(
            f"User: {registered_test_user['username']}\nLogin Status: {login_response.status}",
            name="API Login Result",
            attachment_type=allure.attachment_type.TEXT,
        )

    with allure.step("Navigate to dashboard"):
        page.goto(f"{config.FRONTEND_URL}{Routes.DASHBOARD}")
        page.wait_for_url(f"{config.FRONTEND_URL}{Routes.DASHBOARD}")

    return page


# ============================================================================
# Page Object Fixtures - Use these for clean, maintainable tests
# ============================================================================


@pytest.fixture(scope="function")
def login_page(page: Page):
    """Provide LoginPage object for unauthenticated login tests.

    Use this fixture when testing:
    - Login form validation
    - Invalid credentials
    - Navigation to register

    Example:
        def test_login_failure(login_page):
            login_page.open()
            login_page.login_and_expect_failure("wrong", "credentials")
    """
    return LoginPage(page, config.FRONTEND_URL)


@pytest.fixture(scope="function")
def register_page(page: Page):
    """Provide RegisterPage object for registration tests.

    Example:
        def test_registration(register_page):
            register_page.open()
            register_page.register_and_expect_success("user", "email@test.com", "pass")
    """
    return RegisterPage(page, config.FRONTEND_URL)


@pytest.fixture(scope="function")
def dashboard_page(authenticated_page: Page):
    """Provide DashboardPage object (already authenticated).

    This fixture:
    1. Uses authenticated_page (user already logged in)
    2. Returns DashboardPage ready for task operations

    Example:
        def test_create_task(dashboard_page):
            dashboard_page.create_task(title="My Task")
            dashboard_page.expect_task_exists("My Task")
    """
    return DashboardPage(authenticated_page, config.FRONTEND_URL)
