"""Tasks API client for task CRUD operations."""

from __future__ import annotations

from typing import Any

import allure

from tests.api.clients.base_client import APIResponse, BaseAPIClient
from tests.common.constants import Endpoints


class TasksAPIClient(BaseAPIClient):
    """Client for Tasks API endpoints.

    Handles all task CRUD operations for the /api/tasks endpoints.

    Example:
        tasks = TasksAPIClient(authenticated_client, base_url)
        response = tasks.create_task(title="My Task", priority="high")
        response.assert_ok().assert_field_equals("title", "My Task")
    """

    BASE_PATH = Endpoints.TASKS

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        category: str = "",
    ) -> APIResponse:
        """Create a new task.

        Args:
            title: Task title (required)
            description: Task description (optional)
            priority: Task priority - low/medium/high (default: medium)
            category: Task category (optional)

        Returns:
            APIResponse with created task data
        """
        task_data: dict[str, Any] = {"title": title}

        if description:
            task_data["description"] = description
        if priority:
            task_data["priority"] = priority
        if category:
            task_data["category"] = category

        with allure.step(f"Create task: {title}"):
            allure.attach(
                str(task_data),
                name="Task Data",
                attachment_type=allure.attachment_type.JSON,
            )
            return self.post(
                step_name=f"POST {self.endpoint}",
                json=task_data,
            )

    def get_all_tasks(self, skip: int = 0, limit: int = 100) -> APIResponse:
        """Get all tasks for current user.

        Args:
            skip: Number of tasks to skip (pagination)
            limit: Maximum tasks to return (pagination)

        Returns:
            APIResponse with list of tasks
        """
        params: dict[str, int] = {}
        # Use explicit None check so skip=0 is properly handled
        if skip is not None and skip != 0:
            params["skip"] = skip
        if limit is not None and limit != 100:
            params["limit"] = limit

        return self.get(
            step_name="Retrieve all tasks",
            params=params if params else None,
        )

    def get_task(self, task_id: int) -> APIResponse:
        """Get a specific task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            APIResponse with task data
        """
        return self.get(
            path=str(task_id),
            step_name=f"Retrieve task {task_id}",
        )

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        category: str | None = None,
        is_completed: bool | None = None,
    ) -> APIResponse:
        """Update a task.

        Only provided fields will be updated.

        Args:
            task_id: Task ID to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            category: New category (optional)
            is_completed: Completion status (optional)

        Returns:
            APIResponse with updated task data
        """
        update_data: dict[str, Any] = {}

        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if priority is not None:
            update_data["priority"] = priority
        if category is not None:
            update_data["category"] = category
        if is_completed is not None:
            update_data["is_completed"] = is_completed

        with allure.step(f"Update task {task_id}"):
            allure.attach(
                str(update_data),
                name="Update Data",
                attachment_type=allure.attachment_type.JSON,
            )
            return self.put(
                path=str(task_id),
                step_name=f"PUT {self.endpoint}/{task_id}",
                json=update_data,
            )

    def delete_task(self, task_id: int) -> APIResponse:
        """Delete a task.

        Args:
            task_id: Task ID to delete

        Returns:
            APIResponse with deletion confirmation
        """
        return self.delete(
            path=str(task_id),
            step_name=f"Delete task {task_id}",
        )

    def mark_complete(self, task_id: int) -> APIResponse:
        """Mark a task as complete.

        Convenience method wrapping update_task.

        Args:
            task_id: Task ID to mark complete

        Returns:
            APIResponse with updated task
        """
        with allure.step(f"Mark task {task_id} as complete"):
            return self.update_task(task_id, is_completed=True)

    def mark_incomplete(self, task_id: int) -> APIResponse:
        """Mark a task as incomplete.

        Convenience method wrapping update_task.

        Args:
            task_id: Task ID to mark incomplete

        Returns:
            APIResponse with updated task
        """
        with allure.step(f"Mark task {task_id} as incomplete"):
            return self.update_task(task_id, is_completed=False)

    def create_and_get_id(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        category: str = "",
    ) -> int:
        """Create a task and return its ID.

        Convenience method for test setup.

        Args:
            title: Task title
            description: Task description
            priority: Task priority
            category: Task category

        Returns:
            Created task ID

        Raises:
            AssertionError: If creation fails
            KeyError: If id not in response
        """
        response = self.create_task(title, description, priority, category)
        response.assert_ok()
        response.assert_field_exists("id")
        return response.data["id"]
