#!/bin/bash

# Tile Shop Demo - Quick Start Script

echo "🏠 Tile Shop Demo - Starting..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Edit it to add Azure OpenAI credentials (optional)."
    fi
fi

# Start the server
echo ""
echo "🚀 Starting backend server on http://localhost:5000"
echo "📱 Open index.html in your browser to use the demo"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 server.py

