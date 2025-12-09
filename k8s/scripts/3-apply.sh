#!/bin/bash
set -e

echo "========================================="
echo "QA Lab - Local Deployment Script"
echo "========================================="
echo ""

# Deploy using Kustomize
echo "1. Deploying application using Kustomize..."
kubectl apply -k k8s/overlays/local

# Wait for database to be ready
echo ""
echo "2. Waiting for database to be ready..."
kubectl wait --for=condition=ready pod -l app=db -n local --timeout=120s

# Wait for backend to be ready
echo ""
echo "3. Waiting for backend to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n local --timeout=120s

# Wait for frontend to be ready
echo ""
echo "4. Waiting for frontend to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend -n local --timeout=120s

# Show deployment status
echo ""
echo "========================================="
echo "Deployment completed successfully!"
echo "========================================="
echo ""
echo "Deployment status:"
kubectl get all -n local

echo ""
echo "Next steps:"
echo "  1. Expose ports:  ./k8s/scripts/4-expose.sh"
echo ""
echo "Or run everything at once:"
echo "  ./k8s/scripts/0-quick-start.sh"
echo ""
echo "Useful commands:"
echo "  - Redeploy:  ./k8s/scripts/5-redeploy.sh"
echo "  - Status:    ./k8s/scripts/6-status.sh"
echo "  - Logs:      ./k8s/scripts/7-logs.sh"
echo "  - Cleanup:   ./k8s/scripts/9-cleanup.sh"
echo ""
