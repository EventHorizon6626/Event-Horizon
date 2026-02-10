# Event Horizon AI

Multi-agent trading system with two integrated systems:
1. **Data Processing Pipeline** - Transforms raw market data into feature vectors (3 stages)
2. **Analyzer System** - Makes trading decisions from feature vectors (Bull-Bear Analyzer + planned teams)

---

## REPO
* AI core: https://github.com/EventHorizon6626/Event-Horizon
* Frontend: https://github.com/EventHorizon6626/FE
* Backend: https://github.com/EventHorizon6626/BE

## Quick Start

```bash
# Configure
cd event_horizon/thinking-multi-agent
cp .env.example .env
nano .env  # Set LLM_BASE_URL, LLM_MODEL, TAVILY_API_KEY

# Run FastAPI app
bash start.sh
# or directly:
uvicorn app.main:app --host 0.0.0.0 --port 8030
```

The API is available at `http://localhost:8030`. Interactive docs at `http://localhost:8030/docs`.

---

## Architecture

```
+===================================================================+
|             SYSTEM 1: DATA PROCESSING PIPELINE                     |
+===================================================================+
|  Stage 1: Data Retrieval    [IMPLEMENTED]                          |
|    5 agents collect raw data in parallel                           |
|                    |                                               |
|  Stage 2: Normalization     [IMPLEMENTED]                          |
|    Standardize formats, quality scoring                            |
|                    |                                               |
|  Stage 3: Feature Extraction [IMPLEMENTED]                         |
|    LLM extracts structured insights per symbol                     |
+===================================================================+
                              |
+===================================================================+
|             SYSTEM 2: ANALYZER SYSTEM                              |
+===================================================================+
|  Bull-Bear Analyzer         [IMPLEMENTED]                          |
|    3-agent debate (Bull/Bear/Manager)                              |
|                    |                                               |
|  Team 1: Analyst Team       [PLANNED]                              |
|    Multi-perspective analysis                                      |
|                    |                                               |
|  Team 3: Risk Management    [PLANNED]                              |
|    Position sizing debate                                          |
|                    |                                               |
|  Team 4: Trader Agent       [PLANNED]                              |
|    Final decision & execution                                      |
+===================================================================+
```

---

## Project Structure

```
event_horizon/
|-- core/                          # Shared base classes
|   +-- base/                      # BaseAgent, BaseOrchestrator
|
|-- data_pipeline/                 # System 1: Data Processing
|   |-- stage_1/                   # Data Retrieval [IMPLEMENTED]
|   |   |-- agents/                # 5 specialized agents + utils/
|   |   |-- services/              # API clients (yfinance, Tavily, Exa, Massive)
|   |   |-- models/                # Output schemas (Stage1Output)
|   |   +-- orchestrator/          # Parallel execution (ThreadPoolExecutor)
|   |-- stage_2/                   # Normalization [IMPLEMENTED]
|   |   |-- normalizer/            # DataNormalizer, quality scoring
|   |   |-- models/                # NormalizedSymbolData, Stage2Output
|   |   +-- orchestrator/          # Sequential symbol processing
|   +-- stage_3/                   # Feature Extraction [IMPLEMENTED]
|       |-- extractors/            # LLMFeatureExtractor (Opik-traced)
|       |-- models/                # SymbolFeatures, Stage3Output
|       +-- orchestrator/          # LLM extraction coordination
|
|-- analyzer_system/               # System 2: Analyzer
|   +-- bull_bear_analyzer/        # Bull-Bear Debate [IMPLEMENTED]
|       |-- agents/                # BullResearcher, BearResearcher, ResearchManager
|       |-- models/                # BullArgument, BearArgument, InvestmentThesis
|       +-- orchestrator/          # BullBearAnalyzer (debate coordinator)
|
|-- utils/                         # Configuration loader
|
+-- thinking-multi-agent/          # FastAPI Application (v3.0.0)
    +-- app/
        |-- main.py                # FastAPI entry point (port 8030)
        |-- models.py              # Request/response Pydantic models
        |-- agents.py              # AgentStore (CRUD + JSON persistence)
        |-- seed.py                # Built-in agent definitions
        |-- prompts.py             # System/user prompt builders
        |-- routers/               # Route modules
        |   |-- health.py          # /, /health, /models
        |   |-- data_pipeline.py   # /api/v1/analyze-portfolio, /api/v1/supported-agents
        |   |-- agents_named.py    # Named agent endpoints (data, bull-bear, think, etc.)
        |   |-- agents_crud.py     # Agent CRUD + /agents/{id}/analyze dispatch
        |   +-- analysis.py        # /analyze, /analyze/stream
        +-- services/              # App-level services
            |-- llm.py             # Unified LLM client (OpenAI-compatible)
            |-- data_agents.py     # Stage 1 agent execution wrapper
            |-- data_processing.py # Raw data -> Stage 1->2->3 pipeline
            |-- thinking_engine.py # ReAct thinking loop + tool discovery
            +-- web_search.py      # Tavily/Exa web search
```

