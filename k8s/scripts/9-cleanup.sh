#!/bin/bash
set -e

echo "========================================="
echo "QA Lab - Cleanup Script"
echo "========================================="
echo ""

echo "This will delete all resources in the local namespace."
read -p "Are you sure? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""
echo "Deleting all resources..."
kubectl delete namespace local

# Clean up local secrets file
if [ -f "k8s/overlays/local/secrets.yml" ]; then
    echo "Removing local secrets file..."
    rm k8s/overlays/local/secrets.yml
fi

echo ""
echo "Cleanup completed!"
echo ""
echo "To completely stop Minikube:"
echo "  minikube stop"
echo ""
echo "To delete Minikube cluster:"
echo "  minikube delete"
echo ""

exit 0
