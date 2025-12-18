"""Test data factories for generating unique test data.

Provides dataclasses and factory methods for creating test tasks
with unique identifiers to support parallel test execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tests.common.utils import generate_unique_id


@dataclass
class TaskData:
    """Test task data container.

    Example:
        task = TaskData.generate()
        response = api.create_task(task.title, task.description, task.priority)

        # Or with specific values
        task = TaskData(title="My Task", priority="high")
    """

    title: str
    description: str | None = None
    priority: str = "medium"
    category: str | None = None
    is_completed: bool = False
    id: int | None = None

    @classmethod
    def generate(cls, prefix: str = "Test Task") -> TaskData:
        """Generate a unique test task.

        Args:
            prefix: Prefix for task title

        Returns:
            TaskData with unique title
        """
        unique_id = generate_unique_id()
        return cls(
            title=f"{prefix} {unique_id}",
            description=f"Auto-generated test task {unique_id}",
        )

    def to_create_dict(self) -> dict[str, Any]:
        """Convert to task creation API payload.

        Only includes non-None fields.
        """
        result: dict[str, Any] = {"title": self.title}

        if self.description:
            result["description"] = self.description
        if self.priority:
            result["priority"] = self.priority
        if self.category:
            result["category"] = self.category
        if self.is_completed:
            result["is_completed"] = self.is_completed

        return result

    def to_update_dict(self, include_title: bool = False) -> dict[str, Any]:
        """Convert to task update API payload.

        Unlike create, updates typically don't include title unless explicitly needed.

        Args:
            include_title: Whether to include title in update payload (default: False)
        """
        result: dict[str, Any] = {}

        if include_title and self.title:
            result["title"] = self.title
        if self.description:
            result["description"] = self.description
        if self.priority:
            result["priority"] = self.priority
        if self.category:
            result["category"] = self.category
        if self.is_completed:
            result["is_completed"] = self.is_completed

        return result


@dataclass
class TaskFactory:
    """Factory for creating various test task configurations.

    Example:
        task = TaskFactory.simple("My Task")
        task = TaskFactory.high_priority()
        task = TaskFactory.complete()
    """

    @staticmethod
    def simple(title: str | None = None) -> TaskData:
        """Create a simple task with just title.

        Args:
            title: Task title (auto-generated if None)
        """
        task = TaskData.generate()
        if title:
            task.title = title
        return task

    @staticmethod
    def with_priority(priority: str, title: str | None = None) -> TaskData:
        """Create a task with specific priority.

        Args:
            priority: Task priority (low/medium/high)
            title: Task title (auto-generated if None)
        """
        task = TaskData.generate()
        task.priority = priority
        if title:
            task.title = title
        return task

    @staticmethod
    def high_priority(title: str | None = None) -> TaskData:
        """Create a high priority task."""
        return TaskFactory.with_priority("high", title)

    @staticmethod
    def low_priority(title: str | None = None) -> TaskData:
        """Create a low priority task."""
        return TaskFactory.with_priority("low", title)

    @staticmethod
    def complete(title: str | None = None) -> TaskData:
        """Create a task with all fields populated.

        Args:
            title: Task title (auto-generated if None)
        """
        unique_id = generate_unique_id()
        return TaskData(
            title=title or f"Complete Task {unique_id}",
            description="Full description for comprehensive testing",
            priority="high",
            category="testing",
        )

    @staticmethod
    def minimal(title: str | None = None) -> TaskData:
        """Create a minimal task (title only).

        Args:
            title: Task title (auto-generated if None)
        """
        unique_id = generate_unique_id()
        return TaskData(
            title=title or f"Minimal Task {unique_id}",
        )

    @staticmethod
    def batch(count: int, prefix: str = "Batch Task") -> list[TaskData]:
        """Create multiple unique tasks.

        Args:
            count: Number of tasks to create
            prefix: Prefix for task titles

        Returns:
            List of TaskData instances
        """
        return [TaskData.generate(prefix=f"{prefix} {i + 1}") for i in range(count)]
