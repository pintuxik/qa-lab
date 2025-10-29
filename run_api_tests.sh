#!/bin/bash
#
# Script to run API integration tests
# Usage: ./run_api_tests.sh [options]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
ALLURE_REPORT="${ALLURE_REPORT:-false}"
TEST_PATTERN="${TEST_PATTERN:-tests/api/}"
MARKERS="${MARKERS:-integration}"

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

# Function to check if API is running
check_api() {
    print_info "Checking if API is running at ${API_BASE_URL}..."
    
    if curl -sf "${API_BASE_URL}/health" > /dev/null 2>&1; then
        print_info "API is running and healthy ✓"
        return 0
    else
        print_warning "API health check failed at ${API_BASE_URL}/health"
        print_warning "Backend API is not running!"
        echo ""
        print_info "To start the backend, run one of these commands:"
        print_info "  Option 1 (Docker Compose): docker compose up -d"
        print_info "  Option 2 (Setup Script):   ./setup_backend_for_tests.sh"
        print_info "  Option 3 (Manual):         See tests/api/README.md"
        echo ""
        return 1
    fi
}

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Run API integration tests for the Task Management API

OPTIONS:
    -h, --help              Show this help message
    -u, --url URL           API base URL (default: http://localhost:8000)
    -a, --allure            Generate Allure report after tests
    -t, --test PATTERN      Test pattern to run (default: tests/api/)
    -m, --markers MARKERS   Pytest markers to filter tests (default: integration)
    -s, --skip-check        Skip API health check
    -v, --verbose           Run tests in verbose mode

EXAMPLES:
    # Run all integration tests
    $0

    # Run with custom API URL
    $0 --url http://api.example.com:8000

    # Run specific test file
    $0 --test tests/api/test_auth_api.py

    # Run with Allure report
    $0 --allure

    # Run without health check (useful in CI)
    $0 --skip-check

    # Run all tests (including sample tests)
    $0 --markers ""

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
            API_BASE_URL="$2"
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
        -m|--markers)
            MARKERS="$2"
            shift 2
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

# Main execution
print_info "=== API Integration Tests ==="
print_info "API URL: ${API_BASE_URL}"
print_info "Test Pattern: ${TEST_PATTERN}"
print_info "Markers: ${MARKERS:-none}"

# Check if API is running (unless skipped)
if [ "$SKIP_CHECK" = false ]; then
    if ! check_api; then
        print_error "API health check failed. Use --skip-check to bypass this check."
        exit 1
    fi
fi

# Export API_BASE_URL for tests
export API_BASE_URL

# Build pytest command
PYTEST_CMD="uv run pytest ${TEST_PATTERN} ${VERBOSE}"

if [ -n "$MARKERS" ]; then
    PYTEST_CMD="${PYTEST_CMD} -m ${MARKERS}"
fi

if [ "$ALLURE_REPORT" = true ]; then
    print_info "Allure reporting enabled"
    PYTEST_CMD="${PYTEST_CMD} --alluredir=allure-results"
fi

# Run tests
print_info "Running tests..."
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

exit $EXIT_CODE
