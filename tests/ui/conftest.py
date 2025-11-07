"""
Global pytest configuration for Playwright testing with Allure integration.

Fixture scopes:
- Playwright session (singleton): Reused across all tests
- Browser (function): Created fresh per test for isolation
- Browser context (function): Fresh context per test
- Page (function): Fresh page per test with global timeouts

This enables:
✅ Full test isolation (no state bleed between tests)
✅ Parallel execution (4+ workers via pytest-xdist)
✅ Trace recording on failure for debugging
✅ Proper cleanup even on hard errors
✅ Fast authenticated UI tests (API-based login, no UI registration/login)
"""

import os
import uuid
from pathlib import Path
from typing import Generator

import allure
import pytest
import requests
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from utils.utils import get_screenshot_path

# URLs
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5001")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def playwright_session():
    """Session-scoped Playwright instance - reused across all tests."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="function")
def browser_type_launch_args():
    """Function-scoped browser launch args - can vary per test if needed."""
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    return {
        "headless": headless,  # Set via HEADLESS env var
        "slow_mo": 300 if not headless else 0,  # Slow down for visibility in headed mode
        "args": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--window-size=1920,1080"],
    }


@pytest.fixture(scope="function")
def browser_context_args():
    """Function-scoped browser context args - fresh per test."""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "accept_downloads": True,
    }


@pytest.fixture(scope="function")
def browser(playwright_session, browser_type_launch_args) -> Generator[Browser, None, None]:
    """Function-scoped browser fixture - fresh browser per test.

    This ensures:
    - Full test isolation (no state/cookies carry over)
    - Enables parallel execution with pytest-xdist
    - Each test starts with clean browser instance
    """
    browser = playwright_session.chromium.launch(**browser_type_launch_args)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def browser_context(browser: Browser, browser_context_args) -> Generator[BrowserContext, None, None]:
    """Function-scoped browser context - fresh context per test.

    Always runs after browser fixture, ensuring proper cleanup order.
    """
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(browser_context: BrowserContext, request) -> Generator[Page, None, None]:
    """Function-scoped page fixture with:
    - Global timeout configuration (10s per repo standards)
    - Trace recording on failure for debugging

    Traces include: network, DOM, screenshot snapshots.
    Saved on failure to help debug flaky tests.
    """
    # Start trace recording
    browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)

    page = browser_context.new_page()

    # Set global default timeout to 10 seconds per repo standards
    page.set_default_timeout(10000)  # 10 seconds
    page.set_default_navigation_timeout(10000)  # 10 seconds

    yield page

    # Stop trace and save on failure
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
        trace_path = Path(get_screenshot_path(f"{request.node.name}_trace.zip"))
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        browser_context.tracing.stop(path=str(trace_path))

        # Attach trace to Allure
        with open(trace_path, "rb") as f:
            allure.attach(
                f.read(),
                name=f"Trace: {request.node.name}",
                attachment_type="application/zip",
            )
    else:
        browser_context.tracing.stop()

    page.close()


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, page):
    """Automatically take screenshot on test failure and attach to Allure."""
    yield

    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
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


# ============================================================================
# Authenticated UI Test Fixtures - Fast API-based Login for Task Tests
# ============================================================================


@pytest.fixture(scope="function")
def api_session():
    """Provide a requests session with global timeout for API calls."""
    session = requests.Session()
    session.timeout = 10  # 10 seconds default timeout
    return session


@pytest.fixture(scope="function")
def test_user_credentials():
    """Generate unique test user credentials per test."""
    unique_id = str(uuid.uuid4())[:8]  # First 8 chars of UUID
    return {
        "username": f"uiuser_{unique_id}",
        "email": f"uiuser_{unique_id}@example.com",
        "password": "TestPass123!",
    }


@pytest.fixture(scope="function")
def registered_test_user(api_session, test_user_credentials):
    """Register a new test user via API (fast, deterministic).

    Returns dict with user credentials and ID.
    """
    with allure.step("Register test user via API"):
        response = api_session.post(
            f"{API_BASE_URL}/api/auth/register",
            json=test_user_credentials,
            timeout=10,
        )
        assert response.status_code == 200, f"Failed to register user: {response.text}"
        user_data = response.json()

        allure.attach(
            f"Username: {test_user_credentials['username']}\nEmail: {test_user_credentials['email']}",
            name="Test User Created",
            attachment_type=allure.attachment_type.TEXT,
        )

    return {**test_user_credentials, "id": user_data.get("id")}


@pytest.fixture(scope="function")
def authenticated_page(page: Page, registered_test_user):
    """Provide an authenticated Playwright page ready for testing via API-based login.

    This fixture:
    1. Registers user via API (fast, ~1 second)
    2. Authenticates via API using page.request context (no UI interactions)
    3. Navigates to dashboard
    4. Returns page already logged in and ready for testing

    ✅ Faster than UI login: No form filling/clicking, pure HTTP
    ✅ Reliable: Uses Playwright's page.request for proper cookie/session handling
    ✅ Tests Flask session: Flask /login endpoint is called with credentials
    ✅ Deterministic: No timing-dependent UI waits

    Use this for all feature tests (task creation, filtering, etc).
    Only use plain 'page' fixture for form validation tests.

    Example:
        def test_create_task(authenticated_page):
            # Already logged in, on dashboard
            authenticated_page.click('button:has-text("Add Task")')
    """
    with allure.step("Login via API (page.request context)"):
        # Use page.request.post() to make login call within browser context
        # This ensures all cookies and session data are properly set
        # and respects the browser's cookie jar
        login_response = page.request.post(
            f"{FRONTEND_URL}/login",
            form={
                "username": registered_test_user["username"],
                "password": registered_test_user["password"],
            },
        )
        # Flask redirects after successful login (HTTP 302 or returns 200)
        assert login_response.status in [
            200,
            302,
        ], f"Login failed with status {login_response.status}: {login_response.text}"

        allure.attach(
            f"User: {registered_test_user['username']}\nLogin Status: {login_response.status}",
            name="API Login Result",
            attachment_type=allure.attachment_type.TEXT,
        )

    with allure.step("Navigate to dashboard"):
        page.goto(f"{FRONTEND_URL}/dashboard")
        page.wait_for_url(f"{FRONTEND_URL}/dashboard")

    return page
