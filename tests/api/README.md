# API Integration Tests - Complete Guide

Comprehensive integration tests for the Task Management API with Allure reporting

## Summary

- **34 integration tests** covering all API endpoints
- **~10 second execution** time
- **Allure reporting** for detailed test results
- **CI/CD ready** with automated scripts

## 🚀 Quick Start

### Prerequisites

**Start Backend**
```bash
docker compose up -d
```

### Running Tests Usage

```bash
# Run all integration tests
./run_api_tests.sh

# Or with pytest directly
uv run pytest api/ -m integration -v
```

### Specific Tests

```bash
# Run specific file
uv run pytest api/test_auth_api.py -v

# Run specific class
uv run pytest api/test_auth_api.py::TestUserRegistration -v

# Run specific test
uv run pytest api/test_auth_api.py::TestUserRegistration::test_register_user_success -v
```

### With Allure Reports

```bash
# Generate Allure results
./run_api_tests.sh --allure

# Or manually
uv run pytest api/ -m integration --alluredir=allure-results
allure serve allure-results
```

### Useful Options

```bash
# Verbose output
uv run pytest api/ -m integration -v

# Stop on first failure
uv run pytest api/ -m integration -x

# Show print statements
uv run pytest api/ -m integration -s

# Filter by test name pattern
uv run pytest api/ -m integration -k "login"
```

---

## Advanced Usage

### Configuration

**Environment Variables:**
```bash
export API_BASE_URL="http://localhost:8000"  # Change API URL
./run_api_tests.sh
```

**Database Connection:**
- Host: `localhost:5432`
- Database: `taskmanager`
- User: `postgres`
- Password: `password`

### Test Fixtures

Available in `conftest.py`:

- **`api_client`** - Requests session for API calls
- **`test_user_credentials`** - Unique test user data
- **`registered_user`** - Pre-registered test user
- **`auth_token`** - Authentication token
- **`authenticated_client`** - Authenticated API client

### Allure Annotations

Tests use Allure for rich reporting:

```python
@allure.feature("Authentication API")
@allure.story("User Registration")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Register new user successfully")
def test_register_user_success(self, api_client, api_base_url):
    with allure.step("Prepare registration data"):
        # Test code
```

### CI/CD Integration

**UNDER CONSTRUCTION**

### Debugging

**View Logs:**
```bash
docker compose logs -f backend         # Backend logs (docker-compose)
docker logs db            # PostgreSQL logs
```

**Check Services:**
```bash
docker ps                              # All containers
curl -v http://localhost:8000/health   # Backend health
docker exec qa-lab-postgres psql -U postgres -d taskmanager -c "\dt"  # Database tables
```

**Verbose Test Output:**
```bash
uv run pytest tests/api/ -m integration -vv -s --log-cli-level=DEBUG
```

---

### Key Features

✅ **Test Isolation** - Each test creates its own data
✅ **Unique Identifiers** - Timestamp + random for unique users
✅ **Comprehensive Assertions** - Status codes, response structure, data validation
✅ **Allure Integration** - Detailed reports with steps and attachments
✅ **CI/CD Ready** - Fast execution, no external dependencies
✅ **Well Documented** - Clear test names and descriptions

---
