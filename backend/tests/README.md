# Backend Unit Tests

This directory contains comprehensive unit tests for the FastAPI backend.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures and configuration
├── test_auth.py         # Authentication endpoint tests
├── test_tasks.py        # Task management endpoint tests
└── test_security.py     # Security function tests
```

## Running Tests

### Install Test Dependencies

```bash
cd backend
uv sync --extra test
```

### Run All Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_auth.py

# Run specific test class
uv run pytest tests/test_auth.py::TestUserRegistration

# Run specific test
uv run pytest tests/test_auth.py::TestUserRegistration::test_register_new_user
```

### Run Tests with Verbose Output

```bash
uv run pytest -v
```

### Run Tests and Show Print Statements

```bash
uv run pytest -s
```

## Test Coverage

After running tests with coverage, open the HTML report:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Categories

### Authentication Tests (`test_auth.py`)
- User registration (success, duplicate email, duplicate username)
- User login (success, wrong password, nonexistent user)
- Token-based authentication
- Protected endpoint access

### Task Tests (`test_tasks.py`)
- Task creation (success, without auth, invalid data)
- Task retrieval (all tasks, single task, nonexistent task)
- Task updates (title, completion status, priority, multiple fields)
- Task deletion
- Task pagination
- User isolation (users can only access their own tasks)

### Security Tests (`test_security.py`)
- Password hashing (correctness, uniqueness, special characters)
- Password verification
- JWT token creation and validation
- User authentication

## Writing New Tests

1. Create a new test file: `test_<feature>.py`
2. Import necessary fixtures from `conftest.py`
3. Organize tests into classes by feature
4. Use descriptive test names: `test_<action>_<expected_result>`

Example:

```python
class TestNewFeature:
    """Tests for new feature."""
    
    def test_feature_success(self, client, auth_headers):
        """Test successful feature execution."""
        response = client.post("/api/feature", headers=auth_headers)
        assert response.status_code == 200
```

## Fixtures Available

- `db_session`: Fresh database session for each test
- `client`: TestClient for making API requests
- `test_user`: Pre-created test user
- `admin_user`: Pre-created admin user
- `auth_token`: Authentication token for test user
- `auth_headers`: Authorization headers with token
- `test_task`: Pre-created test task

## Best Practices

1. **Isolation**: Each test should be independent
2. **Arrange-Act-Assert**: Structure tests clearly
3. **Descriptive Names**: Test names should describe what they test
4. **Mock External Services**: Don't make real API calls
5. **Test Edge Cases**: Include error conditions and boundary cases
