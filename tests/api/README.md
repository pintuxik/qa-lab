# API Integration Tests - Complete Guide

> Comprehensive integration tests for the Task Management API with Allure reporting

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Test Coverage](#test-coverage)
- [Setup Options](#setup-options)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## Quick Start

### 1. Start Backend

**Option A: Automated (Recommended)**
```bash
./setup_backend_for_tests.sh
```

**Option B: Docker Compose**
```bash
docker compose up -d
```

### 2. Run Tests

```bash
./run_api_tests.sh
```

That's it! ✅

---

## Test Coverage

### 📊 Statistics
- **Total Tests**: 34 integration tests
- **Test Files**: 2 (`test_auth_api.py`, `test_tasks_api.py`)
- **Execution Time**: ~10 seconds
- **Coverage**: Complete API endpoint coverage

### 🔐 Authentication API (13 tests)

**User Registration**
- ✅ Successful registration with valid data
- ✅ Duplicate email/username validation
- ✅ Missing required fields validation

**User Login**
- ✅ Successful login with valid credentials
- ✅ Failed login (wrong password, non-existent user)
- ✅ Form data format validation

**Token Authentication**
- ✅ Access with valid token
- ✅ Rejection without token
- ✅ Rejection with invalid token

### 📝 Tasks API (21 tests)

**Task Creation** - Create tasks with validation
**Task Retrieval** - Get all/single tasks, pagination, empty lists
**Task Update** - Update title, completion, priority, multiple fields
**Task Deletion** - Delete tasks with proper authorization
**Task Isolation** - Users cannot access other users' tasks

---

## Setup Options

### Option 1: Automated Script ⭐

Handles everything automatically:

```bash
./setup_backend_for_tests.sh
```

**What it does:**
- Starts PostgreSQL container
- Initializes database (creates tables)
- Creates admin user (admin/admin123)
- Starts backend API on port 8000
- Verifies everything is healthy

**Management:**
```bash
./stop_backend.sh                      # Stop backend only
./stop_backend.sh --database           # Stop backend + database
./stop_backend.sh --clean              # Clean up everything
./setup_backend_for_tests.sh --help    # Show setup options
```

### Option 2: Docker Compose

```bash
docker compose up -d
docker compose logs -f backend  # Wait for "Application startup complete"
```

### Option 3: Manual Setup

```bash
# 1. Start PostgreSQL
docker run -d --name qa-lab-postgres \
  -e POSTGRES_DB=taskmanager \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 postgres:15

# 2. Initialize database
cd backend
export DATABASE_URL="postgresql://postgres:password@localhost:5432/taskmanager"
uv sync --extra test
uv run python app/init_db.py

# 3. Start backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Verify Setup

```bash
curl http://localhost:8000/health  # Should return: {"status":"healthy"}
```

---

## Running Tests

### Basic Usage

```bash
# Run all integration tests
./run_api_tests.sh

# Or with pytest directly
uv run pytest tests/api/ -m integration -v
```

### Specific Tests

```bash
# Run specific file
uv run pytest tests/api/test_auth_api.py -v

# Run specific class
uv run pytest tests/api/test_auth_api.py::TestUserRegistration -v

# Run specific test
uv run pytest tests/api/test_auth_api.py::TestUserRegistration::test_register_user_success -v
```

### With Allure Reports

```bash
# Generate Allure results
./run_api_tests.sh --allure

# Or manually
uv run pytest tests/api/ -m integration --alluredir=allure-results
allure serve allure-results
```

### Useful Options

```bash
# Verbose output
uv run pytest tests/api/ -m integration -v

# Stop on first failure
uv run pytest tests/api/ -m integration -x

# Show print statements
uv run pytest tests/api/ -m integration -s

# Filter by test name pattern
uv run pytest tests/api/ -m integration -k "login"
```

---

## Troubleshooting

### 🔴 Backend Not Running

**Error:** `Connection refused`

**Fix:**
```bash
curl http://localhost:8000/health  # Check if running
./setup_backend_for_tests.sh      # Start if not running
```

### 🔴 Port Already in Use

**Error:** `Address already in use`

**Fix:**
```bash
lsof -i :8000                      # Find process
./stop_backend.sh                  # Stop backend
# OR
pkill -f uvicorn                   # Kill all uvicorn
```

### 🔴 Database Not Initialized

**Error:** `relation "users" does not exist`

**Fix:**
```bash
cd backend
uv run python app/init_db.py
```

### 🔴 Tests Hang or Timeout

**Fix:**
```bash
# Check backend logs
tail -f backend.log

# Restart backend
./stop_backend.sh
./setup_backend_for_tests.sh
```

### 🔴 Script Freezes at "Starting backend API..."

**Cause:** Backend already running

**Fix:**
```bash
# Backend is already running - just run tests
./run_api_tests.sh

# Or stop and restart
./stop_backend.sh
./setup_backend_for_tests.sh
```

### 🆘 Clean Slate

Start fresh with everything:

```bash
./stop_backend.sh --clean
./setup_backend_for_tests.sh
./run_api_tests.sh
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

**Default Admin User:**
- Username: `admin`
- Password: `admin123`
- Email: `admin@example.com`

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

**GitHub Actions Example:**
```yaml
- name: Setup Backend
  run: ./setup_backend_for_tests.sh --docker-compose

- name: Run Integration Tests
  run: ./run_api_tests.sh --skip-check --allure

- name: Cleanup
  if: always()
  run: ./stop_backend.sh --clean
```

### Debugging

**View Logs:**
```bash
tail -f backend.log                    # Backend logs (setup script)
docker compose logs -f backend         # Backend logs (docker-compose)
docker logs qa-lab-postgres            # PostgreSQL logs
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

## Test Structure

```
tests/api/
├── conftest.py           # Fixtures and configuration
├── test_auth_api.py      # Authentication tests (13 tests)
├── test_tasks_api.py     # Tasks tests (21 tests)
└── GUIDE.md              # This file
```

### Key Features

✅ **Test Isolation** - Each test creates its own data
✅ **Unique Identifiers** - Timestamp + random for unique users
✅ **Comprehensive Assertions** - Status codes, response structure, data validation
✅ **Allure Integration** - Detailed reports with steps and attachments
✅ **CI/CD Ready** - Fast execution, no external dependencies
✅ **Well Documented** - Clear test names and descriptions

---

## Quick Reference

### Common Commands

```bash
# Setup
./setup_backend_for_tests.sh                    # Start everything
./stop_backend.sh                               # Stop backend
./stop_backend.sh --clean                       # Clean up all

# Run Tests
./run_api_tests.sh                              # Run all tests
./run_api_tests.sh --allure                     # With Allure report
./run_api_tests.sh --test tests/api/test_auth_api.py  # Specific file

# Verify
curl http://localhost:8000/health               # Check backend
docker ps | grep postgres                       # Check database
```

### Scenarios

**First Time:**
```bash
./setup_backend_for_tests.sh && ./run_api_tests.sh
```

**Backend Already Running:**
```bash
./run_api_tests.sh
```

**Something Went Wrong:**
```bash
./stop_backend.sh --clean && ./setup_backend_for_tests.sh && ./run_api_tests.sh
```

---

## Getting Help

1. **Check if backend is running:** `curl http://localhost:8000/health`
2. **View backend logs:** `tail -f backend.log`
3. **Check database:** `docker ps | grep postgres`
4. **Try clean slate:** `./stop_backend.sh --clean && ./setup_backend_for_tests.sh`
5. **Run with verbose output:** `uv run pytest tests/api/ -m integration -vv`

---

## Summary

- **34 integration tests** covering all API endpoints
- **3 setup options** (automated, docker-compose, manual)
- **~10 second execution** time
- **Allure reporting** for detailed test results
- **CI/CD ready** with automated scripts
- **Comprehensive troubleshooting** guide included

**Ready to test?** Run `./setup_backend_for_tests.sh && ./run_api_tests.sh` 🚀
