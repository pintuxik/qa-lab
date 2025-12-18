#!/bin/bash
#
# Script to run all integration tests (API + UI)
# Skips unit tests - only runs integration tests against running services
#
# Usage: ./run_integration_tests.sh [options]
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:5001}"
SKIP_CHECK=false
VERBOSE=""
ALLURE_REPORT=false

# Track test results
API_PASSED=0
UI_PASSED=0

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

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Run all integration tests (API + UI) - skips unit tests

OPTIONS:
    -h, --help              Show this help message
    -s, --skip-check        Skip service health checks
    -v, --verbose           Run tests in verbose mode
    -a, --allure            Generate Allure reports
    --api-only              Run only API tests
    --ui-only               Run only UI tests
    --api-url URL           API base URL (default: http://localhost:8000)
    --frontend-url URL      Frontend URL (default: http://localhost:5001)

EXAMPLES:
    # Run all integration tests
    $0

    # Run with verbose output
    $0 -v

    # Run only API tests
    $0 --api-only

    # Run only UI tests
    $0 --ui-only

    # Skip health checks (useful in CI)
    $0 --skip-check

EOF
    exit 0
}

# Parse command line arguments
API_ONLY=false
UI_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -s|--skip-check)
            SKIP_CHECK=true
            shift
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -a|--allure)
            ALLURE_REPORT=true
            shift
            ;;
        --api-only)
            API_ONLY=true
            shift
            ;;
        --ui-only)
            UI_ONLY=true
            shift
            ;;
        --api-url)
            API_BASE_URL="$2"
            shift 2
            ;;
        --frontend-url)
            FRONTEND_URL="$2"
            shift 2
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Build options to pass to sub-scripts
PASS_OPTS=""
if [ "$SKIP_CHECK" = true ]; then
    PASS_OPTS="$PASS_OPTS --skip-check"
fi
if [ -n "$VERBOSE" ]; then
    PASS_OPTS="$PASS_OPTS -v"
fi
if [ "$ALLURE_REPORT" = true ]; then
    PASS_OPTS="$PASS_OPTS --allure"
fi

# Main execution
echo ""
echo -e "${BLUE}=== Integration Tests ===${NC}"
echo -e "${BLUE}=========================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run API Integration Tests
if [ "$UI_ONLY" = false ]; then
    echo -e "${BLUE}[1/2] Running API Integration Tests...${NC}"
    echo "----------------------------------------"

    export API_BASE_URL
    if "${SCRIPT_DIR}/run_api_tests.sh" $PASS_OPTS; then
        print_info "API integration tests passed!"
        API_PASSED=1
    else
        print_error "API integration tests failed!"
    fi
    echo ""
fi

# Run UI Integration Tests
if [ "$API_ONLY" = false ]; then
    echo -e "${BLUE}[2/2] Running UI Integration Tests...${NC}"
    echo "--------------------------------------"

    export FRONTEND_URL
    if "${SCRIPT_DIR}/run_ui_tests.sh" $PASS_OPTS; then
        print_info "UI integration tests passed!"
        UI_PASSED=1
    else
        print_error "UI integration tests failed!"
    fi
    echo ""
fi

# Summary
echo ""
echo -e "${BLUE}=========================${NC}"
echo -e "${BLUE}  Test Results Summary${NC}"
echo -e "${BLUE}=========================${NC}"

if [ "$UI_ONLY" = false ]; then
    echo -e "API Integration Tests:  $([ $API_PASSED -eq 1 ] && echo -e "${GREEN}PASSED${NC}" || echo -e "${RED}FAILED${NC}")"
fi
if [ "$API_ONLY" = false ]; then
    echo -e "UI Integration Tests:   $([ $UI_PASSED -eq 1 ] && echo -e "${GREEN}PASSED${NC}" || echo -e "${RED}FAILED${NC}")"
fi
echo ""

# Determine exit code
if [ "$API_ONLY" = true ]; then
    [ $API_PASSED -eq 1 ] && exit 0 || exit 1
elif [ "$UI_ONLY" = true ]; then
    [ $UI_PASSED -eq 1 ] && exit 0 || exit 1
else
    [ $API_PASSED -eq 1 ] && [ $UI_PASSED -eq 1 ] && exit 0 || exit 1
fi
