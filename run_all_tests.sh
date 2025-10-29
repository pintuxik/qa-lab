#!/bin/bash

# Script to run all tests for QA Lab project

set -e

echo "🧪 QA Lab - Running All Tests"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Backend Tests
echo -e "${BLUE}📦 Running Backend Tests...${NC}"
echo "----------------------------"
cd backend
if uv sync --extra test > /dev/null 2>&1; then
    if uv run pytest -v; then
        echo -e "${GREEN}✅ Backend tests passed!${NC}"
    else
        echo -e "${RED}❌ Backend tests failed!${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Failed to install backend test dependencies${NC}"
    exit 1
fi
cd ..
echo ""

# Frontend Tests
echo -e "${BLUE}🎨 Running Frontend Tests...${NC}"
echo "----------------------------"
cd frontend
if uv sync --extra test > /dev/null 2>&1; then
    if uv run pytest -v; then
        echo -e "${GREEN}✅ Frontend tests passed!${NC}"
    else
        echo -e "${RED}❌ Frontend tests failed!${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Failed to install frontend test dependencies${NC}"
    exit 1
fi
cd ..
echo ""

# Summary
echo "=============================="
echo -e "${GREEN}🎉 All tests passed successfully!${NC}"
echo ""
echo "To view coverage reports:"
echo "  Backend:  open backend/htmlcov/index.html"
echo "  Frontend: open frontend/htmlcov/index.html"
echo ""
echo "To run integration tests:"
echo "  python tests/test_api.py"
