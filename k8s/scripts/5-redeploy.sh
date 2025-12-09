#!/bin/bash
set -e

echo "========================================="
echo "QA Lab - Redeploy (Build + Restart)"
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

# Restart deployments
echo ""
echo "3. Restarting deployments..."
echo "   Restarting backend..."
kubectl rollout restart deployment/backend -n local

echo "   Restarting frontend..."
kubectl rollout restart deployment/frontend -n local

# Wait for pods to be ready
echo ""
echo "4. Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n local --timeout=120s
kubectl wait --for=condition=ready pod -l app=frontend -n local --timeout=120s

echo ""
echo "========================================="
echo "Redeploy completed successfully!"
echo "========================================="
echo ""
echo "Useful commands:"
echo "  - Status:    ./k8s/scripts/6-status.sh"
echo "  - Logs:      ./k8s/scripts/7-logs.sh"
echo "  - Cleanup:   ./k8s/scripts/9-cleanup.sh"
echo ""
