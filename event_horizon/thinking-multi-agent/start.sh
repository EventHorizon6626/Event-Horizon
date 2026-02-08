#!/bin/bash
set -e

# ============================================================
# Thinking Multi-Agent: Mistral Reasoning Financial Analyzer
# Single container: vLLM + FastAPI on port 8030
# ============================================================

# Check for .env file
if [ ! -f .env ]; then
    echo "ERROR: .env file not found."
    echo "Create one from the example:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env and add your HuggingFace token"
    exit 1
fi

# Check for HF token
source .env
if [ -z "$HF_TOKEN" ] || [ "$HF_TOKEN" = "hf_your_token_here" ]; then
    echo "ERROR: Please set a valid HF_TOKEN in your .env file."
    echo "Get a token at: https://huggingface.co/settings/tokens"
    exit 1
fi

echo "=== Starting Thinking Multi-Agent ==="
echo "Model: mistralai/Ministral-3-14B-Reasoning-2512"
echo "API:   http://localhost:8030"
echo "Docs:  http://localhost:8030/docs"
echo ""
echo "NOTE: First startup downloads the model (~27GB). This may take a while."
echo "======================================="
echo ""

docker compose up --build "$@"
