from dataclasses import dataclass


@dataclass(frozen=True)
class Routes:
    ROOT = "/"
    LOGIN = "/login"
    LOGOUT = "/logout"
    REGISTER = "/register"
    DASHBOARD = "/dashboard"
