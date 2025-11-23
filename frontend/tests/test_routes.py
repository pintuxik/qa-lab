"""
Unit tests for Flask routes.
"""

from unittest.mock import Mock, patch


class TestIndexRoute:
    """Tests for index route."""

    def test_index_redirects_to_login_when_not_authenticated(self, client):
        """Test that index redirects to login for unauthenticated users."""
        response = client.get("/")

        assert response.status_code == 302
        assert "/login" in response.location

    def test_index_redirects_to_dashboard_when_authenticated(self, authenticated_client):
        """Test that index redirects to dashboard for authenticated users."""
        response = authenticated_client.get("/")

        assert response.status_code == 302
        assert "/dashboard" in response.location


class TestLoginRoute:
    """Tests for login route."""

    def test_login_page_loads(self, client):
        """Test that login page loads successfully."""
        response = client.get("/login")

        assert response.status_code == 200
        assert b"Login" in response.data

    @patch("app.routes.make_api_request")
    def test_login_success(self, mock_api, client):
        """Test successful login."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token_123", "token_type": "bearer"}
        mock_api.return_value = mock_response

        response = client.post(
            "/login", data={"username": "testuser", "password": "testpass123"}, follow_redirects=False
        )

        assert response.status_code == 302
        assert "/dashboard" in response.location

        # Verify API was called with correct parameters
        mock_api.assert_called_once()
        call_args = mock_api.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/api/auth/login"
        assert call_args[1]["use_form_data"] is True

    @patch("app.routes.make_api_request")
    def test_login_failure(self, mock_api, client):
        """Test login with invalid credentials."""
        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_api.return_value = mock_response

        response = client.post("/login", data={"username": "testuser", "password": "wrongpassword"})

        assert response.status_code == 200
        assert b"Invalid username or password" in response.data


class TestRegisterRoute:
    """Tests for registration route."""

    def test_register_page_loads(self, client):
        """Test that registration page loads successfully."""
        response = client.get("/register")

        assert response.status_code == 200
        assert b"Register" in response.data

    @patch("app.routes.make_api_request")
    def test_register_success(self, mock_api, client):
        """Test successful user registration."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1, "username": "newuser", "email": "newuser@example.com"}
        mock_api.return_value = mock_response

        response = client.post(
            "/register",
            data={"username": "newuser", "email": "newuser@example.com", "password": "newpass123"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/login" in response.location

    @patch("app.routes.make_api_request")
    def test_register_duplicate_user(self, mock_api, client):
        """Test registration with duplicate username."""
        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Username already taken"}
        mock_api.return_value = mock_response

        response = client.post(
            "/register", data={"username": "existinguser", "email": "user@example.com", "password": "password123"}
        )

        assert response.status_code == 200
        # Check for the actual error message displayed
        assert b"Username already taken" in response.data


class TestLogoutRoute:
    """Tests for logout route."""

    def test_logout_clears_session(self, authenticated_client):
        """Test that logout clears the session."""
        response = authenticated_client.get("/logout", follow_redirects=False)

        assert response.status_code == 302
        assert "/login" in response.location

        # Verify session is cleared
        with authenticated_client.session_transaction() as sess:
            assert "access_token" not in sess
            assert "username" not in sess


class TestDashboardRoute:
    """Tests for dashboard route."""

    def test_dashboard_requires_authentication(self, client):
        """Test that dashboard requires authentication."""
        response = client.get("/dashboard")

        assert response.status_code == 302
        assert "/login" in response.location

    @patch("app.routes.make_api_request")
    def test_dashboard_loads_with_tasks(self, mock_api, authenticated_client):
        """Test that dashboard loads with user tasks."""
        # Mock API response with tasks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1,
                "title": "Test Task",
                "description": "Description",
                "is_completed": False,
                "priority": "high",
                "category": "work",
                "created_at": "2024-01-01T00:00:00",
            }
        ]
        mock_api.return_value = mock_response

        response = authenticated_client.get("/dashboard")

        assert response.status_code == 200
        assert b"Test Task" in response.data

    @patch("app.routes.make_api_request")
    def test_dashboard_handles_empty_tasks(self, mock_api, authenticated_client):
        """Test dashboard with no tasks."""
        # Mock API response with empty list
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_api.return_value = mock_response

        response = authenticated_client.get("/dashboard")

        assert response.status_code == 200


