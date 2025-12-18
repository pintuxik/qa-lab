"""
Integration tests for Tasks API endpoints.

Uses API client abstraction for clean, maintainable tests.
"""

import allure
import pytest

from tests.api.clients import AuthAPIClient, TasksAPIClient, UsersAPIClient
from tests.common.factories import TaskFactory, UserFactory


@allure.feature("Tasks API")
@allure.story("Task Creation")
class TestTaskCreation:
    """Test cases for creating tasks."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Create task with all fields")
    @allure.description("Verify that a task can be created with all fields populated")
    @pytest.mark.integration
    def test_create_task_success(self, authenticated_tasks_api: TasksAPIClient):
        """Test successful task creation with all fields."""
        task = TaskFactory.complete("Complete API Integration Tests")

        response = authenticated_tasks_api.create_task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            category=task.category,
        )

        response.assert_ok()
        response.assert_field_exists("id")
        response.assert_field_equals("title", task.title)
        response.assert_field_equals("description", task.description)
        response.assert_field_equals("priority", task.priority)
        response.assert_field_equals("category", task.category)
        response.assert_field_is_false("is_completed")
        response.assert_field_exists("created_at")
        response.assert_field_exists("owner_id")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create task with minimal data")
    @allure.description("Verify that a task can be created with only required fields")
    @pytest.mark.integration
    def test_create_task_minimal(self, authenticated_tasks_api: TasksAPIClient):
        """Test task creation with only required fields."""
        task = TaskFactory.minimal("Minimal Task")

        response = authenticated_tasks_api.create_task(title=task.title)

        response.assert_ok()
        response.assert_field_equals("title", task.title)
        response.assert_field_equals("priority", "medium")  # Default priority
        response.assert_field_is_false("is_completed")

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Create task requires authentication")
    @allure.description("Verify that task creation fails without authentication")
    @pytest.mark.integration
    def test_create_task_requires_auth(self, tasks_api: TasksAPIClient):
        """Test that creating a task requires authentication."""
        response = tasks_api.create_task(title="Unauthorized Task")

        response.assert_unauthorized()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create task with invalid data")
    @allure.description("Verify that task creation fails with invalid data")
    @pytest.mark.integration
    def test_create_task_invalid_data(self, authenticated_tasks_api: TasksAPIClient):
        """Test task creation with missing required fields."""
        # Use raw post to send malformed data
        response = authenticated_tasks_api.post(json={"description": "Task without title"})

        response.assert_validation_error()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create multiple tasks")
    @allure.description("Verify that multiple tasks can be created for the same user")
    @pytest.mark.integration
    def test_create_multiple_tasks(self, authenticated_tasks_api: TasksAPIClient):
        """Test creating multiple tasks."""
        priorities = ["low", "medium", "high"]
        created_tasks = []

        with allure.step("Create 3 tasks"):
            for i, priority in enumerate(priorities):
                response = authenticated_tasks_api.create_task(
                    title=f"Task {i + 1}",
                    description=f"Description for task {i + 1}",
                    priority=priority,
                )
                response.assert_ok()
                created_tasks.append(response.data)

        with allure.step("Verify all tasks were created"):
            assert len(created_tasks) == 3
            for i, task in enumerate(created_tasks):
                assert task["title"] == f"Task {i + 1}"


@allure.feature("Tasks API")
@allure.story("Task Retrieval")
class TestTaskRetrieval:
    """Test cases for retrieving tasks."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Get all tasks for authenticated user")
    @allure.description("Verify that user can retrieve all their tasks")
    @pytest.mark.integration
    def test_get_all_tasks(self, authenticated_tasks_api: TasksAPIClient):
        """Test retrieving all tasks for a user."""
        # Create test tasks
        for i in range(3):
            authenticated_tasks_api.create_task(title=f"Test Task {i + 1}")

        response = authenticated_tasks_api.get_all_tasks()

        response.assert_ok()
        response.assert_is_list()
        response.assert_list_length(3)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Get tasks with pagination")
    @allure.description("Verify that tasks can be retrieved with skip and limit parameters")
    @pytest.mark.integration
    def test_get_tasks_with_pagination(self, authenticated_tasks_api: TasksAPIClient):
        """Test task retrieval with pagination."""
        # Create 5 tasks
        for i in range(5):
            authenticated_tasks_api.create_task(title=f"Paginated Task {i + 1}")

        response = authenticated_tasks_api.get_all_tasks(skip=1, limit=3)

        response.assert_ok()
        response.assert_is_list()
        response.assert_list_length(3)

        response = authenticated_tasks_api.get_all_tasks(skip=3)
        response.assert_ok()
        response.assert_is_list()
        response.assert_list_length(2)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Get single task by ID")
    @allure.description("Verify that a specific task can be retrieved by its ID")
    @pytest.mark.integration
    def test_get_single_task(self, authenticated_tasks_api: TasksAPIClient):
        """Test retrieving a single task by ID."""
        # Create a task
        task_id = authenticated_tasks_api.create_and_get_id(
            title="Specific Task",
            description="Task to retrieve",
        )

        response = authenticated_tasks_api.get_task(task_id)

        response.assert_ok()
        response.assert_field_equals("id", task_id)
        response.assert_field_equals("title", "Specific Task")
        response.assert_field_equals("description", "Task to retrieve")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Get non-existent task returns 404")
    @allure.description("Verify that retrieving a non-existent task returns 404")
    @pytest.mark.integration
    def test_get_nonexistent_task(self, authenticated_tasks_api: TasksAPIClient):
        """Test retrieving a non-existent task."""
        response = authenticated_tasks_api.get_task(999999)

        response.assert_not_found()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Get tasks requires authentication")
    @allure.description("Verify that retrieving tasks requires authentication")
    @pytest.mark.integration
    def test_get_tasks_requires_auth(self, tasks_api: TasksAPIClient):
        """Test that retrieving tasks requires authentication."""
        response = tasks_api.get_all_tasks()

        response.assert_unauthorized()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Get empty task list")
    @allure.description("Verify that empty list is returned when user has no tasks")
    @pytest.mark.integration
    def test_get_empty_task_list(self, authenticated_tasks_api: TasksAPIClient):
        """Test retrieving tasks when user has none."""
        response = authenticated_tasks_api.get_all_tasks()

        response.assert_ok()
        response.assert_is_list()
        response.assert_list_length(0)


