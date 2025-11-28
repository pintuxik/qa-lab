# UI Integration Tests

Comprehensive UI integration tests for the Task Management application using Playwright and Allure reporting.

## Summary

- **19 UI tests** covering authentication and task management
- **Playwright** for browser automation
- **Allure** for detailed reporting
- **Automatic screenshots** on failure
- **CI/CD ready** with headless mode
- **Easy to extend** with helper functions

## 🚀 Quick Start

### Prerequisites

1. **Frontend and Backend running**
   ```bash
   docker compose up -d
   ```

2. **Install Playwright browsers** (first time only)
   ```bash
   uv run playwright install chromium
   ```

### Run Tests

```bash
# Run all UI tests
./run_ui_tests.sh

# Or with pytest directly
uv run pytest ui/ -m ui -v

# Run specific test file
uv run pytest ui/test_auth_ui.py -v

# Run in headed mode
HEADLESS=false uv run pytest tests/ui/ -m ui -v

# Run in parallel
uv run -n auto

# With Allure report
uv run pytest tests/ui/ -m ui --alluredir=allure-results
allure serve allure-results
```

## 📝 Configuration

### Environment Variables

- `FRONTEND_URL` - Frontend URL (default: `http://localhost:5001`)
- `HEADLESS` - Run in headless mode (default: `false`)

```bash
export FRONTEND_URL="http://localhost:5001"
export HEADLESS="true"
uv run pytest tests/ui/ -m ui -v
```

### Browser Configuration

Edit `conftest.py` to customize:
- Browser type (chromium/firefox/webkit)
- Viewport size
- Slow motion speed
- Screenshot settings

## 📸 Screenshots

Screenshots are automatically taken on test failure and saved to `screenshots/` directory.

## 🐛 Troubleshooting

### Frontend Not Running

**Error:** `page.goto: net::ERR_CONNECTION_REFUSED`

**Fix:**
```bash
docker compose up -d
# Verify frontend is running
curl http://localhost:5001
```

### Playwright Not Installed

**Error:** `Executable doesn't exist`

**Fix:**
```bash
uv run playwright install
```

### Tests Timeout

**Issue:** Tests hang or timeout

**Fix:**
- Check if frontend/backend are responsive
- Run in headed mode to see what's happening:
  ```bash
  HEADLESS=false uv run pytest ui/test_auth_ui.py::TestUserLogin::test_login_success -v
  ```

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
            page.goto("http://localhost:5001")
            
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

## 🔗 Related Documentation

- [Playwright Documentation](https://playwright.dev/python/)
- [Allure Documentation](https://docs.qameta.io/allure/)

## 🎓 Tips

- **Debug mode**: Run with `HEADLESS=false` to see browser
- **Slow motion**: Increase `slow_mo` in conftest.py
- **Pause test**: Use `page.pause()` to inspect state
- **Console logs**: Check browser console with `page.on("console", ...)`
- **Network**: Monitor requests with `page.on("request", ...)`
