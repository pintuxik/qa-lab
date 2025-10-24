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

3. **Install pre-commit hooks:**
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

**Run Playwright tests:**
```bash
# Run all tests (including Playwright)
uv run pytest -v

# Run only Playwright tests
uv run pytest tests/test_playwright.py -v

# Run Playwright tests with Allure reports
uv run pytest tests/test_playwright.py --alluredir=allure-results -v
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

## Project Structure

```
qa-lab/
├── .gitignore              # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── conftest.py             # Global pytest configuration with Playwright
├── pytest.ini             # Pytest configuration
├── pyproject.toml         # Project configuration and dependencies
├── README.md              # This file
├── tests/                 # Test files
│   ├── test_sample.py     # Sample tests with Allure annotations
│   └── test_playwright.py # Playwright web UI tests
├── screenshots/           # Screenshots on test failures
├── allure-results/        # Allure test results
├── allure-report/        # Generated Allure reports
└── main.py                # Main project file
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
