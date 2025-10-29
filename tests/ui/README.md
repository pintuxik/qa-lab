# UI Integration Tests

Comprehensive UI integration tests for the Task Management application using Playwright and Allure reporting.

## 📊 Test Coverage

### Statistics
- **Total Tests**: 19 UI tests
- **Test Files**: 2
  - `test_auth_ui.py` - Authentication flows (11 tests)
  - `test_tasks_ui.py` - Task management flows (8 tests)
- **Browser**: Chromium (Chrome)
- **Framework**: Playwright + Pytest + Allure

### Test Scenarios

#### Authentication (11 tests)
- ✅ User registration with validation
- ✅ User login with valid/invalid credentials
- ✅ User logout
- ✅ Protected route access
- ✅ Form validation
- ✅ Navigation between auth pages

#### Task Management (8 tests)
- ✅ Dashboard loading and statistics
- ✅ Task creation (full and minimal)
- ✅ Task completion
- ✅ Task deletion
- ✅ Task details viewing
- ✅ Task filtering by priority
- ✅ Empty state handling

## 🚀 Quick Start

### Prerequisites

1. **Frontend and Backend running**
   ```bash
   docker compose up -d
   # OR
   ./setup_backend_for_tests.sh
   ```

2. **Install Playwright browsers** (first time only)
   ```bash
   uv run playwright install chromium
   ```

### Run Tests

```bash
# Run all UI tests
uv run pytest tests/ui/ -m ui -v

# Run specific test file
uv run pytest tests/ui/test_auth_ui.py -v

# Run in headless mode
HEADLESS=true uv run pytest tests/ui/ -m ui -v

# With Allure report
uv run pytest tests/ui/ -m ui --alluredir=allure-results
allure serve allure-results
```

## 📝 Configuration

### Environment Variables

- `FRONTEND_URL` - Frontend URL (default: `http://localhost:5000`)
- `HEADLESS` - Run in headless mode (default: `false`)

```bash
export FRONTEND_URL="http://localhost:5000"
export HEADLESS="true"
uv run pytest tests/ui/ -m ui -v
```

### Browser Configuration

Edit `conftest.py` to customize:
- Browser type (chromium/firefox/webkit)
- Viewport size
- Slow motion speed
- Screenshot settings

## 🎯 Test Structure

```
tests/ui/
├── conftest.py           # Playwright fixtures and configuration
├── test_auth_ui.py       # Authentication UI tests
├── test_tasks_ui.py      # Task management UI tests
├── test_playwright.py    # Sample tests
└── README.md             # This file
```

## 🔍 Test Features

### Allure Integration
- Detailed step-by-step execution
- Screenshots on failure
- Test categorization by feature/story
- Severity levels

### Automatic Screenshots
- Captured on test failure
- Full page screenshots
- Attached to Allure report

### Helper Functions
- `register_and_login()` - Quick user setup
- `login_user()` - Login existing user

## 📸 Screenshots

Screenshots are automatically taken on test failure and saved to `screenshots/` directory.

## 🐛 Troubleshooting

### Frontend Not Running

**Error:** `page.goto: net::ERR_CONNECTION_REFUSED`

**Fix:**
```bash
docker compose up -d
# Verify frontend is running
curl http://localhost:5000
```

### Playwright Not Installed

**Error:** `Executable doesn't exist`

**Fix:**
```bash
uv run playwright install chromium
```

### Tests Timeout

**Issue:** Tests hang or timeout

**Fix:**
- Increase timeout in tests
- Check if frontend/backend are responsive
- Run in headed mode to see what's happening:
  ```bash
  HEADLESS=false uv run pytest tests/ui/test_auth_ui.py::TestUserLogin::test_login_success -v
  ```

### Modal Not Found

**Issue:** Modal elements not visible

**Fix:**
- Add `page.wait_for_timeout(1000)` after actions
- Check if modal ID matches in template
- Verify JavaScript is loaded

## 💡 Writing New Tests

### Basic Test Structure

```python
import allure
from playwright.sync_api import Page, expect

@allure.feature("Feature Name")
@allure.story("User Story")
class TestMyFeature:
    
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Test title")
    @allure.description("Test description")
    @pytest.mark.ui
    def test_my_feature(self, page: Page):
        """Test docstring."""
        with allure.step("Step 1"):
            page.goto("http://localhost:5000")
            
        with allure.step("Step 2"):
            expect(page).to_have_title("Expected Title")
```

### Best Practices

1. **Use Allure steps** - Break tests into logical steps
2. **Use helper functions** - Reuse common operations
3. **Add waits** - Use `page.wait_for_*()` for dynamic content
4. **Unique test data** - Use timestamps for unique identifiers
5. **Clean assertions** - Use Playwright's `expect()` API
6. **Screenshots** - Automatic on failure, manual with `page.screenshot()`

## 🚦 Running in CI/CD

### GitHub Actions Example

```yaml
- name: Install Playwright
  run: uv run playwright install chromium --with-deps

- name: Start Services
  run: docker compose up -d

- name: Wait for Frontend
  run: timeout 30 bash -c 'until curl -f http://localhost:5000; do sleep 1; done'

- name: Run UI Tests
  run: |
    export HEADLESS=true
    uv run pytest tests/ui/ -m ui --alluredir=allure-results

- name: Upload Screenshots
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: screenshots
    path: screenshots/
```

## 📊 Test Execution

### Typical Output

```
tests/ui/test_auth_ui.py::TestUserRegistration::test_register_new_user PASSED [ 5%]
tests/ui/test_auth_ui.py::TestUserLogin::test_login_success PASSED           [10%]
tests/ui/test_tasks_ui.py::TestTaskCreation::test_create_task PASSED         [15%]
...
=================== 19 passed in 45.23s ===================
```

### Performance

- **Execution Time**: ~45 seconds for all tests
- **Per Test**: ~2-3 seconds average
- **Headless**: Faster execution
- **Headed**: Better for debugging

## 🔗 Related Documentation

- [Playwright Documentation](https://playwright.dev/python/)
- [Allure Documentation](https://docs.qameta.io/allure/)
- [Frontend Tests](../../frontend/tests/README.md)
- [API Tests](../api/README.md)

## 📈 Next Steps

### Potential Enhancements

1. **Visual regression testing** - Screenshot comparison
2. **Mobile viewport testing** - Test responsive design
3. **Cross-browser testing** - Firefox, WebKit
4. **Performance testing** - Page load times
5. **Accessibility testing** - ARIA labels, keyboard navigation
6. **API mocking** - Test frontend in isolation

## 🎓 Tips

- **Debug mode**: Run with `HEADLESS=false` to see browser
- **Slow motion**: Increase `slow_mo` in conftest.py
- **Pause test**: Use `page.pause()` to inspect state
- **Console logs**: Check browser console with `page.on("console", ...)`
- **Network**: Monitor requests with `page.on("request", ...)`

## Summary

- **19 UI tests** covering authentication and task management
- **Playwright** for browser automation
- **Allure** for detailed reporting
- **Automatic screenshots** on failure
- **CI/CD ready** with headless mode
- **Easy to extend** with helper functions

Run tests: `uv run pytest tests/ui/ -m ui -v` 🚀
