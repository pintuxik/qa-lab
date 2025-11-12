"""Shared test data, constants, and helper functions for tests."""

from datetime import datetime


# API Endpoints
class Endpoints:
    """API endpoint constants."""

    # Auth endpoints
    AUTH_REGISTER = "/api/auth/register"
    AUTH_LOGIN = "/api/auth/login"

    # Task endpoints
    TASKS = "/api/tasks"
    TASK_BY_ID = "/api/tasks/{task_id}"

    # Main endpoints
    ROOT = "/"
    HEALTH = "/health"
    OPENAPI = "/openapi.json"
    DOCS = "/docs"
    REDOC = "/redoc"

    @staticmethod
    def task_by_id(task_id: int) -> str:
        """Get task endpoint with specific ID."""
        return f"/api/tasks/{task_id}"


# Test User Data
class TestUsers:
    """Test user data constants."""

    VALID_USER = {"email": "test@example.com", "username": "testuser", "password": "TestPass123!"}

    VALID_USER_2 = {"email": "user2@example.com", "username": "testuser2", "password": "TestPass123!"}

    ADMIN_USER = {"email": "admin@example.com", "username": "admin", "password": "Admin123!"}

    NEW_USER = {"email": "newuser@example.com", "username": "newuser", "password": "NewPass123!"}

    # Additional test users for multi-user scenarios
    OTHER_USER = {"email": "other@example.com", "username": "otheruser", "password": "OtherPass123!"}

    OTHER_USER_2 = {"email": "other2@example.com", "username": "otheruser2", "password": "OtherPass123!"}

    OTHER_USER_3 = {"email": "other3@example.com", "username": "otheruser3", "password": "OtherPass123!"}

    # Generic password for test scenarios
    GENERIC_PASSWORD = "TestPass123!"
    OTHER_PASSWORD = "otherpass"

    # Invalid passwords for testing
    WEAK_PASSWORDS = {
        "no_uppercase": "testpass123!",
        "no_lowercase": "TESTPASS123!",
        "no_digit": "TestPass!",
        "no_special": "TestPass123",
        "too_short": "Test1!",
        "empty": "",
    }

    # Invalid usernames
    INVALID_USERNAMES = {
        "empty": "",
        "too_short": "ab",
        "too_long": "a" * 31,
        "special_chars": "test@user",
        "unicode": "用户",
        "sql_injection": "admin' OR '1'='1",
        "xss": "<script>alert('xss')</script>",
    }

    # Invalid emails
    INVALID_EMAILS = {"empty": "", "no_at": "testexample.com", "no_domain": "test@", "invalid_format": "not-an-email"}


# Test Task Data
class TestTasks:
    """Test task data constants."""

    VALID_TASK = {"title": "Test Task", "description": "This is a test task", "priority": "high", "category": "testing"}

    MINIMAL_TASK = {"title": "Minimal Task"}

    TASK_WITH_PRIORITY = {"title": "Priority Task", "priority": "low"}

    COMPLETED_TASK = {"title": "Completed Task", "is_completed": True}

    # Full task payload with all fields
    FULL_TASK = {"title": "New Task", "description": "Task description", "priority": "high", "category": "work"}

    # Task update payloads
    UPDATE_TITLE = {"title": "Updated Title"}
    UPDATE_COMPLETION = {"is_completed": True}
    UPDATE_PRIORITY = {"priority": "low"}
    UPDATE_MULTIPLE = {
        "title": "Updated Task",
        "description": "Updated description",
        "priority": "medium",
        "is_completed": True,
    }

    # Valid priority values
    VALID_PRIORITIES = ["low", "medium", "high"]
    # Invalid priority values
    INVALID_PRIORITIES = ["urgent", "invalid"]

    # Invalid task data
    INVALID_TASKS = {
        "empty_title": {"title": ""},
        "missing_title": {"description": "No title"},
        "long_title": {"title": "A" * 101},
        "long_description": {"title": "Task", "description": "B" * 501},
        "invalid_priority": {"title": "Task", "priority": "urgent"},
        "null_title": {"title": None},
    }


# HTTP Status Code Messages
class StatusMessages:
    """Common status code assertion messages."""

    UNAUTHORIZED = "Should return 401 for unauthorized access"
    FORBIDDEN = "Should return 403 for forbidden access"
    NOT_FOUND = "Should return 404 for not found"
    VALIDATION_ERROR = "Should return 422 for validation error"
    BAD_REQUEST = "Should return 400 for bad request"
    SUCCESS = "Should return 200 for successful request"
    CREATED = "Should return 201 for successful creation"


