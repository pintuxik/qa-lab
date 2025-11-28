# Frontend Unit Tests

This directory contains comprehensive unit tests for the Flask frontend.

## Running Tests

### Install Test Dependencies

```bash
cd frontend
uv sync --extra test
```

### Run All Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_routes.py

# Run specific test class
uv run pytest tests/test_routes.py::TestLoginRoute

# Run specific test
uv run pytest tests/test_routes.py::TestLoginRoute::test_login_success
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
htmlcov/index.html
```

## Test Categories

### Route Tests (`test_routes.py`)

#### Index Route
- Redirect to login when not authenticated
- Redirect to dashboard when authenticated

#### Login Route
- Login page loads
- Successful login
- Failed login with wrong credentials
- Form data vs JSON handling

#### Register Route
- Registration page loads
- Successful registration
- Duplicate user handling

#### Logout Route
- Session clearing

#### Dashboard Route
- Authentication requirement
- Loading with tasks
- Handling empty task list

#### Task Management Routes
- Task creation
- Task toggle (completion status)
- Task deletion
- Authentication requirements

#### API Helper Tests
- JSON data requests
- Form data requests
- Connection error handling

## Writing New Tests

1. Create a new test file or add to existing: `test_<feature>.py`
2. Import necessary fixtures from `conftest.py`
3. Use mocking for external API calls
4. Organize tests into classes by feature

Example:

```python
from unittest.mock import Mock, patch

class TestNewFeature:
    """Tests for new feature."""
    
    @patch('app.routes.make_api_request')
    def test_feature_success(self, mock_api, authenticated_client):
        """Test successful feature execution."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_api.return_value = mock_response
        
        response = authenticated_client.get('/feature')
        assert response.status_code == 200
```

## Fixtures Available

- `app`: Flask test application
- `client`: Test client for making requests
- `runner`: CLI test runner
- `authenticated_client`: Client with authenticated session

## Mocking External APIs

All tests that interact with the backend API should mock the `make_api_request` function:

```python
@patch('app.routes.make_api_request')
def test_example(self, mock_api, client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'key': 'value'}
    mock_api.return_value = mock_response
    
    # Your test code here
```

## Best Practices

1. **Mock External Calls**: Always mock API requests to the backend
2. **Test User Flows**: Test complete user interactions
3. **Check Redirects**: Verify proper redirects for authentication
4. **Session Management**: Test session state changes
5. **Error Handling**: Test error conditions and edge cases
6. **Response Content**: Verify expected content in responses

## Common Patterns

### Testing Authenticated Routes

```python
def test_protected_route(self, authenticated_client):
    response = authenticated_client.get('/protected')
    assert response.status_code == 200
```

### Testing Redirects

```python
def test_redirect(self, client):
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location
```

### Testing Flash Messages

```python
def test_flash_message(self, client):
    response = client.post('/action')
    assert b'Success message' in response.data
```
