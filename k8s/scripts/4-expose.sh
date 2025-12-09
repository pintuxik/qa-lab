#!/bin/bash
set -e

echo "========================================="
echo "QA Lab - Port Forwarding Setup"
echo "========================================="
echo ""

# Get Minikube IP
MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "127.0.0.1")

echo "Setting up port forwarding for integration tests..."
echo ""
echo "Minikube IP: $MINIKUBE_IP"
echo ""

# Check if services are running
if ! kubectl get service backend -n local &> /dev/null; then
    echo "Error: Backend service not found. Please run ./k8s/scripts/local-deploy.sh first"
    exit 1
fi

echo "Services are exposed via NodePort:"
echo "  Backend:  http://$MINIKUBE_IP:30800"
echo "  Frontend: http://$MINIKUBE_IP:30501"
echo ""
echo "For localhost access, run in separate terminals:"
echo "  kubectl port-forward -n local service/backend 8000:8000"
echo "  kubectl port-forward -n local service/frontend 5001:5001"
echo ""
echo "Or use this script to set up port forwarding in the background:"
echo ""

# Offer to set up port forwarding
read -p "Set up port forwarding now? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Kill any existing port-forward processes
    pkill -f "port-forward.*local.*backend" 2>/dev/null || true
    pkill -f "port-forward.*local.*frontend" 2>/dev/null || true

    echo "Starting port forwarding..."
    kubectl port-forward -n local service/backend 8000:8000 > /dev/null 2>&1 &
    BACKEND_PID=$!

    kubectl port-forward -n local service/frontend 5001:5001 > /dev/null 2>&1 &
    FRONTEND_PID=$!

    sleep 2

    echo ""
    echo "Port forwarding active:"
    echo "  Backend:  http://localhost:8000 (PID: $BACKEND_PID)"
    echo "  Frontend: http://localhost:5001 (PID: $FRONTEND_PID)"
    echo ""
    echo "To stop port forwarding:"
    echo "  kill $BACKEND_PID $FRONTEND_PID"
    echo ""
    echo "Or run: pkill -f 'port-forward.*local'"
    echo ""

    # Save PIDs to a file
    echo "$BACKEND_PID" > /tmp/qa-lab-backend-pf.pid
    echo "$FRONTEND_PID" > /tmp/qa-lab-frontend-pf.pid

    echo "PIDs saved to /tmp/qa-lab-*-pf.pid"

    echo ""
    echo "Ready for integration tests!"
fi

echo "Useful commands:"
echo "  - Redeploy:  ./k8s/scripts/5-redeploy.sh"
echo "  - Status:    ./k8s/scripts/6-status.sh"
echo "  - Logs:      ./k8s/scripts/7-logs.sh"
echo "  - Cleanup:   ./k8s/scripts/9-cleanup.sh"
echo ""