# Test Helper Functions
class TestHelpers:
    """Helper functions for tests."""

    @staticmethod
    def create_auth_headers(token: str) -> dict:
        """Create authorization headers with token."""
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def create_task_payload(title: str = "Test Task", **kwargs) -> dict:
        """Create a task payload with optional overrides."""
        payload = {"title": title}
        payload.update(kwargs)
        return payload

    @staticmethod
    def create_user_payload(username: str = "testuser", **kwargs) -> dict:
        """Create a user registration payload with optional overrides."""
        payload = {"email": f"{username}@example.com", "username": username, "password": "TestPass123!"}
        payload.update(kwargs)
        return payload

    @staticmethod
    def assert_error_in_response(response_json: dict, field: str):
        """Assert that an error for a specific field exists in the response."""
        assert "detail" in response_json, "Response should contain error details"
        # Pydantic validation errors have a specific structure
        if isinstance(response_json["detail"], list):
            field_errors = [error for error in response_json["detail"] if field in str(error.get("loc", []))]
            assert len(field_errors) > 0, f"No validation error found for field: {field}"
        else:
            assert field in str(response_json["detail"]), f"Field {field} not in error message"

    @staticmethod
    def assert_valid_task_response(task_data: dict):
        """Assert that task response contains all required fields."""
        required_fields = ["id", "title", "is_completed", "priority", "created_at", "owner_id"]
        for field in required_fields:
            assert field in task_data, f"Task response missing required field: {field}"

    @staticmethod
    def assert_valid_user_response(user_data: dict):
        """Assert that user response contains all required fields."""
        required_fields = ["id", "email", "username", "is_active", "is_admin", "created_at"]
        for field in required_fields:
            assert field in user_data, f"User response missing required field: {field}"
        # Ensure password is not in response
        assert "password" not in user_data, "User response should not contain password"
        assert "hashed_password" not in user_data, "User response should not contain hashed_password"

    @staticmethod
    def create_and_login_user(client, db_session, username: str, email: str, password: str) -> dict:
        """
        Create a new user in database, login, and return auth headers.

        Args:
            client: FastAPI test client
            db_session: Database session
            username: Username for new user
            email: Email for new user
            password: Password for new user (will be hashed)

        Returns:
            dict: Authorization headers with bearer token
        """
        from app.core.security import get_password_hash
        from app.models import User

        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        # Login to get token
        response = client.post(Endpoints.AUTH_LOGIN, data={"username": username, "password": password})
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def create_test_user(
        db_session,
        username: str = "testuser",
        email: str = "test@example.com",
        password: str = "TestPass123!",
        is_active: bool = True,
        is_admin: bool = False,
    ):
        """
        Create a test user in the database.

        Args:
            db_session: Database session
            username: Username (default: "testuser")
            email: Email (default: "test@example.com")
            password: Plain password to be hashed (default: "TestPass123!")
            is_active: User active status (default: True)
            is_admin: Admin status (default: False)

        Returns:
            User: Created user object
        """
        from app.core.security import get_password_hash
        from app.models import User

        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_active=is_active,
            is_admin=is_admin,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @staticmethod
    def create_test_task(db_session, owner_id: int, title: str = "Test Task", **kwargs):
        """
        Create a test task in the database.

        Args:
            db_session: Database session
            owner_id: ID of the task owner
            title: Task title (default: "Test Task")
            **kwargs: Additional task fields (description, priority, category, is_completed)

        Returns:
            Task: Created task object
        """
        from app.models import Task

        task = Task(title=title, owner_id=owner_id, **kwargs)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task

    @staticmethod
    def get_validation_error_fields(exc_info) -> list[str]:
        """
        Extract field names from Pydantic ValidationError.

        Args:
            exc_info: pytest ExceptionInfo from pytest.raises(ValidationError)

        Returns:
            list[str]: List of field names that had validation errors
        """
        errors = exc_info.value.errors()
        return [error["loc"][0] for error in errors]

    @staticmethod
    def assert_validation_error_on_field(exc_info, field: str):
        """
        Assert that a specific field has a validation error.

        Args:
            exc_info: pytest ExceptionInfo from pytest.raises(ValidationError)
            field: Field name to check for error
        """
        errors = exc_info.value.errors()
        assert any(
            error["loc"] == (field,) for error in errors
        ), f"Expected validation error on field '{field}', but got errors on: {[e['loc'] for e in errors]}"

    @staticmethod
    def assert_validation_error_type(exc_info, field: str, error_type: str):
        """
        Assert that a specific field has a validation error of a specific type.

        Args:
            exc_info: pytest ExceptionInfo from pytest.raises(ValidationError)
            field: Field name to check
            error_type: Expected error type (e.g., "string_too_short", "literal_error")
        """
        errors = exc_info.value.errors()
        assert any(
            error["loc"] == (field,) and error["type"] == error_type for error in errors
        ), f"Expected '{error_type}' error on field '{field}'"

    @staticmethod
    def assert_validation_error_on_fields(exc_info, *fields: str):
        """
        Assert that multiple fields have validation errors.

        Args:
            exc_info: pytest ExceptionInfo from pytest.raises(ValidationError)
            *fields: Variable number of field names to check for errors
        """
        errors = exc_info.value.errors()
        error_fields = {error["loc"][0] for error in errors if error["loc"]}

        for field in fields:
            assert (
                field in error_fields
            ), f"Expected validation error on field '{field}', but got errors on: {error_fields}"

    @staticmethod
    def get_current_datetime() -> datetime:
        """
        Get current datetime for tests. Centralizes datetime.now() calls.

        Returns:
            datetime: Current datetime
        """
        return datetime.now()

    @staticmethod
    def assert_field_in_dict(data: dict, field: str):
        """Assert that a field exists in a dictionary."""
        assert field in data, f"Field '{field}' not found in response data"

    @staticmethod
    def assert_field_not_in_dict(data: dict, field: str):
        """Assert that a field does not exist in a dictionary."""
        assert field not in data, f"Field '{field}' should not be in response data"
