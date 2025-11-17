#!/bin/bash

# Determine number of physical processors for Flask backpressure setting
if [ "$(uname)" == "Darwin" ]; then
    NPROC_ADJUSTED=$(sysctl -n hw.physicalcpu) # macOS physical cores           
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    NPROC_ADJUSTED=$(($(nproc)/2)) # Linux half of total cores
else 
    NPROC_ADJUSTED="1" # Other OS fallback
fi 

# Start the Flask application
echo "Starting Flask application..."
uv run granian --interface wsgi app.main:app --backpressure $NPROC_ADJUSTED --host 0.0.0.0 --port 5001 
