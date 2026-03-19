#!/bin/bash
set -e

MODEL="${LLM_MODEL:-mistralai/Ministral-3-14B-Reasoning-2512}"
VLLM_PORT=8000

echo "=== Event Horizon — Unified Financial Analysis API ==="
echo "Model: $MODEL"
echo "API:   http://0.0.0.0:8030"
echo "Docs:  http://0.0.0.0:8030/docs"
echo "======================================================="

if [ "${SKIP_VLLM}" = "true" ]; then
  echo "SKIP_VLLM=true — skipping local vLLM, using remote LLM backend"
  echo "LLM_BASE_URL=${LLM_BASE_URL}"
  export LLM_BASE_URL="${LLM_BASE_URL:-http://localhost:8000}"
else
  # Start vLLM in the background
  echo "Starting vLLM inference engine..."
  vllm serve "$MODEL" \
    --tokenizer_mode mistral \
    --config_format mistral \
    --load_format mistral \
    --reasoning-parser mistral \
    --enable-auto-tool-choice \
    --tool-call-parser mistral \
    --max-model-len 32768 \
    --gpu-memory-utilization 0.85 \
    --max-num-batched-tokens 8192 \
    --dtype bfloat16 \
    --tensor-parallel-size 1 \
    --trust-remote-code \
    --host 0.0.0.0 \
    --port $VLLM_PORT &

  VLLM_PID=$!

  # Wait for vLLM to become healthy
  echo "Waiting for model to load..."
  until curl -sf http://localhost:$VLLM_PORT/health > /dev/null 2>&1; do
    if ! kill -0 $VLLM_PID 2>/dev/null; then
      echo "ERROR: vLLM process died"
      exit 1
    fi
    sleep 5
  done
  echo "vLLM is ready!"

  export LLM_BASE_URL="http://localhost:$VLLM_PORT"
fi

# Start the FastAPI app in the foreground
echo "Starting API server on port 8030..."
exec uvicorn main:app --host 0.0.0.0 --port 8030 --app-dir /app
