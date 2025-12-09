#!/bin/bash
set -e

echo "========================================="
echo "QA Lab - Quick Start"
echo "========================================="
echo ""
echo "This script will set up and deploy the entire application."
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Step 1/4: Setup Minikube..."
"$SCRIPT_DIR/1-setup.sh"

echo ""
echo "Step 2/4: Build Docker images..."
"$SCRIPT_DIR/2-build.sh"

echo ""
echo "Step 3/4: Apply Kubernetes config..."
"$SCRIPT_DIR/3-apply.sh"

echo ""
echo "Step 4/4: Expose services..."
"$SCRIPT_DIR/4-expose.sh"

echo ""
echo "========================================="
echo "Quick Start completed!"
echo "========================================="
echo ""
