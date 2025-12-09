#!/bin/bash

echo "========================================="
echo "QA Lab - Status"
echo "========================================="
echo ""

echo "=== Pods ==="
kubectl get pods -n local
echo ""

echo "=== Services ==="
kubectl get svc -n local
echo ""

echo "=== Recent Events ==="
kubectl get events -n local --sort-by='.lastTimestamp' | tail -10
echo ""
