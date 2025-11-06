"""Unit tests for Pydantic schemas."""

from datetime import datetime

import pytest
from app.schemas.task import Task, TaskBase, TaskCreate, TaskUpdate
from app.schemas.user import User, UserBase, UserCreate
from pydantic import ValidationError


class TestUserSchemas:
    """Test User schema validation."""

    def test_user_base_valid_data(self):
        """Test UserBase with valid data."""
        user_data = {"email": "test@example.com", "username": "testuser"}
        user = UserBase(**user_data)

        assert user.email == "test@example.com"
        assert user.username == "testuser"

    def test_user_base_missing_email(self):
        """Test UserBase validation fails without email."""
        user_data = {"username": "testuser"}

        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("email",) for error in errors)

    def test_user_base_missing_username(self):
        """Test UserBase validation fails without username."""
        user_data = {"email": "test@example.com"}

        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("username",) for error in errors)

    def test_user_base_empty_email(self):
        """Test UserBase accepts empty string for email (no validation)."""
        user_data = {"email": "", "username": "testuser"}
        # Note: Current schema doesn't validate email format
        user = UserBase(**user_data)
        assert user.email == ""

    def test_user_base_empty_username(self):
        """Test UserBase accepts empty string for username."""
        user_data = {"email": "test@example.com", "username": ""}
        user = UserBase(**user_data)
        assert user.username == ""

    def test_user_create_valid_data(self):
        """Test UserCreate with valid data."""
        user_data = {"email": "test@example.com", "username": "testuser", "password": "securepassword123"}
        user = UserCreate(**user_data)

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.password == "securepassword123"

    def test_user_create_missing_password(self):
        """Test UserCreate validation fails without password."""
        user_data = {"email": "test@example.com", "username": "testuser"}

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("password",) for error in errors)

    def test_user_create_empty_password(self):
        """Test UserCreate accepts empty password (no validation)."""
        user_data = {"email": "test@example.com", "username": "testuser", "password": ""}
        # Note: Current schema doesn't validate password strength
        user = UserCreate(**user_data)
        assert user.password == ""

    def test_user_create_very_long_password(self):
        """Test UserCreate accepts very long password."""
        user_data = {"email": "test@example.com", "username": "testuser", "password": "A" * 1000}
        user = UserCreate(**user_data)
        assert len(user.password) == 1000

    def test_user_create_special_characters_in_password(self):
        """Test UserCreate accepts special characters in password."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "P@ssw0rd!#$%^&*(){}[]|\\:;\"'<>,.?/~`",
        }
        user = UserCreate(**user_data)
        assert user.password == "P@ssw0rd!#$%^&*(){}[]|\\:;\"'<>,.?/~`"

    def test_user_schema_valid_data(self):
        """Test User schema with valid data."""
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(),
        }
        user = User(**user_data)

        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.is_admin is False
        assert isinstance(user.created_at, datetime)

    def test_user_schema_missing_required_fields(self):
        """Test User schema validation fails without required fields."""
        user_data = {"email": "test@example.com", "username": "testuser"}

        with pytest.raises(ValidationError) as exc_info:
            User(**user_data)

        errors = exc_info.value.errors()
        error_fields = [error["loc"][0] for error in errors]
        assert "id" in error_fields
        assert "is_active" in error_fields
        assert "is_admin" in error_fields
        assert "created_at" in error_fields

    def test_user_schema_invalid_id_type(self):
        """Test User schema validation fails with invalid id type."""
        user_data = {
            "id": "not_an_int",
            "email": "test@example.com",
            "username": "testuser",
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(),
        }

        with pytest.raises(ValidationError) as exc_info:
            User(**user_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_user_schema_invalid_boolean_type(self):
        """Test User schema validation with invalid boolean type."""
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "is_active": "not_a_bool",
            "is_admin": False,
            "created_at": datetime.now(),
        }

        # Pydantic v2 doesn't coerce random strings to bool
        with pytest.raises(ValidationError) as exc_info:
            User(**user_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("is_active",) for error in errors)

    def test_user_schema_invalid_datetime_type(self):
        """Test User schema validation fails with invalid datetime."""
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "is_active": True,
            "is_admin": False,
            "created_at": "not_a_datetime",
        }

        with pytest.raises(ValidationError) as exc_info:
            User(**user_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("created_at",) for error in errors)


class TestTaskSchemas:
    """Test Task schema validation."""

    def test_task_base_valid_data(self):
        """Test TaskBase with valid data."""
        task_data = {"title": "Test Task", "description": "Task description", "priority": "high", "category": "work"}
        task = TaskBase(**task_data)

        assert task.title == "Test Task"
        assert task.description == "Task description"
        assert task.priority == "high"
        assert task.category == "work"

    def test_task_base_minimal_data(self):
        """Test TaskBase with only required field."""
        task_data = {"title": "Minimal Task"}
        task = TaskBase(**task_data)

        assert task.title == "Minimal Task"
        assert task.description is None
        assert task.priority == "medium"  # Default value
        assert task.category is None

    def test_task_base_missing_title(self):
        """Test TaskBase validation fails without title."""
        task_data = {"description": "Task description"}

        with pytest.raises(ValidationError) as exc_info:
            TaskBase(**task_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("title",) for error in errors)

    def test_task_base_empty_title(self):
        """Test TaskBase accepts empty title."""
        task_data = {"title": ""}
        task = TaskBase(**task_data)
        assert task.title == ""

    def test_task_base_null_description(self):
        """Test TaskBase accepts None for description."""
        task_data = {"title": "Task", "description": None}
        task = TaskBase(**task_data)
        assert task.description is None

    def test_task_base_null_category(self):
        """Test TaskBase accepts None for category."""
        task_data = {"title": "Task", "category": None}
        task = TaskBase(**task_data)
        assert task.category is None

    def test_task_base_default_priority(self):
        """Test TaskBase default priority is medium."""
        task_data = {"title": "Task"}
        task = TaskBase(**task_data)
        assert task.priority == "medium"

    def test_task_base_custom_priority(self):
        """Test TaskBase accepts custom priority values."""
        priorities = ["low", "medium", "high", "urgent", "invalid"]

        for priority in priorities:
            task_data = {"title": "Task", "priority": priority}
            # Note: Current schema doesn't validate priority values
            task = TaskBase(**task_data)
            assert task.priority == priority

    def test_task_create_inherits_from_task_base(self):
        """Test TaskCreate has same validation as TaskBase."""
        task_data = {"title": "New Task", "description": "Description", "priority": "low", "category": "personal"}
        task = TaskCreate(**task_data)

        assert task.title == "New Task"
        assert task.description == "Description"
        assert task.priority == "low"
        assert task.category == "personal"

    def test_task_update_all_fields_optional(self):
        """Test TaskUpdate allows all fields to be optional."""
        task_data = {}
        task = TaskUpdate(**task_data)

        assert task.title is None
        assert task.description is None
        assert task.is_completed is None
        assert task.priority is None
        assert task.category is None

    def test_task_update_partial_fields(self):
        """Test TaskUpdate with partial field updates."""
        task_data = {"title": "Updated Title", "is_completed": True}
        task = TaskUpdate(**task_data)

        assert task.title == "Updated Title"
        assert task.is_completed is True
        assert task.description is None
        assert task.priority is None
        assert task.category is None

    def test_task_update_only_is_completed(self):
        """Test TaskUpdate with only is_completed field."""
        task_data = {"is_completed": True}
        task = TaskUpdate(**task_data)

        assert task.is_completed is True
        assert task.title is None

    def test_task_update_invalid_boolean_type(self):
        """Test TaskUpdate with invalid is_completed type."""
        task_data = {"is_completed": "not_a_bool"}
        # Pydantic v2 doesn't coerce random strings to bool
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(**task_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("is_completed",) for error in errors)

    def test_task_schema_valid_data(self):
        """Test Task schema with valid data."""
        task_data = {
            "id": 1,
            "title": "Complete Task",
            "description": "Description",
            "is_completed": False,
            "priority": "medium",
            "category": "work",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "owner_id": 1,
        }
        task = Task(**task_data)

        assert task.id == 1
        assert task.title == "Complete Task"
        assert task.description == "Description"
        assert task.is_completed is False
        assert task.priority == "medium"
        assert task.category == "work"
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
        assert task.owner_id == 1

    def test_task_schema_null_updated_at(self):
        """Test Task schema accepts None for updated_at."""
        task_data = {
            "id": 1,
            "title": "Task",
            "is_completed": False,
            "created_at": datetime.now(),
            "updated_at": None,
            "owner_id": 1,
        }
        task = Task(**task_data)
        assert task.updated_at is None

    def test_task_schema_missing_required_fields(self):
        """Test Task schema validation fails without required fields."""
        task_data = {"title": "Task"}

        with pytest.raises(ValidationError) as exc_info:
            Task(**task_data)

        errors = exc_info.value.errors()
        error_fields = [error["loc"][0] for error in errors]
        assert "id" in error_fields
        assert "is_completed" in error_fields
        assert "created_at" in error_fields
        assert "owner_id" in error_fields

    def test_task_schema_invalid_id_type(self):
        """Test Task schema validation fails with invalid id type."""
        task_data = {
            "id": "not_an_int",
            "title": "Task",
            "is_completed": False,
            "created_at": datetime.now(),
            "owner_id": 1,
        }

        with pytest.raises(ValidationError) as exc_info:
            Task(**task_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_task_schema_invalid_owner_id_type(self):
        """Test Task schema validation fails with invalid owner_id type."""
        task_data = {
            "id": 1,
            "title": "Task",
            "is_completed": False,
            "created_at": datetime.now(),
            "owner_id": "not_an_int",
        }

        with pytest.raises(ValidationError) as exc_info:
            Task(**task_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("owner_id",) for error in errors)

    def test_task_schema_very_long_title(self):
        """Test Task schema with very long title."""
        long_title = "A" * 10000

        task_data = {"id": 1, "title": long_title, "is_completed": False, "created_at": datetime.now(), "owner_id": 1}
        task = Task(**task_data)
        assert len(task.title) == 10000

    def test_task_schema_unicode_characters(self):
        """Test Task schema with unicode characters."""
        task_data = {
            "id": 1,
            "title": "任务 タスク مهمة 📝",
            "description": "Unicode description: 你好世界",
            "is_completed": False,
            "created_at": datetime.now(),
            "owner_id": 1,
        }
        task = Task(**task_data)
        assert task.title == "任务 タスク مهمة 📝"
        assert task.description == "Unicode description: 你好世界"

    def test_task_schema_special_characters(self):
        """Test Task schema with special characters."""
        task_data = {
            "id": 1,
            "title": "Task: Review & Update @mentions #hashtags <html>",
            "description": "Special chars: !@#$%^&*(){}[]|\\:;\"'<>,.?/~`",
            "is_completed": False,
            "created_at": datetime.now(),
            "owner_id": 1,
        }
        task = Task(**task_data)
        assert "<html>" in task.title
        assert "!@#$%^&*()" in task.description

    def test_task_base_extra_fields_ignored(self):
        """Test that extra fields are ignored (no extra='forbid')."""
        task_data = {"title": "Task", "extra_field": "should be ignored"}
        task = TaskBase(**task_data)
        assert not hasattr(task, "extra_field")
