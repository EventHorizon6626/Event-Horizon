#!/bin/bash
# Local Development Server
# Runs the unified FastAPI app locally without Docker

echo "Starting Event Horizon AI - Local Development Mode"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Copy .env.example to .env and configure your API keys"
    exit 1
fi

# Load environment
set -a
source .env
set +a

# Default: skip local vLLM when running locally
export SKIP_VLLM="${SKIP_VLLM:-true}"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r event_horizon/thinking-multi-agent/app/requirements.txt

echo ""
echo "Starting API server on http://127.0.0.1:8030"
echo "Docs: http://127.0.0.1:8030/docs"
echo "Press CTRL+C to stop"
echo ""

PYTHONPATH="$(pwd)" uvicorn main:app \
    --host 0.0.0.0 \
    --port 8030 \
    --reload \
    --app-dir event_horizon/thinking-multi-agent/app
