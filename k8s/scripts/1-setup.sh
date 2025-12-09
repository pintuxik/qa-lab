#!/bin/bash
set -e

echo "========================================="
echo "QA Lab - Minikube Setup Script"
echo "========================================="
echo ""

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "Error: minikube is not installed"
    echo "Install from: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed"
    echo "Install from: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if kustomize is installed (optional, kubectl has built-in support)
if ! command -v kustomize &> /dev/null; then
    echo "Note: kustomize standalone not found, using kubectl's built-in kustomize"
fi

# Start Minikube if not running
echo "1. Checking Minikube status..."
if minikube status &> /dev/null; then
    echo "   Minikube is already running"
else
    echo "   Starting Minikube..."
    minikube start --cpus=8 --memory=4096 --driver=docker
fi

# Configure Docker to use Minikube's Docker daemon
echo ""
echo "2. Configuring Docker environment..."
eval $(minikube docker-env)

# Create secrets
echo ""
echo "3. Setting up secrets..."
cd k8s/overlays/local

if [ ! -f "secrets.yml" ]; then
    echo "   Creating secrets from template..."
    cat > secrets.yml <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: qa-lab-secrets
type: Opaque
stringData:
  # Database credentials (will be base64 encoded automatically)
  DB_USER: "postgres"
  DB_PASSWORD: "password"
  # Application secrets
  SECRET_KEY: "local-dev-secret-key-do-not-use-in-production"
  FLASK_SECRET_KEY: "local-dev-flask-secret-do-not-use-in-production"
EOF

    echo "   secrets.yml created"
else
    echo "   Using existing secrets.yml"
fi

cd ../../..

echo ""
echo "========================================="
echo "Setup completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Build images:  ./k8s/scripts/2-build.sh"
echo "  2. Apply config:  ./k8s/scripts/3-apply.sh"
echo "  3. Expose ports:  ./k8s/scripts/4-expose.sh"
echo ""
echo "Or run everything at once:"
echo "  ./k8s/scripts/0-quick-start.sh"
echo ""
