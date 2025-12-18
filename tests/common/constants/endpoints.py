from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoints:
    AUTH = "/api/auth"
    TASKS = "/api/tasks"
    USERS = "/api/users"
