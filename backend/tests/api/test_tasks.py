"""
Unit tests for task management endpoints.
"""

from fastapi import status
from tests.test_data import Endpoints, TestHelpers, TestTasks, TestUsers


class TestTaskCreation:
    """Tests for task creation endpoint."""

    def test_create_task_success(self, client, auth_headers):
        """Test successful task creation."""
        response = client.post(Endpoints.TASKS, json=TestTasks.FULL_TASK, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        TestHelpers.assert_valid_task_response(data)
        assert data["title"] == TestTasks.FULL_TASK["title"]
        assert data["description"] == TestTasks.FULL_TASK["description"]
        assert data["priority"] == TestTasks.FULL_TASK["priority"]
        assert data["category"] == TestTasks.FULL_TASK["category"]
        assert data["is_completed"] is False

    def test_create_task_minimal_data(self, client, auth_headers):
        """Test creating task with only required fields."""
        response = client.post(Endpoints.TASKS, json=TestTasks.MINIMAL_TASK, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == TestTasks.MINIMAL_TASK["title"]
        assert data["is_completed"] is False

    def test_create_task_without_auth(self, client):
        """Test creating task without authentication fails."""
        response = client.post(Endpoints.TASKS, json={"title": "Unauthorized Task"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_task_invalid_data(self, client, auth_headers):
        """Test creating task with invalid data fails."""
        response = client.post(Endpoints.TASKS, json=TestTasks.INVALID_TASKS["missing_title"], headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestTaskRetrieval:
    """Tests for task retrieval endpoints."""

    def test_get_all_tasks(self, client, auth_headers, test_task):
        """Test retrieving all user tasks."""
        response = client.get(Endpoints.TASKS, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(task["id"] == test_task.id for task in data)

    def test_get_tasks_empty_list(self, client, auth_headers):
        """Test retrieving tasks when user has none."""
        response = client.get(Endpoints.TASKS, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_single_task(self, client, auth_headers, test_task):
        """Test retrieving a single task by ID."""
        response = client.get(Endpoints.task_by_id(test_task.id), headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == test_task.title

    def test_get_nonexistent_task(self, client, auth_headers):
        """Test retrieving nonexistent task returns 404."""
        response = client.get(Endpoints.task_by_id(99999), headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_task_without_auth(self, client, test_task):
        """Test retrieving task without authentication fails."""
        response = client.get(Endpoints.task_by_id(test_task.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_cannot_access_other_users_tasks(self, client, db_session, test_task):
        """Test that users can only access their own tasks."""
        # Create and login as another user
        other_headers = TestHelpers.create_and_login_user(
            client,
            db_session,
            TestUsers.OTHER_USER["username"],
            TestUsers.OTHER_USER["email"],
            TestUsers.OTHER_PASSWORD,
        )

        # Try to access test_task (owned by test_user)
        response = client.get(Endpoints.task_by_id(test_task.id), headers=other_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTaskUpdate:
    """Tests for task update endpoint."""

    def test_update_task_title(self, client, auth_headers, test_task):
        """Test updating task title."""
        response = client.put(Endpoints.task_by_id(test_task.id), json=TestTasks.UPDATE_TITLE, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == TestTasks.UPDATE_TITLE["title"]
        assert data["id"] == test_task.id

    def test_update_task_completion_status(self, client, auth_headers, test_task):
        """Test marking task as completed."""
        response = client.put(
            Endpoints.task_by_id(test_task.id), json=TestTasks.UPDATE_COMPLETION, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_completed"] is True

    def test_update_task_priority(self, client, auth_headers, test_task):
        """Test updating task priority."""
        response = client.put(Endpoints.task_by_id(test_task.id), json=TestTasks.UPDATE_PRIORITY, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["priority"] == TestTasks.UPDATE_PRIORITY["priority"]

    def test_update_multiple_fields(self, client, auth_headers, test_task):
        """Test updating multiple task fields at once."""
        response = client.put(Endpoints.task_by_id(test_task.id), json=TestTasks.UPDATE_MULTIPLE, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == TestTasks.UPDATE_MULTIPLE["title"]
        assert data["description"] == TestTasks.UPDATE_MULTIPLE["description"]
        assert data["priority"] == TestTasks.UPDATE_MULTIPLE["priority"]
        assert data["is_completed"] is True

    def test_update_nonexistent_task(self, client, auth_headers):
        """Test updating nonexistent task returns 404."""
        response = client.put(Endpoints.task_by_id(99999), json={"title": "Updated"}, headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_task_without_auth(self, client, test_task):
        """Test updating task without authentication fails."""
        response = client.put(Endpoints.task_by_id(test_task.id), json={"title": "Unauthorized Update"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTaskDeletion:
    """Tests for task deletion endpoint."""

    def test_delete_task_success(self, client, auth_headers, test_task):
        """Test successful task deletion."""
        response = client.delete(Endpoints.task_by_id(test_task.id), headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data

        # Verify task is actually deleted
        get_response = client.get(Endpoints.task_by_id(test_task.id), headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_task(self, client, auth_headers):
        """Test deleting nonexistent task returns 404."""
        response = client.delete(Endpoints.task_by_id(99999), headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_without_auth(self, client, test_task):
        """Test deleting task without authentication fails."""
        response = client.delete(Endpoints.task_by_id(test_task.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTaskPagination:
    """Tests for task pagination."""

    def test_pagination_skip_and_limit(self, client, auth_headers, db_session, test_user):
        """Test task pagination with skip and limit parameters."""
        # Create multiple tasks
        for i in range(15):
            TestHelpers.create_test_task(db_session, test_user.id, f"Task {i}")

        # Test with limit
        response = client.get(f"{Endpoints.TASKS}?limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

        # Test with skip
        response = client.get(f"{Endpoints.TASKS}?skip=10", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

        # Test with both
        response = client.get(f"{Endpoints.TASKS}?skip=5&limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5


class TestTaskCreationNegativeCases:
    """Additional negative test cases for task creation."""

    def test_create_task_missing_title(self, client, auth_headers):
        """Test creating task without title fails."""
        response = client.post(Endpoints.TASKS, json=TestTasks.INVALID_TASKS["missing_title"], headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_task_empty_title(self, client, auth_headers):
        """Test creating task with empty title."""
        response = client.post(Endpoints.TASKS, json=TestTasks.INVALID_TASKS["empty_title"], headers=auth_headers)

        # With min_length=1 validation, empty title should be rejected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_task_null_title(self, client, auth_headers):
        """Test creating task with null title."""
        response = client.post(Endpoints.TASKS, json=TestTasks.INVALID_TASKS["null_title"], headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_task_max_long_title(self, client, auth_headers):
        """Test creating task with max long title."""
        long_title = "A" * 100

        response = client.post(Endpoints.TASKS, json={"title": long_title}, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

    def test_create_task_very_long_description(self, client, auth_headers):
        """Test creating task with very long description."""
        response = client.post(Endpoints.TASKS, json=TestTasks.INVALID_TASKS["long_description"], headers=auth_headers)

        # With max_length=500 validation on description, very long description should be rejected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_task_invalid_priority(self, client, auth_headers):
        """Test creating task with invalid priority value."""
        response = client.post(Endpoints.TASKS, json=TestTasks.INVALID_TASKS["invalid_priority"], headers=auth_headers)

        # With Literal validation on priority, invalid values should be rejected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_task_null_priority(self, client, auth_headers):
        """Test creating task with null priority."""
        response = client.post(Endpoints.TASKS, json={"title": "Task", "priority": None}, headers=auth_headers)

        # Null priority should be rejected due to Literal validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_task_special_characters_in_title(self, client, auth_headers):
        """Test creating task with special characters in title."""
        response = client.post(
            Endpoints.TASKS, json={"title": "Task: Review & Update @mentions #hashtags <html>"}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "<html>" in data["title"]

    def test_create_task_unicode_characters(self, client, auth_headers):
        """Test creating task with unicode characters."""
        response = client.post(
            Endpoints.TASKS,
            json={"title": "任务 タスク مهمة 📝", "description": "Unicode: 你好世界"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK

    def test_create_task_sql_injection_attempt(self, client, auth_headers):
        """Test that SQL injection attempts are handled safely."""
        response = client.post(Endpoints.TASKS, json={"title": "Task'; DROP TABLE tasks;--"}, headers=auth_headers)

        # Should be safely stored as literal string
        assert response.status_code == status.HTTP_200_OK

    def test_create_task_xss_attempt(self, client, auth_headers):
        """Test that XSS attempts are handled safely."""
        response = client.post(Endpoints.TASKS, json={"title": "<script>alert('xss')</script>"}, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

    def test_create_task_with_extra_fields(self, client, auth_headers):
        """Test creating task with extra unexpected fields."""
        response = client.post(
            Endpoints.TASKS,
            json={
                "title": "Task",
                "owner_id": 99999,  # Should be ignored
                "id": 12345,  # Should be ignored
                "extra_field": "value",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # ID should be auto-generated, not the provided one
        assert data["id"] != 12345

    def test_create_task_invalid_auth_token(self, client):
        """Test creating task with invalid token."""
        response = client.post(
            Endpoints.TASKS, json={"title": "Task"}, headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_task_no_json_body(self, client, auth_headers):
        """Test creating task without JSON body."""
        response = client.post(Endpoints.TASKS, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestTaskRetrievalNegativeCases:
    """Additional negative test cases for task retrieval."""

    def test_get_task_invalid_id_type(self, client, auth_headers):
        """Test retrieving task with invalid ID type."""
        response = client.get(Endpoints.TASKS + "/invalid_id", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_get_task_negative_id(self, client, auth_headers):
        """Test retrieving task with negative ID."""
        response = client.get(Endpoints.task_by_id(-1), headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_task_zero_id(self, client, auth_headers):
        """Test retrieving task with zero ID."""
        response = client.get(Endpoints.task_by_id(0), headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_task_very_large_id(self, client, auth_headers):
        """Test retrieving task with very large ID."""
        response = client.get(Endpoints.task_by_id(9999999999999), headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_tasks_invalid_pagination_params(self, client, auth_headers):
        """Test getting tasks with invalid pagination parameters."""
        # Negative skip
        response = client.get(f"{Endpoints.TASKS}?skip=-1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_tasks_string_pagination_params(self, client, auth_headers):
        """Test getting tasks with string pagination parameters."""
        response = client.get(f"{Endpoints.TASKS}?skip=abc&limit=xyz", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_get_tasks_very_large_limit(self, client, auth_headers):
        """Test getting tasks with very large limit."""
        response = client.get(f"{Endpoints.TASKS}?limit=999999", headers=auth_headers)

        # Should succeed but return available tasks
        assert response.status_code == status.HTTP_200_OK


class TestTaskUpdateNegativeCases:
    """Additional negative test cases for task update."""

    def test_update_task_with_empty_json(self, client, auth_headers, test_task):
        """Test updating task with empty JSON body."""
        response = client.put(Endpoints.task_by_id(test_task.id), json={}, headers=auth_headers)

        # Should succeed (all fields optional in update)
        assert response.status_code == status.HTTP_200_OK

    def test_update_task_null_title(self, client, auth_headers, test_task):
        """Test updating task with null title."""
        response = client.put(Endpoints.task_by_id(test_task.id), json={"title": None}, headers=auth_headers)

        # Pydantic validation should catch null title and return 422
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert "title cannot be null" in response.text.lower()

    def test_update_task_empty_title(self, client, auth_headers, test_task):
        """Test updating task with empty title."""
        response = client.put(Endpoints.task_by_id(test_task.id), json={"title": ""}, headers=auth_headers)

        # With min_length=1 validation, empty title should be rejected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_update_task_invalid_boolean(self, client, auth_headers, test_task):
        """Test updating task with invalid boolean value."""
        response = client.put(
            Endpoints.task_by_id(test_task.id), json={"is_completed": "not_a_bool"}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_update_task_very_long_title(self, client, auth_headers, test_task):
        """Test updating task with very long title."""
        long_title = "C" * 101

        response = client.put(Endpoints.task_by_id(test_task.id), json={"title": long_title}, headers=auth_headers)

        # With max_length=100 validation, very long title should be rejected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_update_task_invalid_priority(self, client, auth_headers, test_task):
        """Test updating task with invalid priority."""
        response = client.put(
            Endpoints.task_by_id(test_task.id), json={"priority": "super_urgent"}, headers=auth_headers
        )

        # With Literal validation on priority in TaskUpdate, invalid values should be rejected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_update_task_special_characters(self, client, auth_headers, test_task):
        """Test updating task with special characters."""
        response = client.put(
            Endpoints.task_by_id(test_task.id), json={"title": "<script>alert('xss')</script>"}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

    def test_update_task_user_cannot_modify_others_task(self, client, db_session, test_task):
        """Test that user cannot update another user's task."""
        # Create and login as another user
        other_headers = TestHelpers.create_and_login_user(
            client,
            db_session,
            TestUsers.OTHER_USER_2["username"],
            TestUsers.OTHER_USER_2["email"],
            TestUsers.OTHER_PASSWORD,
        )

        # Try to update test_task (owned by test_user)
        response = client.put(Endpoints.task_by_id(test_task.id), json={"title": "Hacked"}, headers=other_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_task_invalid_id_type(self, client, auth_headers):
        """Test updating task with invalid ID type."""
        response = client.put(Endpoints.TASKS + "/invalid_id", json={"title": "Updated"}, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_update_task_no_json_body(self, client, auth_headers, test_task):
        """Test updating task without JSON body."""
        response = client.put(Endpoints.task_by_id(test_task.id), headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_update_task_with_owner_id(self, client, auth_headers, test_task):
        """Test that updating task doesn't change owner_id."""
        original_owner_id = test_task.owner_id

        response = client.put(
            Endpoints.task_by_id(test_task.id), json={"title": "Updated", "owner_id": 99999}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Owner should not change
        assert data["owner_id"] == original_owner_id


class TestTaskDeletionNegativeCases:
    """Additional negative test cases for task deletion."""

    def test_delete_task_invalid_id_type(self, client, auth_headers):
        """Test deleting task with invalid ID type."""
        response = client.delete(Endpoints.TASKS + "/invalid_id", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_delete_task_negative_id(self, client, auth_headers):
        """Test deleting task with negative ID."""
        response = client.delete(Endpoints.task_by_id(-1), headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_zero_id(self, client, auth_headers):
        """Test deleting task with zero ID."""
        response = client.delete(Endpoints.task_by_id(0), headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_user_cannot_delete_others_task(self, client, db_session, test_task):
        """Test that user cannot delete another user's task."""
        # Create and login as another user
        other_headers = TestHelpers.create_and_login_user(
            client,
            db_session,
            TestUsers.OTHER_USER_3["username"],
            TestUsers.OTHER_USER_3["email"],
            TestUsers.OTHER_PASSWORD,
        )

        # Try to delete test_task (owned by test_user)
        response = client.delete(Endpoints.task_by_id(test_task.id), headers=other_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_twice(self, client, auth_headers, test_task):
        """Test deleting same task twice."""
        # First deletion
        response = client.delete(Endpoints.task_by_id(test_task.id), headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        # Second deletion should fail
        response = client.delete(Endpoints.task_by_id(test_task.id), headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTaskPaginationNegativeCases:
    """Additional negative test cases for pagination."""

    def test_pagination_zero_limit(self, client, auth_headers):
        """Test pagination with zero limit."""
        response = client.get(f"{Endpoints.TASKS}?limit=0", headers=auth_headers)

        # Should return empty
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

    def test_pagination_skip_beyond_total(self, client, auth_headers, db_session, test_user):
        """Test pagination skip beyond total number of tasks."""
        # Create 5 tasks
        for i in range(5):
            TestHelpers.create_test_task(db_session, test_user.id, f"Task {i}")

        # Skip beyond total
        response = client.get(f"{Endpoints.TASKS}?skip=100", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

    def test_pagination_float_parameters(self, client, auth_headers):
        """Test pagination with float parameters."""
        response = client.get(f"{Endpoints.TASKS}?skip=1.5&limit=5.5", headers=auth_headers)

        # Should fail or coerce to int
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
