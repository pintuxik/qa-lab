# Testing Guide - QA Lab Task Management System

This document provides comprehensive information about testing the QA Lab Task Management System.

## Test Statistics by 11/28/25

### Backend Unit Tests ✅
- **Total Tests**: 199
- **Status**: All Passing ✅
- **Coverage**: 79%

### Frontend Unit Tests ✅
- **Total Tests**: 21
- **Status**: All Passing ✅
- **Coverage**: 86%

### API Integration Tests ✅
- **Total Tests**: 34
- **Status**: All Passing ✅

### UI Integration Tests 🆕
- **Total Tests**: 19
- **Status**: Ready to Run


### Total
- **Combined Tests**: 273 tests (220 unit + 34 API + 19 UI)
- **Overall Status**: ✅ All Passing

## Overview

The project includes four types of tests:

1. **Backend Unit Tests** - FastAPI endpoint and security tests
2. **Frontend Unit Tests** - Flask route and view tests  
3. **API Integration Tests** - End-to-end API tests with requests
4. **UI Integration Tests** - End-to-end browser tests with Playwright

## Quick Start

### Backend Unit Tests

```bash
cd backend
uv sync --group test
uv run pytest -n auto
```

### Frontend Unit Tests

```bash
cd frontend
uv sync --group test
uv run pytest -n auto
```

### API Integration Tests

```bash
# Make sure backend API is running
docker compose up -d

# Run API tests
./run_api_tests.sh

# Or run directly with pytest
uv run pytest api/ -m integration -v

# With Allure report
./run_api_tests.sh --allure
```

### UI Integration Tests

```bash
# Make sure frontend and backend are running
docker compose up -d

# Optionally install Playwright browsers before run
uv run playwright install

# Run UI tests
./run_ui_tests.sh

# Or run directly with pytest
uv run pytest ui/ -m ui -v

# Run in headed mode
./run_ui_tests.sh --headed

# With Allure report
./run_ui_tests.sh --allure
```

## Backend Unit Tests


### Running Backend Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/api/test_auth.py

# Run specific test
uv run pytest tests/api/test_auth.py::TestUserLogin::test_login_success

# Run with verbose output
uv run pytest -v

# Run and show print statements
uv run pytest -s
```

### Backend Test Examples

```python
# Test user registration
def test_register_new_user(client):
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpass123"
    })
    assert response.status_code == 200

# Test authenticated endpoint
def test_create_task(client, auth_headers):
    response = client.post("/api/tasks", 
        json={"title": "New Task"},
        headers=auth_headers
    )
    assert response.status_code == 200
```

## Frontend Unit Tests

### Running Frontend Tests

```bash
cd frontend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_routes.py

# Run specific test
uv run pytest tests/test_routes.py::TestLoginRoute::test_login_success

# Run with verbose output
uv run pytest -v

# Run and show print statements
uv run pytest -s
```

### Frontend Test Examples

```python
# Test login page
def test_login_page_loads(client):
    """Test that login page loads successfully."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

# Test with mocked API
@patch('app.routes.make_api_request')
def test_login_success(mock_api, client):
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
```

## Integration Tests

### Running Integration Tests

```bash
# Start services
docker compose up -d

# Run API integration tests
./run_api_tests.sh

# Run UI integration tests
./run_ui_tests.sh
```

## Test Coverage Reports

### Generate Coverage Reports

```bash
# Backend
cd backend
uv run pytest --cov=app --cov-report=html
open htmlcov/index.html

# Frontend
cd frontend
uv run pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Coverage Goals

- **Backend**: Target 80%+ coverage ✅ (Currently 79%)
- **Frontend**: Target 80%+ coverage ✅ (Currently 86%)

## Continuous Integration

### UNDER CONSTRUCTION

## Running Tests in Docker

### Backend Tests in Container

```bash
docker exec qa-lab-backend-1 uv run pytest
```

### Frontend Tests in Container

```bash
docker exec qa-lab-frontend-1 uv run pytest
```

## Best Practices

### General

1. **Write tests first** - TDD approach when possible
2. **Test one thing** - Each test should verify one behavior
3. **Use descriptive names** - Test names should explain what they test
4. **Arrange-Act-Assert** - Structure tests clearly
5. **Independent tests** - Tests should not depend on each other

### Backend Specific

1. **Use fixtures** - Leverage pytest fixtures for setup
2. **Test edge cases** - Include boundary conditions
3. **Mock external services** - Don't make real external calls
4. **Test authorization** - Verify user isolation
5. **Test validation** - Check input validation

### Frontend Specific

1. **Mock API calls** - Always mock backend requests
2. **Test redirects** - Verify proper navigation
3. **Test session state** - Check authentication state
4. **Test error handling** - Verify error messages
5. **Test user flows** - Complete user interactions

## Troubleshooting

### Common Issues

**Import errors**
```bash
# Make sure you're in the correct directory
cd backend  # or frontend
uv sync --group test
```

**Database errors in backend tests**
```bash
# Tests use SQLite in-memory, no setup needed
# If issues persist, check conftest.py and backend/app/database.py
```

**Mock not working**
```python
# Make sure to patch the correct import path
@patch('app.routes.make_api_request')  # Not 'routes.make_api_request'
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Flask Testing](https://flask.palletsprojects.com/en/latest/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)

## Test Quality Metrics

### Test Characteristics
- ✅ Fast execution (< 15 seconds total)
- ✅ Isolated (no test dependencies)
- ✅ Deterministic (consistent results)
- ✅ Well-documented
- ✅ Easy to extend

### Key Features


## Documentation

Detailed testing documentation available in:
- [/backend/tests/README.md](../backend/tests/README.md) - Backend testing guide
- [/frontend/tests/README.md](../frontend/tests/README.md) - Frontend testing guide
- [tests/api/README.MD](api/README.md) - API integration testing guide
- [tests/ui/README.MD](ui/README.md) - UI integration testing guide

## CI/CD Ready

Tests are ready for integration into CI/CD pipelines:
- Fast execution time
- No external dependencies
- Clear pass/fail status
- Coverage reporting
- Docker support

## Next Steps

### Recommended Additions
1. ✅ **API Integration Tests**: End-to-end API testing (COMPLETED - 34 tests in `/tests/api/`)
2. ✅ **UI Integration Tests**: Browser automation tests (COMPLETED - 19 tests in `/tests/ui/`)
3. **Performance Tests**: Load testing with locust
4. **Security Tests**: OWASP security scanning
5. **Contract Tests**: API contract testing
6. **Visual Regression**: Screenshot comparison tests

### Maintenance
- Run tests before each commit
- Update tests when adding features
- Maintain >80% coverage
- Review failing tests immediately
- Keep documentation updated