class TestTaskCreation:
    """Tests for task creation route."""

    def test_create_task_requires_authentication(self, client):
        """Test that task creation requires authentication."""
        response = client.post("/tasks", data={"title": "New Task"})

        assert response.status_code == 302
        assert "/login" in response.location

    @patch("app.routes.make_api_request")
    def test_create_task_success(self, mock_api, authenticated_client):
        """Test successful task creation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "title": "New Task", "description": "Description"}
        mock_api.return_value = mock_response

        response = authenticated_client.post(
            "/tasks",
            data={"title": "New Task", "description": "Description", "priority": "high", "category": "work"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/dashboard" in response.location


class TestTaskToggle:
    """Tests for task toggle route."""

    def test_toggle_task_requires_authentication(self, client):
        """Test that task toggle requires authentication."""
        response = client.post("/tasks/1/toggle")

        assert response.status_code == 302
        assert "/login" in response.location

    @patch("app.routes.make_api_request")
    def test_toggle_task_success(self, mock_api, authenticated_client):
        """Test successful task toggle."""
        # Mock GET response for current task
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": 1, "title": "Task", "is_completed": False}

        # Mock PUT response for update
        mock_put_response = Mock()
        mock_put_response.status_code = 200
        mock_put_response.json.return_value = {"id": 1, "title": "Task", "is_completed": True}

        mock_api.side_effect = [mock_get_response, mock_put_response]

        response = authenticated_client.post("/tasks/1/toggle", follow_redirects=False)

        assert response.status_code == 302
        assert "/dashboard" in response.location


class TestTaskDeletion:
    """Tests for task deletion route."""

    def test_delete_task_requires_authentication(self, client):
        """Test that task deletion requires authentication."""
        response = client.post("/tasks/1/delete")

        assert response.status_code == 302
        assert "/login" in response.location

    @patch("app.routes.make_api_request")
    def test_delete_task_success(self, mock_api, authenticated_client):
        """Test successful task deletion."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_api.return_value = mock_response

        response = authenticated_client.post("/tasks/1/delete", follow_redirects=False)

        assert response.status_code == 302
        assert "/dashboard" in response.location


class TestAPIRequestHelper:
    """Tests for API request helper function."""

    @patch("app.routes.requests.post")
    def test_make_api_request_with_json(self, mock_post, app):
        """Test making API request with JSON data."""
        from app.routes import make_api_request

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with app.app_context():
            with app.test_request_context():
                result = make_api_request("POST", "/api/test", data={"key": "value"})

        assert result == mock_response
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert "json" in call_kwargs
        assert call_kwargs["json"] == {"key": "value"}

    @patch("app.routes.requests.post")
    def test_make_api_request_with_form_data(self, mock_post, app):
        """Test making API request with form data."""
        from app.routes import make_api_request

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with app.app_context():
            with app.test_request_context():
                result = make_api_request("POST", "/api/test", data={"key": "value"}, use_form_data=True)

        assert result == mock_response
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert "data" in call_kwargs
        assert call_kwargs["data"] == {"key": "value"}

    @patch("app.routes.requests.get")
    def test_make_api_request_connection_error(self, mock_get, app):
        """Test handling connection error in API request."""
        import requests
        from app.routes import make_api_request

        mock_get.side_effect = requests.exceptions.ConnectionError()

        with app.app_context():
            with app.test_request_context():
                result = make_api_request("GET", "/api/test")

        assert result is None
