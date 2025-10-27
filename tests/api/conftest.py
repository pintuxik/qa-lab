"""
Global pytest configuration for API testing with Allure integration.
"""

import allure
import pytest


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
