#!/bin/bash

# Start MuseTalk Avatar App locally

echo "🚀 Starting MuseTalk Avatar App..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup_local.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if required directories exist
if [ ! -d "musetalk/models/dwpose" ]; then
    echo "❌ Models not found. Please run ./setup_local.sh first"
    exit 1
fi

echo "🌐 Starting server on http://localhost:8080"
echo "📱 You can also access it via your public IP on port 8080"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI application
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload