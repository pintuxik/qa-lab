#!/bin/bash

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! pg_isready -h db -p 5432 -U postgres; do
  sleep 1
done

echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
python app/run_migrations.py

# Initialize database with admin user
echo "Creating default admin user..."
python app/init_db.py

# Start the FastAPI application
echo "Starting FastAPI application..."
granian --interface asgi app.main:app --host 0.0.0.0 --port 8000
