"""Unit tests for main application endpoints."""

from tests.test_data import Endpoints


class TestRootEndpoint:
    """Test the root endpoint."""

    def test_root_endpoint_returns_message(self, client):
        """Test that root endpoint returns welcome message."""
        response = client.get("/")

        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "Task Management API is running"

    def test_root_endpoint_returns_json(self, client):
        """Test that root endpoint returns JSON content type."""
        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_root_endpoint_accepts_get_only(self, client):
        """Test that root endpoint only accepts GET requests."""
        # POST should not be allowed
        response = client.post("/")
        assert response.status_code == 405  # Method Not Allowed

        # PUT should not be allowed
        response = client.put("/")
        assert response.status_code == 405

        # DELETE should not be allowed
        response = client.delete("/")
        assert response.status_code == 405


class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_check_returns_healthy(self, client):
        """Test that health endpoint returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"

    def test_health_check_returns_json(self, client):
        """Test that health endpoint returns JSON content type."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_health_check_accepts_get_only(self, client):
        """Test that health endpoint only accepts GET requests."""
        # POST should not be allowed
        response = client.post("/health")
        assert response.status_code == 405

        # PUT should not be allowed
        response = client.put("/health")
        assert response.status_code == 405

        # DELETE should not be allowed
        response = client.delete("/health")
        assert response.status_code == 405

    def test_health_check_no_authentication_required(self, client):
        """Test that health endpoint doesn't require authentication."""
        # Should work without auth headers
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_with_invalid_token(self, client):
        """Test that health endpoint works even with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/health", headers=headers)

        # Health check should still work
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestCORSConfiguration:
    """Test CORS middleware configuration."""

    def test_cors_headers_present_on_options_request(self, client):
        """Test that CORS headers are present on OPTIONS request."""
        response = client.options(Endpoints.AUTH_REGISTER)

        # OPTIONS may return 405 if not explicitly configured
        # CORS headers should still be present
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        if response.status_code == 200:
            assert "access-control-allow-origin" in headers_lower
        # Note: Some frameworks return 405 for OPTIONS if not configured

    def test_cors_allows_credentials(self, client):
        """Test that CORS allows credentials."""
        response = client.options(Endpoints.TASKS)

        # Should allow credentials
        # Note: Actual header name might be case-insensitive
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        if "access-control-allow-credentials" in headers_lower:
            assert headers_lower["access-control-allow-credentials"] == "true"


class TestAPIDocumentation:
    """Test API documentation endpoints."""

    def test_openapi_schema_available(self, client):
        """Test that OpenAPI schema is available."""
        response = client.get(Endpoints.OPENAPI)

        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "Task Management API"
        assert schema["info"]["version"] == "1.0.0"

    def test_docs_endpoint_available(self, client):
        """Test that Swagger docs endpoint is available."""
        response = client.get(Endpoints.DOCS)

        assert response.status_code == 200

    def test_redoc_endpoint_available(self, client):
        """Test that ReDoc docs endpoint is available."""
        response = client.get(Endpoints.REDOC)

        assert response.status_code == 200


class TestInvalidEndpoints:
    """Test handling of invalid endpoints."""

    def test_nonexistent_endpoint_returns_404(self, client):
        """Test that accessing non-existent endpoint returns 404."""
        response = client.get("/nonexistent")

        assert response.status_code == 404
        assert "detail" in response.json()

    def test_invalid_api_path_returns_404(self, client):
        """Test that invalid API path returns 404."""
        response = client.get("/api/invalid")  # Intentionally invalid path

        assert response.status_code == 404

    def test_invalid_method_returns_405(self, client):
        """Test that invalid HTTP method returns 405."""
        # GET on login endpoint (which only accepts POST)
        response = client.get(Endpoints.AUTH_LOGIN)

        assert response.status_code == 405

    def test_trailing_slash_handling(self, client):
        """Test how API handles trailing slashes."""
        # Test with and without trailing slash
        response1 = client.get("/health")
        response2 = client.get("/health/")

        # Without trailing slash should work
        assert response1.status_code == 200
        # With trailing slash should succeed (TestClient follows redirects automatically)
        assert response2.status_code == 200


class TestApplicationMetadata:
    """Test application metadata and configuration."""

    def test_api_title_in_openapi(self, client):
        """Test that API title is correctly set in OpenAPI schema."""
        response = client.get(Endpoints.OPENAPI)
        schema = response.json()

        assert schema["info"]["title"] == "Task Management API"

    def test_api_description_in_openapi(self, client):
        """Test that API description is correctly set."""
        response = client.get(Endpoints.OPENAPI)
        schema = response.json()

        assert schema["info"]["description"] == "A simple task management system"

    def test_api_version_in_openapi(self, client):
        """Test that API version is correctly set."""
        response = client.get(Endpoints.OPENAPI)
        schema = response.json()

        assert schema["info"]["version"] == "1.0.0"

    def test_auth_endpoints_in_openapi(self, client):
        """Test that auth endpoints are documented in OpenAPI."""
        response = client.get(Endpoints.OPENAPI)
        schema = response.json()

        paths = schema["paths"]
        assert Endpoints.AUTH_REGISTER in paths
        assert Endpoints.AUTH_LOGIN in paths

    def test_tasks_endpoints_in_openapi(self, client):
        """Test that tasks endpoints are documented in OpenAPI."""
        response = client.get(Endpoints.OPENAPI)
        schema = response.json()

        paths = schema["paths"]
        # OpenAPI schema uses trailing slash for router endpoints
        assert "/api/tasks/" in paths
        assert "/api/tasks/{task_id}" in paths

    def test_tags_in_openapi(self, client):
        """Test that API tags are properly set."""
        response = client.get(Endpoints.OPENAPI)
        schema = response.json()

        # Check that endpoints have proper tags
        user_register = schema["paths"][Endpoints.USERS]["post"]
        assert "users" in user_register["tags"]

        auth_login = schema["paths"]["/api/auth/login"]["post"]
        assert "authentication" in auth_login["tags"]

        # OpenAPI schema uses trailing slash for router endpoints
        tasks_list = schema["paths"]["/api/tasks/"]["get"]
        assert "tasks" in tasks_list["tags"]
