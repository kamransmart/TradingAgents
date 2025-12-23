#!/bin/bash
# Startup script for Railway deployment
# This ensures PORT is properly set as a number

# Get PORT from Railway (defaults to 8000 if not set)
export PORT=${PORT:-8000}

# Set CHAINLIT_PORT to the actual PORT number
export CHAINLIT_PORT=$PORT

# Start Chainlit
exec chainlit run chainlit_app_interactive.py --host 0.0.0.0 --port $PORT
