#!/bin/bash

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! pg_isready -h db -p 5432 -U postgres; do
  sleep 1
done

echo "Database is ready!"

# Initialize database with admin user
echo "Initializing database..."
uv run app/init_db.py

# Start the FastAPI application
echo "Starting FastAPI application..."
uv run granian --interface asgi app.main:app --host 0.0.0.0 --port 8000
