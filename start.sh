#!/bin/bash
# Startup script for Railway deployment
# This ensures PORT is properly set as a number

# Get PORT from Railway (defaults to 8000 if not set)
export PORT=${PORT:-8000}

# Unset any existing CHAINLIT_PORT that might contain "$PORT" string
unset CHAINLIT_PORT

# Set CHAINLIT_PORT to the actual PORT number
export CHAINLIT_PORT=$PORT

# Debug: print what we're setting
echo "PORT=$PORT"
echo "CHAINLIT_PORT=$CHAINLIT_PORT"

# Start Chainlit with viewer app
exec chainlit run chainlit_app_with_viewer.py --host 0.0.0.0 --port $PORT
