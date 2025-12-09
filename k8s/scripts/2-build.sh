#!/bin/bash
set -e

echo "========================================="
echo "QA Lab - Build Docker Images"
echo "========================================="
echo ""

# Configure Docker to use Minikube's Docker daemon
echo "1. Configuring Docker environment..."
eval $(minikube docker-env)

# Build Docker images inside Minikube
echo ""
echo "2. Building Docker images..."
echo "   Building backend image..."
docker build -t qa-lab-backend:latest ./backend

echo "   Building frontend image..."
docker build -t qa-lab-frontend:latest ./frontend

echo ""
echo "========================================="
echo "Build completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Apply config:  ./k8s/scripts/3-apply.sh"
echo "  2. Expose ports:  ./k8s/scripts/4-expose.sh"
echo "  3. Redeploy if already running:   ./k8s/scripts/5-redeploy.sh"
echo ""
echo "Or run everything at once:"
echo "  ./k8s/scripts/0-quick-start.sh"
echo ""
