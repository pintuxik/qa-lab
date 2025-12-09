#!/bin/bash

# Usage: ./7-logs.sh [backend|frontend|db] (default: all)
SERVICE=${1:-all}

echo "========================================="
echo "QA Lab - Logs"
echo "========================================="
echo ""

case $SERVICE in
  backend)
    echo "Tailing backend logs... (Ctrl+C to stop)"
    kubectl logs -f deployment/backend -n local
    ;;
  frontend)
    echo "Tailing frontend logs... (Ctrl+C to stop)"
    kubectl logs -f deployment/frontend -n local
    ;;
  db)
    echo "Tailing database logs... (Ctrl+C to stop)"
    kubectl logs -f deployment/db -n local
    ;;
  all|*)
    echo "Tailing all logs... (Ctrl+C to stop)"
    echo "Usage: ./7-logs.sh [backend|frontend|db] for specific service"
    echo ""
    kubectl logs -f -l app -n local --max-log-requests=30
    ;;
esac
