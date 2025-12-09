#!/bin/bash
# ============================================================================
# QA Lab Environment Setup Script
# ============================================================================
# Creates required .env files for container-first development.
# Safe to run multiple times - will not overwrite existing files.
#
# Usage: ./setup-env.sh
#
# Philosophy: All services run in Docker containers. No local installation
# of PostgreSQL or service-specific configuration needed.
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Setting up environment files for QA Lab..."
echo ""

# Track what we created
CREATED=0
SKIPPED=0

# ----------------------------------------------------------------------------
# Root .env (docker-compose) - Required for running services
# ----------------------------------------------------------------------------
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[+] Created .env (docker-compose config)"
    CREATED=$((CREATED + 1))
else
    echo "[-] Skipped .env (already exists)"
    SKIPPED=$((SKIPPED + 1))
fi

# ----------------------------------------------------------------------------
# Tests .env.test (integration tests) - Required for API/UI tests
# ----------------------------------------------------------------------------
if [ ! -f tests/.env.test ]; then
    cp tests/.env.test.example tests/.env.test
    echo "[+] Created tests/.env.test"
    CREATED=$((CREATED + 1))
else
    echo "[-] Skipped .env (already exists)"
    SKIPPED=$((SKIPPED + 1))
fi

# ----------------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------------
echo ""
echo "============================================"
echo "Setup complete!"
echo "  Created: $CREATED file(s)"
echo "  Skipped: $SKIPPED file(s) (already existed)"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Start services:     docker-compose up --build"
echo "  2. Run unit tests:     cd backend && uv run pytest -n auto"
echo "  3. Run API tests:      ./run_api_tests.sh"
echo "  4. Run UI tests:       ./run_ui_tests.sh"
echo ""
echo "Note: All services run in Docker containers."
echo "      No local PostgreSQL or service config needed."
echo ""
