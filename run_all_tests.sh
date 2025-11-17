#!/bin/bash

# Script to run all tests for QA Lab project

echo "🧪 QA Lab - Running All Tests"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to clean broken venv
clean_venv() {
    local dir=$1
    if [ -d "$dir/.venv" ] && [ ! -f "$dir/.venv/bin/python" ]; then
        echo -e "${YELLOW}⚠️  Cleaning broken virtual environment in $dir...${NC}"
        # Try to make it writable first
        chmod -R u+w "$dir/.venv" 2>/dev/null || true
        # Remove it
        rm -rf "$dir/.venv" 2>/dev/null || {
            echo -e "${YELLOW}⚠️  Could not remove .venv, trying with sudo...${NC}"
            sudo rm -rf "$dir/.venv" 2>/dev/null || {
                echo -e "${RED}❌ Failed to remove broken venv. Please run: sudo rm -rf $dir/.venv${NC}"
                return 1
            }
        }
        echo -e "${GREEN}✓ Cleaned up broken venv${NC}"
    fi
    return 0
}

# Clean up any broken virtual environments first
echo "Checking for broken virtual environments..."
clean_venv "backend"
clean_venv "frontend"
echo ""

# Track test results
BACKEND_PASSED=0
FRONTEND_PASSED=0
API_PASSED=0
UI_PASSED=0

# Adjust number of threads for pytest
export PYTEST_ADDOPTS="-n auto"

# Backend Tests
echo -e "${BLUE}📦 Running Backend Tests...${NC}"
echo "----------------------------"
cd backend

# Sync dependencies
echo "Installing dependencies..."
if uv sync --group test > /dev/null 2>&1 || uv sync --group test; then
    echo "Running tests..."
    if uv run pytest -v; then
        echo -e "${GREEN}✅ Backend tests passed!${NC}"
        BACKEND_PASSED=1
    else
        echo -e "${RED}❌ Backend tests failed!${NC}"
    fi
else
    echo -e "${RED}❌ Failed to install backend test dependencies${NC}"
fi
cd ..
echo ""

# Frontend Tests
echo -e "${BLUE}🎨 Running Frontend Tests...${NC}"
echo "----------------------------"
cd frontend

# Sync dependencies
echo "Installing dependencies..."
if uv sync --group test > /dev/null 2>&1 || uv sync --group test; then
    echo "Running tests..."
    if uv run pytest -v; then
        echo -e "${GREEN}✅ Frontend tests passed!${NC}"
        FRONTEND_PASSED=1
    else
        echo -e "${RED}❌ Frontend tests failed!${NC}"
    fi
else
    echo -e "${RED}❌ Failed to install frontend test dependencies${NC}"
fi
cd ..
echo ""

# API Integration Tests
echo -e "${BLUE}🔌 Running API Integration Tests...${NC}"
echo "----------------------------"
if ./run_api_tests.sh --skip-check; then
    echo -e "${GREEN}✅ API integration tests passed!${NC}"
    API_PASSED=1
else
    echo -e "${YELLOW}⚠️  API integration tests skipped or failed${NC}"
    echo -e "${YELLOW}    (Make sure backend is running: ./setup_backend_for_tests.sh)${NC}"
fi
echo ""

# UI Integration Tests
echo -e "${BLUE}🎭 Running UI Integration Tests...${NC}"
echo "----------------------------"
if ./run_ui_tests.sh --skip-check; then # TODO: add --headless after demo period
    echo -e "${GREEN}✅ UI integration tests passed!${NC}"
    UI_PASSED=1
else
    echo -e "${YELLOW}⚠️  UI integration tests skipped or failed${NC}"
    echo -e "${YELLOW}    (Make sure frontend and backend are running: docker compose up -d)${NC}"
fi
echo ""

# Summary
echo "=============================="
echo "📊 Test Results Summary"
echo "=============================="
echo -e "Backend Unit Tests:     $([ $BACKEND_PASSED -eq 1 ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${RED}❌ FAILED${NC}")"
echo -e "Frontend Unit Tests:    $([ $FRONTEND_PASSED -eq 1 ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${RED}❌ FAILED${NC}")"
echo -e "API Integration Tests:  $([ $API_PASSED -eq 1 ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${YELLOW}⚠️  SKIPPED${NC}")"
echo -e "UI Integration Tests:   $([ $UI_PASSED -eq 1 ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${YELLOW}⚠️  SKIPPED${NC}")"
echo ""

if [ $BACKEND_PASSED -eq 1 ] && [ $FRONTEND_PASSED -eq 1 ]; then
    echo -e "${GREEN}🎉 All unit tests passed successfully!${NC}"
    echo ""
    echo "📁 Coverage reports available at:"
    echo "  Backend:  backend/htmlcov/index.html"
    echo "  Frontend: frontend/htmlcov/index.html"
    echo ""
    if [ $API_PASSED -eq 0 ] || [ $UI_PASSED -eq 0 ]; then
        echo -e "${YELLOW}💡 To run integration tests:${NC}"
        if [ $API_PASSED -eq 0 ]; then
            echo "  ./setup_backend_for_tests.sh  # Start backend for API tests"
            echo "  ./run_api_tests.sh            # Run API tests"
        fi
        if [ $UI_PASSED -eq 0 ]; then
            echo "  docker compose up -d          # Start frontend + backend for UI tests"
            echo "  ./run_ui_tests.sh             # Run UI tests"
        fi
    fi
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    exit 1
fi
