#!/bin/bash
#
# Script to run UI integration tests
# Usage: ./run_ui_tests.sh [options]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
FRONTEND_URL="${FRONTEND_URL:-http://localhost:5001}"
HEADLESS="${HEADLESS:-true}"
ALLURE_REPORT="${ALLURE_REPORT:-false}"
TEST_PATTERN="${TEST_PATTERN:-ui/}"
BROWSER="${BROWSER:-chromium}"

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if frontend is running
check_frontend() {
    print_info "Checking if frontend is running at ${FRONTEND_URL}..."
    
    if curl -sf "${FRONTEND_URL}" > /dev/null 2>&1; then
        print_info "Frontend is running ✓"
        return 0
    else
        print_warning "Frontend is not accessible at ${FRONTEND_URL}"
        print_warning "Make sure the frontend is running before running UI tests"
        echo ""
        print_info "To start services:"
        print_info "  docker compose up -d"
        echo ""
        return 1
    fi
}

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Run UI integration tests with Playwright

OPTIONS:
    -h, --help              Show this help message
    -u, --url URL           Frontend URL (default: http://localhost:5001)
    -a, --allure            Generate Allure report after tests
    -t, --test PATTERN      Test pattern to run (default: ui/)
    -b, --browser BROWSER   Browser to use (chromium/firefox/webkit, default: chromium)
    --headless              Run in headless mode (default)
    --headed                Run in headed mode
    -s, --skip-check        Skip frontend availability check
    -v, --verbose           Run tests in verbose mode

EXAMPLES:
    # Run all UI tests
    $0

    # Run in headed mode
    $0 --headed

    # Run specific test file
    $0 --test ui/test_auth_ui.py

    # Run with Allure report
    $0 --allure

    # Run with custom frontend URL
    $0 --url http://frontend.example.com:5001

EOF
    exit 0
}

# Parse command line arguments
SKIP_CHECK=false
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -u|--url)
            FRONTEND_URL="$2"
            shift 2
            ;;
        -a|--allure)
            ALLURE_REPORT=true
            shift
            ;;
        -t|--test)
            TEST_PATTERN="$2"
            shift 2
            ;;
        -b|--browser)
            BROWSER="$2"
            shift 2
            ;;
        --headless)
            HEADLESS=true
            shift
            ;;
        --headed)
            HEADLESS=false
            shift
            ;;
        -s|--skip-check)
            SKIP_CHECK=true
            shift
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Detecting platform
if [ "$(uname)" == "Darwin" ]; then
    PLATFORM="Darwin"
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    PLATFORM="Linux"
else
    PLATFORM=""
fi
# Check if Playwright browsers are already installed to avoid triggering Docker reload
case "$PLATFORM" in
    "Darwin")
        PLAYWRIGHT_BROWSERS_PATH="$HOME/Library/Caches/ms-playwright" ;;
    "Linux")
        PLAYWRIGHT_BROWSERS_PATH="$HOME/.cache/ms-playwright" ;;
    *)
        PLAYWRIGHT_BROWSERS_PATH="" ;;
esac

if [ ! -d "$PLAYWRIGHT_BROWSERS_PATH" ] 2>/dev/null ; then
    echo "Installing Playwright browsers..."
    if uv run playwright install chromium --with-deps; then
        echo -e "${GREEN}✓ Playwright browsers installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Failed to install Playwright browsers${NC}"
    fi
else
    echo -e "${GREEN}✓ Playwright browsers already installed${NC}"
fi

# Main execution
print_info "=== UI Integration Tests ==="
print_info "Frontend URL: ${FRONTEND_URL}"
print_info "Test Pattern: ${TEST_PATTERN}"
print_info "Browser: ${BROWSER}"
print_info "Headless: ${HEADLESS}"


# Check if frontend is running (unless skipped)
if [ "$SKIP_CHECK" = false ]; then
    if ! check_frontend; then
        print_error "Frontend check failed. Use --skip-check to bypass this check."
        exit 1
    fi
fi

# Export environment variables
export FRONTEND_URL
export HEADLESS

# Build pytest command
PYTEST_CMD="uv run pytest ${TEST_PATTERN} -m ui ${VERBOSE}"

# Adjust number of threads for pytest for UI tests
case "$PLATFORM" in
    "Darwin")
        NPROC_ADJUSTED=$(sysctl -n hw.physicalcpu) ;; # macOS physical cores
    "Linux")
        NPROC_ADJUSTED=$(($(nproc)/2)) ;; # Linux half of total cores
    *)
        NPROC_ADJUSTED="1" ;; # Other OS fallback
esac

export PYTEST_ADDOPTS="-n$NPROC_ADJUSTED"

if [ "$ALLURE_REPORT" = true ]; then
    print_info "Allure reporting enabled"
    PYTEST_CMD="${PYTEST_CMD} --alluredir=allure-results"
fi

# Run tests
print_info "Running UI tests..."
print_info "Command: ${PYTEST_CMD}"
echo ""

if eval "${PYTEST_CMD}"; then
    print_info "Tests completed successfully ✓"
    EXIT_CODE=0
else
    print_error "Tests failed ✗"
    EXIT_CODE=1
fi

# Generate Allure report if requested
if [ "$ALLURE_REPORT" = true ] && [ -d "allure-results" ]; then
    print_info "Generating Allure report..."
    
    if command -v allure &> /dev/null; then
        allure generate allure-results -o allure-report --clean
        print_info "Allure report generated in allure-report/"
        print_info "To view report: allure open allure-report"
    else
        print_warning "Allure command not found. Install with: pip install allure-pytest"
        print_info "You can still view results with: allure serve allure-results"
    fi
fi

# Show screenshots location if tests failed
if [ $EXIT_CODE -ne 0 ] && [ -d "screenshots" ]; then
    echo ""
    print_info "Screenshots saved in: screenshots/"
fi

exit $EXIT_CODE
