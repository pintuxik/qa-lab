"""Page Object Model classes for UI tests."""

from .base_page import BasePage
from .dashboard_page import DashboardPage
from .login_page import LoginPage
from .register_page import RegisterPage

__all__ = ["BasePage", "LoginPage", "RegisterPage", "DashboardPage"]
