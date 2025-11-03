#!/bin/bash

# Start the Flask application
echo "Starting Flask application..."
uv run granian --interface wsgi app.main:app --backpressure $(nproc) --host 0.0.0.0 --port 5000 