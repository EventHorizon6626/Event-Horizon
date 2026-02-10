# Event Horizon - Usage Guide

## Overview

Event Horizon runs as a **FastAPI application** (v3.0.0) serving a multi-agent trading analysis system. The primary entry point is the FastAPI app on port 8030, which provides 20+ REST endpoints for data retrieval, analysis, agent management, and more.

---

## Quick Start

### 1. Configure Environment

```bash
cd event_horizon/thinking-multi-agent
cp .env.example .env
nano .env
```

Set the required variables:
```bash
LLM_BASE_URL=http://localhost:8000       # Your vLLM or OpenAI-compatible endpoint
LLM_MODEL=mistralai/Ministral-3-14B-Reasoning-2512
TAVILY_API_KEY=your_tavily_key           # For news/web search
AGENTS_FILE=/tmp/agents.json             # Writable path for agent persistence
```

### 2. Install Dependencies

```bash
pip install -r app/requirements.txt
```

### 3. Start the App

```bash
# Using the start script
bash start.sh

# Or directly
cd app && uvicorn main:app --host 0.0.0.0 --port 8030
```

### 4. Verify

```bash
curl http://localhost:8030/health
```

Interactive API docs: `http://localhost:8030/docs`

---

## API Endpoints

### Health & Info

```bash
# Root - service info, model, agent count
curl http://localhost:8030/

# Health check - includes LLM backend status
curl http://localhost:8030/health

# List available LLM models
curl http://localhost:8030/models
```

### Data Agents (Stage 1)

Each data agent retrieves a specific type of market data:

```bash
# OHLCV price data
curl -X POST http://localhost:8030/agents/candlestick \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "TSLA"], "period": "1mo", "timeframe": "1d"}'

# Earnings and financial reports
curl -X POST http://localhost:8030/agents/earnings \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL"]}'

# News articles (via Tavily/Exa)
curl -X POST http://localhost:8030/agents/news \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL"], "days": 7}'

# Technical indicators (SMA, RSI, MACD)
curl -X POST http://localhost:8030/agents/technical \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL"], "indicators": ["SMA", "RSI", "MACD"]}'

# Fundamental metrics
curl -X POST http://localhost:8030/agents/fundamentals \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL"]}'

# Web search
curl -X POST http://localhost:8030/agents/web-search \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL"]}'
```

### Full Pipeline

```bash
# Run Stage 1 on a portfolio (all 5 agents in parallel)
curl -X POST http://localhost:8030/api/v1/analyze-portfolio \
  -H "Content-Type: application/json" \
  -d '{"portfolio": ["AAPL", "TSLA", "NVDA"]}'

# List supported agent types and their config options
curl http://localhost:8030/api/v1/supported-agents
```

### Bull-Bear Analyzer

```bash
# Run bull-bear debate analysis
curl -X POST http://localhost:8030/agents/bull-bear-analyzer \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL"]}'
```

The bull-bear endpoint supports 3 modes:
- **No data**: Returns `needs_data` with required agent suggestions
- **With `raw_data`**: Processes through Stage 1->2->3 pipeline, then debates
- **With `data`**: Runs debate directly on pre-processed SymbolFeatures

### Thinking Agent

```bash
# ReAct-style iterative reasoning
curl -X POST http://localhost:8030/agents/think \
  -H "Content-Type: application/json" \
  -d '{
    "stocks": ["AAPL", "MSFT"],
    "system_prompt": "You are a dividend-focused analyst. Find stocks with sustainable high dividends.",
    "max_iterations": 5,
    "available_tools": ["fundamentals", "earnings", "candlestick", "web_search"]
  }'
```

### Agent Management (CRUD)

```bash
# List all agents (built-in + user-created)
curl http://localhost:8030/agents

# Get agent details
curl http://localhost:8030/agents/{agent_id}

# Create a custom agent
curl -X POST http://localhost:8030/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "momentum-scanner",
    "description": "Scans for momentum trading opportunities",
    "type": "analysis",
    "system_prompt": "You are a momentum trading analyst..."
  }'

# Delete an agent (only user-created agents can be deleted)
curl -X DELETE http://localhost:8030/agents/{agent_id}

# Run analysis through any agent
curl -X POST http://localhost:8030/agents/{agent_id}/analyze \
  -H "Content-Type: application/json" \
  -d '{"task": "Analyze AAPL for momentum signals", "stocks": ["AAPL"]}'
```

