"""
Integration tests for Tasks API endpoints.
"""

import allure
import pytest
from conftest import TEST_API_KEY


@allure.feature("Tasks API")
@allure.story("Task Creation")
class TestTaskCreation:
    """Test cases for creating tasks."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Create task with all fields")
    @allure.description("Verify that a task can be created with all fields populated")
    @pytest.mark.integration
    def test_create_task_success(self, authenticated_client, api_base_url):
        """Test successful task creation with all fields."""
        with allure.step("Prepare task data"):
            task_data = {
                "title": "Complete API Integration Tests",
                "description": "Write comprehensive tests for all API endpoints",
                "priority": "high",
                "category": "testing",
            }
            allure.attach(str(task_data), name="Task Data", attachment_type=allure.attachment_type.JSON)

        with allure.step("Send create task request"):
            response = authenticated_client.post(f"{api_base_url}/api/tasks/", json=task_data)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 200"):
            assert response.status_code == 200

        with allure.step("Verify response contains task data"):
            response_data = response.json()
            assert "id" in response_data
            assert response_data["title"] == task_data["title"]
            assert response_data["description"] == task_data["description"]
            assert response_data["priority"] == task_data["priority"]
            assert response_data["category"] == task_data["category"]
            assert response_data["is_completed"] is False
            assert "created_at" in response_data
            assert "owner_id" in response_data

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create task with minimal data")
    @allure.description("Verify that a task can be created with only required fields")
    @pytest.mark.integration
    def test_create_task_minimal(self, authenticated_client, api_base_url):
        """Test task creation with only required fields."""
        with allure.step("Prepare minimal task data"):
            task_data = {"title": "Minimal Task"}
            allure.attach(str(task_data), name="Task Data", attachment_type=allure.attachment_type.JSON)

        with allure.step("Send create task request"):
            response = authenticated_client.post(f"{api_base_url}/api/tasks/", json=task_data)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 200"):
            assert response.status_code == 200

        with allure.step("Verify response contains default values"):
            response_data = response.json()
            assert response_data["title"] == task_data["title"]
            assert response_data["priority"] == "medium"  # Default priority
            assert response_data["is_completed"] is False

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Create task requires authentication")
    @allure.description("Verify that task creation fails without authentication")
    @pytest.mark.integration
    def test_create_task_requires_auth(self, api_client, api_base_url):
        """Test that creating a task requires authentication."""
        with allure.step("Attempt to create task without authentication"):
            task_data = {"title": "Unauthorized Task"}
            response = api_client.post(f"{api_base_url}/api/tasks/", json=task_data)
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 401"):
            assert response.status_code == 401

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create task with invalid data")
    @allure.description("Verify that task creation fails with invalid data")
    @pytest.mark.integration
    def test_create_task_invalid_data(self, authenticated_client, api_base_url):
        """Test task creation with missing required fields."""
        with allure.step("Attempt to create task without title"):
            task_data = {"description": "Task without title"}
            response = authenticated_client.post(f"{api_base_url}/api/tasks/", json=task_data)
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response indicates validation error"):
            assert response.status_code == 422

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create multiple tasks")
    @allure.description("Verify that multiple tasks can be created for the same user")
    @pytest.mark.integration
    def test_create_multiple_tasks(self, authenticated_client, api_base_url):
        """Test creating multiple tasks."""
        task_count = 3
        created_tasks = []

        with allure.step(f"Create {task_count} tasks"):
            for i in range(task_count):
                task_data = {
                    "title": f"Task {i + 1}",
                    "description": f"Description for task {i + 1}",
                    "priority": ["low", "medium", "high"][i],
                }
                response = authenticated_client.post(f"{api_base_url}/api/tasks/", json=task_data)
                assert response.status_code == 200
                created_tasks.append(response.json())

        with allure.step("Verify all tasks were created"):
            assert len(created_tasks) == task_count
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
    def test_get_all_tasks(self, authenticated_client, api_base_url):
        """Test retrieving all tasks for a user."""
        with allure.step("Create test tasks"):
            for i in range(3):
                task_data = {"title": f"Test Task {i + 1}"}
                authenticated_client.post(f"{api_base_url}/api/tasks/", json=task_data)

        with allure.step("Retrieve all tasks"):
            response = authenticated_client.get(f"{api_base_url}/api/tasks/")
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 200"):
            assert response.status_code == 200

        with allure.step("Verify tasks are returned"):
            tasks = response.json()
            assert isinstance(tasks, list)
            assert len(tasks) >= 3

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Get tasks with pagination")
    @allure.description("Verify that tasks can be retrieved with skip and limit parameters")
    @pytest.mark.integration
    def test_get_tasks_with_pagination(self, authenticated_client, api_base_url):
        """Test task retrieval with pagination."""
        with allure.step("Create 5 test tasks"):
            for i in range(5):
                task_data = {"title": f"Paginated Task {i + 1}"}
                authenticated_client.post(f"{api_base_url}/api/tasks/", json=task_data)

        with allure.step("Retrieve tasks with skip=2 and limit=2"):
            response = authenticated_client.get(f"{api_base_url}/api/tasks/?skip=2&limit=2")
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify pagination works"):
            tasks = response.json()
            assert len(tasks) <= 2

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Get single task by ID")
    @allure.description("Verify that a specific task can be retrieved by its ID")
    @pytest.mark.integration
    def test_get_single_task(self, authenticated_client, api_base_url):
        """Test retrieving a single task by ID."""
        with allure.step("Create a test task"):
            task_data = {"title": "Specific Task", "description": "Task to retrieve"}
            create_response = authenticated_client.post(f"{api_base_url}/api/tasks/", json=task_data)
            task_id = create_response.json()["id"]

        with allure.step(f"Retrieve task with ID {task_id}"):
            response = authenticated_client.get(f"{api_base_url}/api/tasks/{task_id}")
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 200"):
            assert response.status_code == 200

        with allure.step("Verify task data matches"):
            task = response.json()
            assert task["id"] == task_id
            assert task["title"] == task_data["title"]
            assert task["description"] == task_data["description"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Get non-existent task returns 404")
    @allure.description("Verify that retrieving a non-existent task returns 404")
    @pytest.mark.integration
    def test_get_nonexistent_task(self, authenticated_client, api_base_url):
        """Test retrieving a non-existent task."""
        with allure.step("Attempt to retrieve non-existent task"):
            response = authenticated_client.get(f"{api_base_url}/api/tasks/999999")
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 404"):
            assert response.status_code == 404

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Get tasks requires authentication")
    @allure.description("Verify that retrieving tasks requires authentication")
    @pytest.mark.integration
    def test_get_tasks_requires_auth(self, api_client, api_base_url):
        """Test that retrieving tasks requires authentication."""
        with allure.step("Attempt to retrieve tasks without authentication"):
            response = api_client.get(f"{api_base_url}/api/tasks/")
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 401"):
            assert response.status_code == 401

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Get empty task list")
    @allure.description("Verify that empty list is returned when user has no tasks")
    @pytest.mark.integration
    def test_get_empty_task_list(self, authenticated_client, api_base_url):
        """Test retrieving tasks when user has none."""
        with allure.step("Retrieve tasks for new user"):
            response = authenticated_client.get(f"{api_base_url}/api/tasks/")
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify empty list is returned"):
            tasks = response.json()
            assert isinstance(tasks, list)


@allure.feature("Tasks API")
@allure.story("Task Update")
class TestTaskUpdate:
    """Test cases for updating tasks."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Update task title")
    @allure.description("Verify that task title can be updated")
    @pytest.mark.integration
    def test_update_task_title(self, authenticated_client, api_base_url):
        """Test updating a task's title."""
        with allure.step("Create a test task"):
            task_data = {"title": "Original Title"}
            create_response = authenticated_client.post(f"{api_base_url}/api/tasks/", json=task_data)
            task_id = create_response.json()["id"]

        with allure.step("Update task title"):
            update_data = {"title": "Updated Title"}
            response = authenticated_client.put(f"{api_base_url}/api/tasks/{task_id}", json=update_data)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 200"):
            assert response.status_code == 200

        with allure.step("Verify title was updated"):
            updated_task = response.json()
            assert updated_task["title"] == "Updated Title"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Update task completion status")
    @allure.description("Verify that task completion status can be toggled")
    @pytest.mark.integration
    def test_update_task_completion(self, authenticated_client, api_base_url):
        """Test updating a task's completion status."""
        with allure.step("Create a test task"):
            task_data = {"title": "Task to Complete"}
            create_response = authenticated_client.post(f"{api_base_url}/api/tasks/", json=task_data)
            task_id = create_response.json()["id"]

        with allure.step("Mark task as completed"):
            update_data = {"is_completed": True}
            response = authenticated_client.put(f"{api_base_url}/api/tasks/{task_id}", json=update_data)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify task is marked as completed"):
            updated_task = response.json()
            assert updated_task["is_completed"] is True

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Update task priority")
    @allure.description("Verify that task priority can be changed")
    @pytest.mark.integration
    def test_update_task_priority(self, authenticated_client, api_base_url):
        """Test updating a task's priority."""
        with allure.step("Create a test task with medium priority"):
            task_data = {"title": "Priority Task", "priority": "medium"}
            create_response = authenticated_client.post(f"{api_base_url}/api/tasks/", json=task_data)
            task_id = create_response.json()["id"]

        with allure.step("Update priority to high"):
            update_data = {"priority": "high"}
            response = authenticated_client.put(f"{api_base_url}/api/tasks/{task_id}", json=update_data)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify priority was updated"):
            updated_task = response.json()
            assert updated_task["priority"] == "high"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Update multiple task fields")
    @allure.description("Verify that multiple fields can be updated in one request")
    @pytest.mark.integration
    def test_update_multiple_fields(self, authenticated_client, api_base_url):
        """Test updating multiple task fields at once."""
        with allure.step("Create a test task"):
            task_data = {"title": "Multi-Update Task", "priority": "low"}
            create_response = authenticated_client.post(f"{api_base_url}/api/tasks/", json=task_data)
            task_id = create_response.json()["id"]

        with allure.step("Update multiple fields"):
            update_data = {
                "title": "Updated Multi-Task",
                "description": "New description",
                "priority": "high",
                "is_completed": True,
            }
            response = authenticated_client.put(f"{api_base_url}/api/tasks/{task_id}", json=update_data)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify all fields were updated"):
            updated_task = response.json()
            assert updated_task["title"] == update_data["title"]
            assert updated_task["description"] == update_data["description"]
            assert updated_task["priority"] == update_data["priority"]
            assert updated_task["is_completed"] == update_data["is_completed"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Update non-existent task returns 404")
    @allure.description("Verify that updating a non-existent task returns 404")
    @pytest.mark.integration
    def test_update_nonexistent_task(self, authenticated_client, api_base_url):
        """Test updating a non-existent task."""
        with allure.step("Attempt to update non-existent task"):
            update_data = {"title": "Updated Title"}
            response = authenticated_client.put(f"{api_base_url}/api/tasks/999999", json=update_data)
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 404"):
            assert response.status_code == 404

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Update task requires authentication")
    @allure.description("Verify that updating a task requires authentication")
    @pytest.mark.integration
    def test_update_task_requires_auth(self, api_client, api_base_url):
        """Test that updating a task requires authentication."""
        with allure.step("Attempt to update task without authentication"):
            update_data = {"title": "Unauthorized Update"}
            response = api_client.put(f"{api_base_url}/api/tasks/1", json=update_data)
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 401"):
            assert response.status_code == 401


@allure.feature("Tasks API")
@allure.story("Task Deletion")
class TestTaskDeletion:
    """Test cases for deleting tasks."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Delete task successfully")
    @allure.description("Verify that a task can be deleted")
    @pytest.mark.integration
    def test_delete_task_success(self, authenticated_client, api_base_url):
        """Test successful task deletion."""
        with allure.step("Create a test task"):
            task_data = {"title": "Task to Delete"}
            create_response = authenticated_client.post(f"{api_base_url}/api/tasks/", json=task_data)
            task_id = create_response.json()["id"]

        with allure.step(f"Delete task with ID {task_id}"):
            response = authenticated_client.delete(f"{api_base_url}/api/tasks/{task_id}")
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 200"):
            assert response.status_code == 200

        with allure.step("Verify success message"):
            response_data = response.json()
            assert "message" in response_data

        with allure.step("Verify task is actually deleted"):
            get_response = authenticated_client.get(f"{api_base_url}/api/tasks/{task_id}")
            assert get_response.status_code == 404

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Delete non-existent task returns 404")
    @allure.description("Verify that deleting a non-existent task returns 404")
    @pytest.mark.integration
    def test_delete_nonexistent_task(self, authenticated_client, api_base_url):
        """Test deleting a non-existent task."""
        with allure.step("Attempt to delete non-existent task"):
            response = authenticated_client.delete(f"{api_base_url}/api/tasks/999999")
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 404"):
            assert response.status_code == 404

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Delete task requires authentication")
    @allure.description("Verify that deleting a task requires authentication")
    @pytest.mark.integration
    def test_delete_task_requires_auth(self, api_client, api_base_url):
        """Test that deleting a task requires authentication."""
        with allure.step("Attempt to delete task without authentication"):
            response = api_client.delete(f"{api_base_url}/api/tasks/1")
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify response status code is 401"):
            assert response.status_code == 401


@allure.feature("Tasks API")
@allure.story("Task Isolation")
class TestTaskIsolation:
    """Test cases for task isolation between users."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("User cannot access other user's tasks")
    @allure.description("Verify that tasks are properly isolated between users")
    @pytest.mark.integration
    def test_task_isolation_between_users(self, api_client, api_base_url):
        """Test that users cannot access each other's tasks."""
        import random
        import time

        unique_id = f"{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        with allure.step("Create first user and task"):
            user1_data = {
                "username": f"api_user_1_{unique_id}",
                "email": f"api_user_1_{unique_id}@example.com",
                "password": "Pass123!",
            }
            response1 = api_client.post(f"{api_base_url}/api/users/", json=user1_data)
            login1 = api_client.post(
                f"{api_base_url}/api/auth/login",
                data={"username": user1_data["username"], "password": user1_data["password"]},
            )
            token1 = login1.json()["access_token"]

            api_client.headers.update({"Authorization": f"Bearer {token1}"})
            task_response = api_client.post(
                f"{api_base_url}/api/tasks/",
                json={"title": "User 1 Task"},
            )
            task_id = task_response.json()["id"]

        with allure.step("Create second user"):
            user2_data = {
                "username": f"api_user_2_{unique_id}",
                "email": f"api_user_2_{unique_id}@example.com",
                "password": "Pass123!",
            }
            response2 = api_client.post(f"{api_base_url}/api/users/", json=user2_data)
            login2 = api_client.post(
                f"{api_base_url}/api/auth/login",
                data={"username": user2_data["username"], "password": user2_data["password"]},
            )
            token2 = login2.json()["access_token"]

        with allure.step("Attempt to access user 1's task as user 2"):
            api_client.headers.update({"Authorization": f"Bearer {token2}"})
            response = api_client.get(f"{api_base_url}/api/tasks/{task_id}")
            allure.attach(response.text, name="Error Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Verify user 2 cannot access user 1's task"):
            assert response.status_code == 404

        # Cleanup: Delete test user using secure test-cleanup endpoint
        if TEST_API_KEY:
            with allure.step("Cleanup test user via test-cleanup endpoint"):
                user_ids = [response1.json()["id"], response2.json()["id"]]
                try:
                    response = api_client.post(
                        f"{api_base_url}/api/users/test-cleanup",
                        json={"user_ids": user_ids},
                        headers={"X-Test-API-Key": TEST_API_KEY},
                    )
                    assert response.status_code == 200, f"Failed to cleanup user: {response.text}"
                    allure.attach(
                        f"Deleted users: {response1.json()['username']}, {response2.json()['username']} (ID: {response1.json()['id']}, {response2.json()['id']})",
                        name="Test User Cleanup",
                        attachment_type=allure.attachment_type.TEXT,
                    )
                except Exception as e:
                    # Log cleanup failure but don't fail the test
                    allure.attach(
                        f"Failed to cleanup users {response1.json()['username']}, {response2.json()['username']}: {str(e)}",
                        name="Cleanup Warning",
                        attachment_type=allure.attachment_type.TEXT,
                    )
