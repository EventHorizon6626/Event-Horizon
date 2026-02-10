# Event Horizon - Configuration Guide

## Overview

Event Horizon is configured primarily through **environment variables** and the **FastAPI app's agent CRUD API**. The system runs as a FastAPI application on port 8030.

---

## Quick Start

### 1. Configure Environment

```bash
cd event_horizon/thinking-multi-agent
cp .env.example .env
nano .env
```

### 2. Set Required Variables

```bash
# LLM Configuration
LLM_BASE_URL=http://localhost:8000
LLM_MODEL=mistralai/Ministral-3-14B-Reasoning-2512
LLM_API_KEY=
LLM_TIMEOUT=300

# Agent Persistence
AGENTS_FILE=/tmp/agents.json

# News & Web Search
TAVILY_API_KEY=your_tavily_key
EXASEARCH_API_KEY=your_exa_key    # Optional fallback

# Optional
MASSIVE_API_KEY=your_massive_key
USE_MASSIVE_API=false
LOG_LEVEL=info
```

### 3. Start the App

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8030
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_BASE_URL` | Yes | `http://localhost:8000` | OpenAI-compatible LLM endpoint |
| `LLM_MODEL` | Yes | `mistralai/Ministral-3-14B-Reasoning-2512` | Model ID |
| `LLM_API_KEY` | No | `""` | API key for LLM |
| `LLM_TIMEOUT` | No | `300` | HTTP timeout (seconds) |
| `AGENTS_FILE` | No | `/data/agents.json` | Path for agent JSON persistence |
| `TAVILY_API_KEY` | For news/search | - | Tavily search API key |
| `EXASEARCH_API_KEY` | No | - | Exa search API key (fallback) |
| `MASSIVE_API_KEY` | No | - | Massive.com chart data key |
| `USE_MASSIVE_API` | No | `false` | Use Massive.com instead of yfinance |
| `LOG_LEVEL` | No | `info` | Logging level (debug, info, warning, error) |

---

## Agent Configuration

### Built-in Agents

The app seeds 5 built-in agents on startup (not deletable):

| Agent | Type | Description |
|-------|------|-------------|
| `candlestick` | data | OHLCV price data |
| `earnings` | data | Financial reports |
| `news` | data | News articles |
| `bull-bear-analyzer` | analysis | Bull-bear debate |
| `risk-manager` | analysis | Risk assessment |

### Creating Custom Agents via API

```bash
# Create a custom analysis agent
curl -X POST http://localhost:8030/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "momentum-scanner",
    "description": "Scans for momentum trading opportunities",
    "type": "analysis",
    "system_prompt": "You are a momentum trading analyst. Focus on price trends, volume, and RSI.",
    "temperature": 0.5,
    "max_tokens": 2000
  }'

# List all agents
curl http://localhost:8030/agents

# Delete a custom agent
curl -X DELETE http://localhost:8030/agents/{agent_id}
```

### Agent Types

- **data**: Runs Stage 1 data retrieval (e.g., candlestick, earnings, news)
- **analysis**: Runs LLM-based analysis with a system prompt

When you call `POST /agents/{id}/analyze`, data agents run the pipeline while analysis agents call the LLM.

---

## Data Agent Configuration

Stage 1 data agents use a default configuration defined in `event_horizon/thinking-multi-agent/app/services/data_agents.py`:

```python
STAGE1_CONFIG = {
    "enabled_agents": ["candlestick", "earnings", "news", "technical", "fundamentals"],
    "max_workers": 5,
    "agent_configs": {
        "candlestick": {"period": "1mo", "interval": "1d"},
        "earnings": {"include_financials": True, "earnings_periods": 4},
        "news": {"max_articles_per_stock": 10, "days_back": 7},
        "technical": {"indicators": ["SMA", "EMA", "RSI", "MACD"], "look_back_days": 30},
        "fundamentals": {"include_ratios": True}
    }
}
```

These defaults are used when calling individual agent endpoints (e.g., `POST /agents/candlestick`) or the full pipeline (`POST /api/v1/analyze-portfolio`). Override specific settings via request parameters.

---

## LLM Configuration

The app communicates with any **OpenAI-compatible** LLM endpoint (e.g., vLLM, OpenAI, Ollama).

### Using vLLM (Local)

```bash
LLM_BASE_URL=http://localhost:8000
LLM_MODEL=mistralai/Ministral-3-14B-Reasoning-2512
LLM_API_KEY=
```

### Using OpenAI

```bash
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
LLM_API_KEY=sk-your-key
```

### Using Ollama

```bash
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=mistral
LLM_API_KEY=
```

---

## Agent Persistence

The `AgentStore` persists agents to a JSON file specified by `AGENTS_FILE`.

- Default: `/data/agents.json` (designed for Docker volumes)
- For local development: `AGENTS_FILE=/tmp/agents.json`
- Built-in agents are re-seeded on startup if missing
- User-created agents persist across restarts

---

## Deployment Scenarios

### Local Development

```bash
AGENTS_FILE=/tmp/agents.json
LLM_BASE_URL=http://localhost:8000
LOG_LEVEL=debug
```

### Docker

```bash
AGENTS_FILE=/data/agents.json    # Mount a volume at /data
LLM_BASE_URL=http://host.docker.internal:8000
LOG_LEVEL=info
```

### Production (VPS)

```bash
AGENTS_FILE=/var/data/agents.json
LLM_BASE_URL=http://localhost:8000
LOG_LEVEL=warning
```

---

## Legacy: config.yaml

The `event_horizon/utils/config_loader.py` utility supports YAML configuration files with `${ENV_VAR}` substitution, but the current FastAPI app does **not** use config.yaml. All configuration is done through environment variables and the agent CRUD API.

---

## Troubleshooting

### "AGENTS_FILE not writable"
Set `AGENTS_FILE` to a writable path (e.g., `/tmp/agents.json` for local dev).

### "LLM backend unreachable"
Check `LLM_BASE_URL` and verify your vLLM/OpenAI server is running:
```bash
curl http://localhost:8000/v1/models
```

### "News agent returns no results"
Ensure `TAVILY_API_KEY` is set. Without it, news and web search features won't work.

---

## Best Practices

1. **Use `.env` files** -- never hardcode API keys
2. **Set `AGENTS_FILE`** to a persistent, writable path
3. **Monitor LLM health** via `GET /health` endpoint
4. **Use `LOG_LEVEL=debug`** during development
5. **Keep `.env` out of git** -- use `.env.example` as template
