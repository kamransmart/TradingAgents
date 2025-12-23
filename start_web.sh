#!/bin/bash

# Start script for TradingAgents Web Interface

echo "🤖 Starting TradingAgents Web Interface..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your API keys."
        echo ""
        read -p "Press Enter after you've added your API keys to .env..."
    else
        echo "❌ Error: .env.example not found!"
        exit 1
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created!"
    echo ""
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if chainlit is installed in venv
if ! command -v chainlit &> /dev/null; then
    echo "📦 Chainlit not found. Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dependencies installed!"
    echo ""
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p results
mkdir -p dataflows/data_cache
echo "✅ Directories created!"
echo ""

# Start the app
echo "🚀 Launching Chainlit web interface..."
echo "📍 Access the app at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

chainlit run chainlit_app.py --host 0.0.0.0 --port 8000