---

## Stage 1 Agents

Data retrieval agents in `event_horizon/data_pipeline/stage_1/agents/`:

| Agent | Data Type | Source |
|-------|-----------|--------|
| CandlestickAgent | OHLCV price data | Yahoo Finance / Massive.com |
| EarningsAgent | Financial reports (stocks, ETFs, mutual funds) | Yahoo Finance |
| NewsAgent | News articles | Tavily (primary), Exa (fallback) |
| TechnicalAgent | Technical indicators (SMA, RSI, MACD) | yfinance |
| FundamentalsAgent | Fundamental metrics (P/E, ROE) | yfinance |

---

## Usage

### FastAPI Endpoints (Primary)

```bash
# Health check
curl http://localhost:8030/health

# Run a specific data agent
curl -X POST http://localhost:8030/agents/candlestick \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "TSLA"]}'

# Run bull-bear analysis
curl -X POST http://localhost:8030/agents/bull-bear-analyzer \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL"]}'

# Run thinking agent (ReAct-style iterative reasoning)
curl -X POST http://localhost:8030/agents/think \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL"], "system_prompt": "Analyze for momentum trading", "max_iterations": 5}'

# Full pipeline analysis
curl -X POST http://localhost:8030/api/v1/analyze-portfolio \
  -H "Content-Type: application/json" \
  -d '{"portfolio": ["AAPL", "TSLA", "NVDA"]}'

# List all agents
curl http://localhost:8030/agents

# Web search
curl -X POST http://localhost:8030/agents/web-search \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL"]}'
```

Interactive API docs are available at `http://localhost:8030/docs` (Swagger UI).

---

## Environment Variables

```bash
# LLM Configuration (required)
LLM_BASE_URL=http://localhost:8000       # OpenAI-compatible endpoint (e.g. vLLM)
LLM_MODEL=mistralai/Ministral-3-14B-Reasoning-2512
LLM_API_KEY=                             # API key if required
LLM_TIMEOUT=300                          # HTTP timeout in seconds

# Agent persistence
AGENTS_FILE=/data/agents.json            # Path for agent JSON store

# News & Web Search
TAVILY_API_KEY=your_tavily_key           # Primary news/search source
EXASEARCH_API_KEY=your_exa_key           # Fallback search source

# Optional
MASSIVE_API_KEY=your_massive_key         # Massive.com chart data (alternative to yfinance)
USE_MASSIVE_API=false                    # Set true to use Massive.com
LOG_LEVEL=info
```

---

## Documentation

- **[Multi-Agent Architecture](docs/architecture/multi-agent-architecture.md)** - Complete system design
- **[System Architecture](docs/architecture/system-architecture.md)** - Deployment & API reference
- **[Stage 1 Guide](docs/guides/stage-1-guide.md)** - Data retrieval details
- **[Thinking Agent Guide](docs/guides/thinking-agent.md)** - ReAct reasoning system
- **[Data Sources](docs/guides/data-sources.md)** - API information
- **[Usage Guide](docs/guides/usage.md)** - FastAPI app usage

---

## Tech Stack

- **Python 3.11+** - Core runtime
- **FastAPI** - REST API framework
- **Mistral via vLLM** - Local LLM inference (OpenAI-compatible)
- **Opik** - Observability/tracing (with graceful fallback)
- **httpx** - Async HTTP client for LLM calls
- **yfinance** - Stock data retrieval
- **Tavily** - Primary news/web search
- **Exa** - Fallback news/web search
- **ThreadPoolExecutor** - Parallel agent execution

---

## Implementation Status

- [x] Stage 1: Data Retrieval (5 agents)
- [x] Stage 2: Normalization & Quality Scoring
- [x] Stage 3: LLM Feature Extraction
- [x] Bull-Bear Analyzer (3-agent debate system)
- [x] FastAPI App with 20+ endpoints (v3.0.0)
- [x] Thinking Agent (ReAct-style iterative reasoning)
- [x] Agent CRUD (create, list, delete, dispatch)
- [x] Web Search (Tavily + Exa)
- [x] Opik observability integration
- [ ] Team 1: Analyst Team
- [ ] Team 3: Risk Management
- [ ] Team 4: Trader Agent

---

## References

Inspired by (docs/core-refs) and (docs/references)
