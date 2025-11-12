"""Unit tests for database models."""

from datetime import datetime

import pytest
from app.models.task import Task
from app.models.user import User
from sqlalchemy.exc import IntegrityError


class TestUserModel:
    """Test User model validation and constraints."""

    def test_create_user_with_all_fields(self, db_session):
        """Test creating a user with all fields."""
        user = User(
            email="test@example.com", username="testuser", hashed_password="hashed_pw", is_active=True, is_admin=False
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.is_admin is False
        assert isinstance(user.created_at, datetime)

    def test_create_user_with_defaults(self, db_session):
        """Test user creation uses default values correctly."""
        user = User(email="default@example.com", username="defaultuser", hashed_password="hashed_pw")
        db_session.add(user)
        db_session.commit()

        assert user.is_active is True  # Default should be True
        assert user.is_admin is False  # Default should be False
        assert user.created_at is not None

    def test_user_email_unique_constraint(self, db_session):
        """Test that duplicate emails are not allowed."""
        user1 = User(email="duplicate@example.com", username="user1", hashed_password="hashed_pw")
        db_session.add(user1)
        db_session.commit()

        # Try to create another user with same email
        user2 = User(email="duplicate@example.com", username="user2", hashed_password="hashed_pw")
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_username_unique_constraint(self, db_session):
        """Test that duplicate usernames are not allowed."""
        user1 = User(email="user1@example.com", username="duplicate_username", hashed_password="hashed_pw")
        db_session.add(user1)
        db_session.commit()

        # Try to create another user with same username
        user2 = User(email="user2@example.com", username="duplicate_username", hashed_password="hashed_pw")
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_email_not_nullable(self, db_session):
        """Test that email cannot be null."""
        user = User(username="testuser", hashed_password="hashed_pw")
        db_session.add(user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_username_not_nullable(self, db_session):
        """Test that username cannot be null."""
        user = User(email="test@example.com", hashed_password="hashed_pw")
        db_session.add(user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_hashed_password_not_nullable(self, db_session):
        """Test that hashed_password cannot be null."""
        user = User(email="test@example.com", username="testuser")
        db_session.add(user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_tasks_relationship(self, db_session):
        """Test that user has relationship to tasks."""
        user = User(email="test@example.com", username="testuser", hashed_password="hashed_pw")
        db_session.add(user)
        db_session.commit()

        # Initially, user should have no tasks
        assert user.tasks == []

        # Add a task
        task = Task(title="Test Task", owner_id=user.id)
        db_session.add(task)
        db_session.commit()

        # Refresh user to get updated tasks
        db_session.refresh(user)
        assert len(user.tasks) == 1
        assert user.tasks[0].title == "Test Task"

    def test_user_can_be_admin(self, db_session):
        """Test creating an admin user."""
        admin = User(email="admin@example.com", username="admin", hashed_password="hashed_pw", is_admin=True)
        db_session.add(admin)
        db_session.commit()

        assert admin.is_admin is True

    def test_user_can_be_inactive(self, db_session):
        """Test creating an inactive user."""
        user = User(email="inactive@example.com", username="inactive", hashed_password="hashed_pw", is_active=False)
        db_session.add(user)
        db_session.commit()

        assert user.is_active is False


class TestTaskModel:
    """Test Task model validation and constraints."""

    def test_create_task_with_all_fields(self, db_session, test_user):
        """Test creating a task with all fields."""
        task = Task(
            title="Complete task",
            description="Task description",
            is_completed=False,
            priority="high",
            category="work",
            owner_id=test_user.id,
        )
        db_session.add(task)
        db_session.commit()

        assert task.id is not None
        assert task.title == "Complete task"
        assert task.description == "Task description"
        assert task.is_completed is False
        assert task.priority == "high"
        assert task.category == "work"
        assert task.owner_id == test_user.id
        assert isinstance(task.created_at, datetime)

    def test_create_task_with_minimal_fields(self, db_session, test_user):
        """Test creating a task with only required fields."""
        task = Task(title="Minimal task", owner_id=test_user.id)
        db_session.add(task)
        db_session.commit()

        assert task.id is not None
        assert task.title == "Minimal task"
        assert task.description is None
        assert task.is_completed is False  # Default
        assert task.priority == "medium"  # Default
        assert task.category is None
        assert task.created_at is not None

    def test_task_title_not_nullable(self, db_session, test_user):
        """Test that task title cannot be null."""
        task = Task(owner_id=test_user.id)
        db_session.add(task)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_task_owner_id_not_nullable(self, db_session):
        """Test that task must have an owner."""
        task = Task(title="Orphan task")
        db_session.add(task)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_task_foreign_key_constraint(self, db_session):
        """Test that owner_id must reference a valid user."""
        task = Task(
            title="Task with invalid owner",
            owner_id=99999,  # Non-existent user ID
        )
        db_session.add(task)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_task_cascade_delete_on_user_deletion(self, db_session):
        """Test that tasks are deleted when user is deleted."""
        user = User(email="delete@example.com", username="deleteuser", hashed_password="hashed_pw")
        db_session.add(user)
        db_session.commit()

        # Create tasks for user
        task1 = Task(title="Task 1", owner_id=user.id)
        task2 = Task(title="Task 2", owner_id=user.id)
        db_session.add_all([task1, task2])
        db_session.commit()

        task_ids = [task1.id, task2.id]

        # Delete user
        db_session.delete(user)
        db_session.commit()

        remaining_tasks = db_session.query(Task).filter(Task.id.in_(task_ids)).all()
        assert len(remaining_tasks) == 0

    def test_task_default_priority_is_medium(self, db_session, test_user):
        """Test that default priority is 'medium'."""
        task = Task(title="Priority test", owner_id=test_user.id)
        db_session.add(task)
        db_session.commit()

        assert task.priority == "medium"

    def test_task_default_is_completed_is_false(self, db_session, test_user):
        """Test that default is_completed is False."""
        task = Task(title="Completion test", owner_id=test_user.id)
        db_session.add(task)
        db_session.commit()

        assert task.is_completed is False

    def test_task_description_can_be_null(self, db_session, test_user):
        """Test that description is nullable."""
        task = Task(title="Task without description", owner_id=test_user.id, description=None)
        db_session.add(task)
        db_session.commit()

        assert task.description is None

    def test_task_category_can_be_null(self, db_session, test_user):
        """Test that category is nullable."""
        task = Task(title="Task without category", owner_id=test_user.id, category=None)
        db_session.add(task)
        db_session.commit()

        assert task.category is None

    def test_task_updated_at_is_set_on_update(self, db_session, test_user):
        """Test that updated_at timestamp is set when task is updated."""
        task = Task(title="Original title", owner_id=test_user.id)
        db_session.add(task)
        db_session.commit()

        original_updated_at = task.updated_at

        # Update task
        task.title = "Updated title"
        db_session.commit()

        # Note: updated_at might still be None if onupdate doesn't trigger
        # This depends on SQLAlchemy configuration
        assert task.updated_at is not None
        assert task.updated_at != original_updated_at

    def test_task_priority_accepts_different_values(self, db_session, test_user):
        """Test that priority can be set to different values."""
        priorities = ["low", "medium", "high"]

        for priority in priorities:
            task = Task(title=f"Task with {priority} priority", priority=priority, owner_id=test_user.id)
            db_session.add(task)
            db_session.commit()

            assert task.priority == priority

    def test_task_owner_relationship(self, db_session, test_user):
        """Test that task has relationship to owner."""
        task = Task(title="Relationship test", owner_id=test_user.id)
        db_session.add(task)
        db_session.commit()

        assert task.owner is not None
        assert task.owner.id == test_user.id
        assert task.owner.username == test_user.username

    def test_multiple_tasks_same_title_different_users(self, db_session):
        """Test that different users can have tasks with same title."""
        user1 = User(email="user1@example.com", username="user1", hashed_password="hashed_pw")
        user2 = User(email="user2@example.com", username="user2", hashed_password="hashed_pw")
        db_session.add_all([user1, user2])
        db_session.commit()

        task1 = Task(title="Same title", owner_id=user1.id)
        task2 = Task(title="Same title", owner_id=user2.id)
        db_session.add_all([task1, task2])
        db_session.commit()

        assert task1.id != task2.id
        assert task1.owner_id != task2.owner_id

    def test_task_with_very_long_description(self, db_session, test_user):
        """Test task can handle very long descriptions."""
        long_description = "A" * 10000  # 10,000 characters

        task = Task(title="Long description task", description=long_description, owner_id=test_user.id)
        db_session.add(task)
        db_session.commit()

        assert len(task.description) == 10000

    def test_task_with_special_characters_in_title(self, db_session, test_user):
        """Test task title can contain special characters."""
        special_title = "Task: Review & Update @mentions #hashtags 100% done!"

        task = Task(title=special_title, owner_id=test_user.id)
        db_session.add(task)
        db_session.commit()

        assert task.title == special_title

    def test_task_with_unicode_characters(self, db_session, test_user):
        """Test task can handle unicode characters."""
        unicode_title = "任务 タスク مهمة 📝"

        task = Task(title=unicode_title, owner_id=test_user.id)
        db_session.add(task)
        db_session.commit()

        assert task.title == unicode_title