@allure.feature("Tasks API")
@allure.story("Task Update")
class TestTaskUpdate:
    """Test cases for updating tasks."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Update task title")
    @allure.description("Verify that task title can be updated")
    @pytest.mark.integration
    def test_update_task_title(self, authenticated_tasks_api: TasksAPIClient):
        """Test updating a task's title."""
        task_id = authenticated_tasks_api.create_and_get_id(title="Original Title")

        response = authenticated_tasks_api.update_task(task_id, title="Updated Title")

        response.assert_ok()
        response.assert_field_equals("title", "Updated Title")

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Update task completion status")
    @allure.description("Verify that task completion status can be toggled")
    @pytest.mark.integration
    def test_update_task_completion(self, authenticated_tasks_api: TasksAPIClient):
        """Test updating a task's completion status."""
        task_id = authenticated_tasks_api.create_and_get_id(title="Task to Complete")

        response = authenticated_tasks_api.mark_complete(task_id)

        response.assert_ok()
        response.assert_field_is_true("is_completed")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Update task priority")
    @allure.description("Verify that task priority can be changed")
    @pytest.mark.integration
    def test_update_task_priority(self, authenticated_tasks_api: TasksAPIClient):
        """Test updating a task's priority."""
        task_id = authenticated_tasks_api.create_and_get_id(
            title="Priority Task",
            priority="medium",
        )

        response = authenticated_tasks_api.update_task(task_id, priority="high")

        response.assert_ok()
        response.assert_field_equals("priority", "high")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Update multiple task fields")
    @allure.description("Verify that multiple fields can be updated in one request")
    @pytest.mark.integration
    def test_update_multiple_fields(self, authenticated_tasks_api: TasksAPIClient):
        """Test updating multiple task fields at once."""
        task_id = authenticated_tasks_api.create_and_get_id(
            title="Multi-Update Task",
            priority="low",
        )

        response = authenticated_tasks_api.update_task(
            task_id,
            title="Updated Multi-Task",
            description="New description",
            priority="high",
            is_completed=True,
        )

        response.assert_ok()
        response.assert_field_equals("title", "Updated Multi-Task")
        response.assert_field_equals("description", "New description")
        response.assert_field_equals("priority", "high")
        response.assert_field_is_true("is_completed")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Update non-existent task returns 404")
    @allure.description("Verify that updating a non-existent task returns 404")
    @pytest.mark.integration
    def test_update_nonexistent_task(self, authenticated_tasks_api: TasksAPIClient):
        """Test updating a non-existent task."""
        response = authenticated_tasks_api.update_task(999999, title="Updated Title")

        response.assert_not_found()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Update task requires authentication")
    @allure.description("Verify that updating a task requires authentication")
    @pytest.mark.integration
    def test_update_task_requires_auth(self, tasks_api: TasksAPIClient):
        """Test that updating a task requires authentication."""
        response = tasks_api.update_task(1, title="Unauthorized Update")

        response.assert_unauthorized()


