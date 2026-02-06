#!/bin/bash
# Local Development Server
# Runs the API server locally without Docker

echo "🚀 Starting Event Horizon AI - Local Development Mode"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "💡 Copy .env.example to .env and configure your API keys"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Run the server
echo ""
echo "✅ Starting API server on http://127.0.0.1:8001"
echo "📝 Logs will appear below..."
echo "⏹️  Press CTRL+C to stop"
echo ""

python api_server.py
