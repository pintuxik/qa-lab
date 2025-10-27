# QA Lab

A Python testing project with pytest, Playwright web testing, Allure reporting, and modern development tools.

[![GitHub](https://img.shields.io/badge/GitHub-pintuxik%2Fqa--lab-blue?style=flat-square&logo=github)](https://github.com/pintuxik/qa-lab)
[![Python](https://img.shields.io/badge/Python-3.14-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

## Prerequisites

### Install uv (Python package manager)

uv is a fast Python package installer and resolver. Install it using one of these methods:

**Using curl (recommended):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Using pip:**
```bash
pip install uv
```

**Using pipx:**
```bash
pipx install uv
```

**Using homebrew (macOS):**
```bash
brew install uv
```

### Install Allure

Allure is a flexible lightweight multi-language test report tool. Install it using one of these methods:

**Using npm (recommended):**
```bash
npm install -g allure-commandline
```

**Using scoop (Windows):**
```bash
scoop install allure
```

**Using chocolatey (Windows):**
```bash
choco install allure
```

**Manual installation:**
1. Download the latest version from [GitHub releases](https://github.com/allure-framework/allure2/releases)
2. Extract the archive
3. Add the `bin` directory to your PATH

## Project Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pintuxik/qa-lab.git
   cd qa-lab
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Install the project in editable mode:**
   ```bash
   uv pip install -e .
   ```
   This step is crucial for proper import resolution of the `utils` package in tests.

4. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

## Running Tests

**Run tests with pytest:**
```bash
uv run pytest
```

**Run tests with verbose output:**
```bash
uv run pytest -v
```

**Generate Allure reports:**
```bash
uv run pytest --alluredir=allure-results
allure serve allure-results
```

**Generate and open Allure report:**
```bash
uv run pytest --alluredir=allure-results
allure generate allure-results -o allure-report --clean
allure open allure-report
```

**For WSL2 users (if browser doesn't open automatically):**
```bash
# Option 1: Use serve command (recommended)
allure serve allure-results

# Option 2: Generate static report and open manually
allure generate allure-results -o allure-report --clean
# Then open: /path/to/qa-lab/allure-report/index.html in Windows browser
# Or access via: \\wsl$\Ubuntu\path\to\qa-lab\allure-report\index.html
```

**Run specific test suites:**
```bash
# Run all tests
uv run pytest -v

# Run only UI tests (Playwright)
uv run pytest tests/ui/ -v

# Run only API tests
uv run pytest tests/api/ -v

# Run specific test file
uv run pytest tests/ui/test_playwright.py -v

# Run tests with Allure reports
uv run pytest --alluredir=allure-results -v
```

## Development Tools

**Run linting:**
```bash
uv run ruff check
```

**Run formatting:**
```bash
uv run ruff format
```

**Run both linting and formatting:**
```bash
uv run ruff check --fix
uv run ruff format
```

## Troubleshooting

### Import Errors

If you encounter import errors like `ModuleNotFoundError: No module named 'utils'`, ensure you've completed the installation steps:

1. **Reinstall in editable mode:**
   ```bash
   uv pip install -e .
   ```

2. **Verify installation:**
   ```bash
   uv run python -c "from utils.utils import get_screenshot_path; print('Import successful')"
   ```

3. **Check if package is installed:**
   ```bash
   uv pip list | grep qa-lab
   ```

### Browser Issues

- **WSL2 users**: If browsers don't open automatically, use the Allure serve command instead of open
- **Headless mode**: Set `headless: True` in `tests/ui/conftest.py` for CI/CD environments

## Project Structure

```
qa-lab/
├── .gitignore              # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── pyproject.toml         # Project configuration and dependencies
├── README.md              # This file
├── main.py                # Main project file
├── utils/                 # Utility functions package
│   ├── __init__.py        # Package initialization
│   └── utils.py           # Utility functions (screenshot paths, etc.)
├── tests/                 # Test files
│   ├── api/               # API tests
│   │   ├── conftest.py    # API test configuration
│   │   └── test_sample.py  # Sample API tests
│   └── ui/                # UI tests
│       ├── conftest.py    # UI test configuration with Playwright
│       └── test_playwright.py # Playwright web UI tests
├── screenshots/           # Screenshots on test failures
├── allure-results/        # Allure test results
└── allure-report/        # Generated Allure reports
```

## Dependencies

- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **allure-pytest**: Allure reporting integration
- **playwright**: Web browser automation
- **pytest-playwright**: Playwright integration for pytest
- **ruff**: Fast Python linter and formatter
- **pre-commit**: Git hooks framework

## Repository

- **GitHub**: [https://github.com/pintuxik/qa-lab](https://github.com/pintuxik/qa-lab)
- **License**: MIT
- **Issues**: [Report bugs or request features](https://github.com/pintuxik/qa-lab/issues)

## Features

- ✅ Python 3.14 support
- ✅ Async test support
- ✅ Playwright web UI testing with Chrome
- ✅ Screenshot on test failure
- ✅ Allure reporting with rich annotations
- ✅ Automated code formatting and linting
- ✅ Pre-commit hooks for code quality
- ✅ Modern dependency management with uv
- ✅ WSL2 compatibility with browser workarounds