@allure.feature("Tasks API")
@allure.story("Task Deletion")
class TestTaskDeletion:
    """Test cases for deleting tasks."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Delete task successfully")
    @allure.description("Verify that a task can be deleted")
    @pytest.mark.integration
    def test_delete_task_success(self, authenticated_tasks_api: TasksAPIClient):
        """Test successful task deletion."""
        task_id = authenticated_tasks_api.create_and_get_id(title="Task to Delete")

        response = authenticated_tasks_api.delete_task(task_id)

        response.assert_ok()
        response.assert_field_exists("message")

        # Verify task is actually deleted
        get_response = authenticated_tasks_api.get_task(task_id)
        get_response.assert_not_found()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Delete non-existent task returns 404")
    @allure.description("Verify that deleting a non-existent task returns 404")
    @pytest.mark.integration
    def test_delete_nonexistent_task(self, authenticated_tasks_api: TasksAPIClient):
        """Test deleting a non-existent task."""
        response = authenticated_tasks_api.delete_task(999999)

        response.assert_not_found()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Delete task requires authentication")
    @allure.description("Verify that deleting a task requires authentication")
    @pytest.mark.integration
    def test_delete_task_requires_auth(self, tasks_api: TasksAPIClient):
        """Test that deleting a task requires authentication."""
        response = tasks_api.delete_task(1)

        response.assert_unauthorized()


@allure.feature("Tasks API")
@allure.story("Task Isolation")
class TestTaskIsolation:
    """Test cases for task isolation between users."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("User cannot access other user's tasks")
    @allure.description("Verify that tasks are properly isolated between users")
    @pytest.mark.integration
    def test_task_isolation_between_users(
        self,
        api_client,
        api_base_url,
    ):
        """Test that users cannot access each other's tasks."""
        # Create API clients
        users_api = UsersAPIClient(api_client, api_base_url)
        auth_api = AuthAPIClient(api_client, api_base_url)
        tasks_api = TasksAPIClient(api_client, api_base_url)

        # Create first user
        user1 = UserFactory.api_user()
        with allure.step("Create first user and task"):
            users_api.register(user1.username, user1.email, user1.password)
            token1 = auth_api.get_token(user1.username, user1.password)

            tasks_api.set_auth_token(token1)
            create_response = tasks_api.create_task(title="User 1 Task")
            task_id = create_response.data["id"]

        # Create second user
        user2 = UserFactory.api_user()
        with allure.step("Create second user"):
            users_api.register(user2.username, user2.email, user2.password)
            token2 = auth_api.get_token(user2.username, user2.password)

        with allure.step("Attempt to access user 1's task as user 2"):
            tasks_api.set_auth_token(token2)
            response = tasks_api.get_task(task_id)

        with allure.step("Verify user 2 cannot access user 1's task"):
            response.assert_not_found()
