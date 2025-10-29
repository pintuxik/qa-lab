"""
Unit tests for task management endpoints.
"""

from fastapi import status


class TestTaskCreation:
    """Tests for task creation endpoint."""

    def test_create_task_success(self, client, auth_headers):
        """Test successful task creation."""
        response = client.post(
            "/api/tasks",
            json={"title": "New Task", "description": "Task description", "priority": "high", "category": "work"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Task description"
        assert data["priority"] == "high"
        assert data["category"] == "work"
        assert data["is_completed"] is False
        assert "id" in data
        assert "owner_id" in data

    def test_create_task_minimal_data(self, client, auth_headers):
        """Test creating task with only required fields."""
        response = client.post("/api/tasks", json={"title": "Minimal Task"}, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["is_completed"] is False

    def test_create_task_without_auth(self, client):
        """Test creating task without authentication fails."""
        response = client.post("/api/tasks", json={"title": "Unauthorized Task"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_task_invalid_data(self, client, auth_headers):
        """Test creating task with invalid data fails."""
        response = client.post(
            "/api/tasks",
            json={},  # Missing required title
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTaskRetrieval:
    """Tests for task retrieval endpoints."""

    def test_get_all_tasks(self, client, auth_headers, test_task):
        """Test retrieving all user tasks."""
        response = client.get("/api/tasks", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(task["id"] == test_task.id for task in data)

    def test_get_tasks_empty_list(self, client, auth_headers):
        """Test retrieving tasks when user has none."""
        response = client.get("/api/tasks", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_single_task(self, client, auth_headers, test_task):
        """Test retrieving a single task by ID."""
        response = client.get(f"/api/tasks/{test_task.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == test_task.title

    def test_get_nonexistent_task(self, client, auth_headers):
        """Test retrieving nonexistent task returns 404."""
        response = client.get("/api/tasks/99999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_task_without_auth(self, client, test_task):
        """Test retrieving task without authentication fails."""
        response = client.get(f"/api/tasks/{test_task.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_cannot_access_other_users_tasks(self, client, db_session, test_task):
        """Test that users can only access their own tasks."""
        from app.core.security import get_password_hash
        from app.models import User

        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("otherpass"),
            is_active=True,
        )
        db_session.add(other_user)
        db_session.commit()

        # Login as other user
        response = client.post("/api/auth/login", data={"username": "otheruser", "password": "otherpass"})
        other_token = response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # Try to access test_task (owned by test_user)
        response = client.get(f"/api/tasks/{test_task.id}", headers=other_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTaskUpdate:
    """Tests for task update endpoint."""

    def test_update_task_title(self, client, auth_headers, test_task):
        """Test updating task title."""
        response = client.put(f"/api/tasks/{test_task.id}", json={"title": "Updated Title"}, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["id"] == test_task.id

    def test_update_task_completion_status(self, client, auth_headers, test_task):
        """Test marking task as completed."""
        response = client.put(f"/api/tasks/{test_task.id}", json={"is_completed": True}, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_completed"] is True

    def test_update_task_priority(self, client, auth_headers, test_task):
        """Test updating task priority."""
        response = client.put(f"/api/tasks/{test_task.id}", json={"priority": "low"}, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["priority"] == "low"

    def test_update_multiple_fields(self, client, auth_headers, test_task):
        """Test updating multiple task fields at once."""
        response = client.put(
            f"/api/tasks/{test_task.id}",
            json={
                "title": "Updated Task",
                "description": "Updated description",
                "priority": "medium",
                "is_completed": True,
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["description"] == "Updated description"
        assert data["priority"] == "medium"
        assert data["is_completed"] is True

    def test_update_nonexistent_task(self, client, auth_headers):
        """Test updating nonexistent task returns 404."""
        response = client.put("/api/tasks/99999", json={"title": "Updated"}, headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_task_without_auth(self, client, test_task):
        """Test updating task without authentication fails."""
        response = client.put(f"/api/tasks/{test_task.id}", json={"title": "Unauthorized Update"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTaskDeletion:
    """Tests for task deletion endpoint."""

    def test_delete_task_success(self, client, auth_headers, test_task):
        """Test successful task deletion."""
        response = client.delete(f"/api/tasks/{test_task.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data

        # Verify task is actually deleted
        get_response = client.get(f"/api/tasks/{test_task.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_task(self, client, auth_headers):
        """Test deleting nonexistent task returns 404."""
        response = client.delete("/api/tasks/99999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_without_auth(self, client, test_task):
        """Test deleting task without authentication fails."""
        response = client.delete(f"/api/tasks/{test_task.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTaskPagination:
    """Tests for task pagination."""

    def test_pagination_skip_and_limit(self, client, auth_headers, db_session, test_user):
        """Test task pagination with skip and limit parameters."""
        from app.models import Task

        # Create multiple tasks
        for i in range(15):
            task = Task(title=f"Task {i}", owner_id=test_user.id)
            db_session.add(task)
        db_session.commit()

        # Test with limit
        response = client.get("/api/tasks?limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

        # Test with skip
        response = client.get("/api/tasks?skip=10", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

        # Test with both
        response = client.get("/api/tasks?skip=5&limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5