### General Analysis

```bash
# Default financial analysis
curl -X POST http://localhost:8030/analyze \
  -H "Content-Type: application/json" \
  -d '{"task": "Analyze these stocks", "stocks": ["AAPL", "TSLA"]}'

# Streaming analysis (SSE)
curl -X POST http://localhost:8030/analyze/stream \
  -H "Content-Type: application/json" \
  -d '{"task": "Analyze AAPL"}'
```

### Utilities

```bash
# Generate a system prompt for a custom agent
curl -X POST http://localhost:8030/agents/generate-agent-system-prompt \
  -H "Content-Type: application/json" \
  -d '{"name": "ESG Analyst", "description": "Analyzes ESG factors", "category": "analysis"}'

# Execute a custom agent with specific tools
curl -X POST http://localhost:8030/agents/custom \
  -H "Content-Type: application/json" \
  -d '{
    "stocks": ["AAPL"],
    "system_prompt": "You analyze options flow...",
    "execution_mode": "fetch",
    "available_tools": ["web_search"]
  }'
```

---

## File Structure

```
event_horizon/
|-- thinking-multi-agent/
|   |-- .env                   # Environment configuration
|   |-- .env.example           # Template
|   |-- start.sh               # Startup script
|   +-- app/
|       |-- main.py            # FastAPI entry point
|       |-- models.py          # Pydantic request/response models
|       |-- agents.py          # AgentStore (CRUD + JSON persistence)
|       |-- seed.py            # Built-in agent definitions
|       |-- prompts.py         # System/user prompt builders
|       |-- routers/           # Route modules
|       +-- services/          # LLM, data agents, thinking engine, web search
|
|-- data_pipeline/
|   |-- stage_1/               # Data Retrieval (5 agents)
|   |-- stage_2/               # Normalization
|   +-- stage_3/               # LLM Feature Extraction
|
|-- analyzer_system/
|   +-- bull_bear_analyzer/    # 3-agent debate system
|
+-- core/
    +-- base/                  # BaseAgent, BaseOrchestrator
```

---

## Built-in Agents

The app seeds these built-in agents on startup (not deletable):

| Agent | Type | Description |
|-------|------|-------------|
| `candlestick` | data | OHLCV price data |
| `earnings` | data | Financial reports |
| `news` | data | News articles (Tavily/Exa) |
| `bull-bear-analyzer` | analysis | Bull-bear debate system |
| `risk-manager` | analysis | Risk assessment (prompt-based) |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_BASE_URL` | Yes | `http://localhost:8000` | OpenAI-compatible LLM endpoint |
| `LLM_MODEL` | Yes | `mistralai/Ministral-3-14B-Reasoning-2512` | Model ID |
| `LLM_API_KEY` | No | `""` | LLM API key |
| `LLM_TIMEOUT` | No | `300` | HTTP timeout (seconds) |
| `AGENTS_FILE` | No | `/data/agents.json` | Agent persistence path |
| `TAVILY_API_KEY` | For news/search | - | Tavily search API key |
| `EXASEARCH_API_KEY` | No | - | Exa search (fallback) |
| `LOG_LEVEL` | No | `info` | Logging level |

---

## Docker Deployment

```bash
cd event_horizon/thinking-multi-agent
docker-compose up -d --build

# Verify
curl http://localhost:8030/health
```

See [Docker Deploy Guide](./docker-deploy.md) for details.

---

## Troubleshooting

### App won't start
- Check that `AGENTS_FILE` points to a writable path
- Ensure LLM backend is reachable at `LLM_BASE_URL`

### LLM calls fail
- Verify `LLM_BASE_URL` is correct and the vLLM server is running
- Check `curl http://localhost:8000/v1/models` to see available models

### News agent returns no results
- Ensure `TAVILY_API_KEY` is set
- The Exa fallback requires `EXASEARCH_API_KEY`

### Port 8030 already in use
- Check what's using it: `sudo lsof -i :8030`
- Use a different port: `uvicorn app.main:app --port 8031`
