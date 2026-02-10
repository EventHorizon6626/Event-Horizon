# Event Horizon AI - System Architecture

## Option 2: Backend Proxy Architecture (Recommended)

```
+-------------------------------------------------------------------------+
|                          User's Browser                                 |
|                     http://localhost:3021                               |
|                        (React Frontend)                                 |
+--------------------------------+----------------------------------------+
                                 |
                                 | HTTPS
                                 | fetch(REACT_APP_BE_API_URL + '/ai/...')
                                 |
                                 v
+-------------------------------------------------------------------------+
|                          VPS Server                                     |
|                   178.18.255.19 or domain                               |
|                                                                         |
|  +-------------------------------------------------------------------+ |
|  |        Backend API (Node.js/Express + PM2)                        | |
|  |        https://evth-api.hirodev.space/api                         | |
|  |                                                                   | |
|  |  Routes:                                                          | |
|  |  - /api/ai/health               -> Health check                  | |
|  |  - /api/ai/portfolio/analyze     -> Full pipeline analysis        | |
|  |  - /api/ai/agents/candlestick   -> Candlestick data              | |
|  |  - /api/ai/agents/earnings      -> Earnings data                 | |
|  |  - /api/ai/agents/news          -> News data                     | |
|  |  - /api/ai/agents/technical     -> Technical indicators          | |
|  |  - /api/ai/agents/fundamentals  -> Fundamental metrics           | |
|  |  - /api/ai/agents/web-search    -> Web search                    | |
|  |  - /api/ai/agents/bull-bear     -> Bull-bear analysis            | |
|  |  - /api/ai/agents/think         -> Thinking agent                | |
|  |  - /api/ai/agents (CRUD)        -> Agent management              | |
|  |  - /api/ai/analyze              -> General analysis              | |
|  +---------------------------+---------------------------------------+ |
|                              |                                         |
|                              | HTTP (localhost only)                   |
|                              | httpx/axios -> http://localhost:8030    |
|                              |                                         |
|                              v                                         |
|  +-----------------------------------------------------------------+  |
|  |        AI Service (Python/FastAPI v3.0.0)                       |  |
|  |        http://127.0.0.1:8030                                    |  |
|  |        (NOT exposed to internet - localhost only)               |  |
|  |                                                                 |  |
|  |  Endpoints:                                                     |  |
|  |  - GET  /                          Root (health + model info)   |  |
|  |  - GET  /health                    Health check                 |  |
|  |  - GET  /models                    List LLM models              |  |
|  |  - POST /api/v1/analyze-portfolio  Full Stage 1 pipeline        |  |
|  |  - GET  /api/v1/supported-agents   List data agent types        |  |
|  |  - POST /agents/candlestick        Candlestick data             |  |
|  |  - POST /agents/earnings           Earnings data                |  |
|  |  - POST /agents/news               News data                   |  |
|  |  - POST /agents/technical          Technical indicators         |  |
|  |  - POST /agents/fundamentals       Fundamental metrics          |  |
|  |  - POST /agents/web-search         Web search (Tavily/Exa)     |  |
|  |  - POST /agents/bull-bear-analyzer Bull-bear debate             |  |
|  |  - POST /agents/custom             Custom agent execution       |  |
|  |  - POST /agents/think              Thinking agent (ReAct)       |  |
|  |  - POST /agents/generate-agent-system-prompt  Prompt generation |  |
|  |  - POST /agents                    Create agent                 |  |
|  |  - GET  /agents                    List all agents              |  |
|  |  - GET  /agents/{id}               Get agent details            |  |
|  |  - DELETE /agents/{id}             Delete agent                 |  |
|  |  - POST /agents/{id}/analyze       Dispatch agent analysis      |  |
|  |  - POST /analyze                   General analysis             |  |
|  |  - POST /analyze/stream            Streaming analysis (SSE)     |  |
|  |  - GET  /docs                      Swagger documentation        |  |
|  |                                                                 |  |
|  |  Data Pipeline:                                                 |  |
|  |  -- Stage 1: 5 data agents (parallel, ThreadPoolExecutor)      |  |
|  |  -- Stage 2: DataNormalizer (quality scoring)                   |  |
|  |  -- Stage 3: LLMFeatureExtractor (Mistral/vLLM, Opik-traced)  |  |
|  |                                                                 |  |
|  |  Analyzer System:                                               |  |
|  |  -- BullBearAnalyzer (BullResearcher, BearResearcher, Manager) |  |
|  |                                                                 |  |
|  |  Services:                                                      |  |
|  |  -- LLM client (httpx, OpenAI-compatible)                      |  |
|  |  -- Thinking engine (ReAct loop + tool discovery)              |  |
|  |  -- Web search (Tavily + Exa)                                  |  |
|  |  -- Data processing (Stage 1->2->3 pipeline)                   |  |
|  +-----------------------------------------------------------------+  |
|                                                                         |
+-------------------------------------------------------------------------+
```

---

## Request Flow

### Example: Portfolio Analysis (Full Pipeline)

1. **User Action** (Frontend - localhost:3021)
   ```javascript
   analyzePortfolio(['AAPL', 'GOOGL', 'TSLA'])
   ```

2. **Frontend -> Backend** (HTTPS)
   ```
   POST https://evth-api.hirodev.space/api/ai/portfolio/analyze
   Body: { portfolio: ['AAPL', 'GOOGL', 'TSLA'] }
   ```

3. **Backend -> AI Service** (HTTP localhost)
   ```
   POST http://localhost:8030/api/v1/analyze-portfolio
   Body: { portfolio: ['AAPL', 'GOOGL', 'TSLA'] }
   ```

4. **AI Service Processes**
   - Stage 1: Runs 5 data agents in parallel (candlestick, earnings, news, technical, fundamentals)
   - Collects OHLCV from yfinance, news from Tavily/Exa, earnings/financials/technicals/fundamentals from yfinance
   - Returns structured Stage1Output

5. **AI Service -> Backend** (Response)
   ```json
   {
     "status": "success",
     "portfolio_id": "...",
     "symbols": ["AAPL", "GOOGL", "TSLA"],
     "stage1_output": { ... },
     "execution_time_seconds": 8.5,
     "agents_executed": ["candlestick", "earnings", "news", "technical", "fundamentals"]
   }
   ```

---

## Components Breakdown

### 1. Frontend (React)

**Location:** Separate repository
**Port:** 3021 (development)
**Environment:**
- `REACT_APP_BE_API_URL=https://evth-api.hirodev.space/api`

---

### 2. Backend API (Node.js/Express)

**Location:** Separate repository
**Port:** 80/443 (behind Nginx)
**Domain:** evth-api.hirodev.space
**Process Manager:** PM2

**Responsibilities:**
- Proxy to AI service
- Authentication (JWT/sessions)
- Rate limiting
- Request validation

---

### 3. AI Service (Python/FastAPI v3.0.0)

**Location:** This repository (`Event-Horizon`)
**Port:** 8030 (localhost only)
**Entry Point:** `event_horizon/thinking-multi-agent/app/main.py`

**Key Features:**
- 20+ REST endpoints for data agents, analysis, CRUD, thinking, search
- Full Stage 1->2->3 data pipeline
- Bull-Bear Analyzer (3-agent debate)
- Thinking Agent (ReAct-style iterative reasoning)
- Agent CRUD with JSON persistence (AgentStore)
- Web search via Tavily/Exa
- Streaming analysis (SSE)
- Opik observability integration
- LLM integration via OpenAI-compatible API (Mistral/vLLM)

---

## Security Features

### 1. AI Service Isolation
- Binds to `127.0.0.1` only (not `0.0.0.0`)
- NOT accessible from internet
- Only Backend on same VPS can access it

### 2. Backend as Gateway
- Single entry point for frontend
- Can add authentication layer
- Can add rate limiting
- Input validation before forwarding

### 3. Firewall
- Port 8030 blocked from external access
- Only 80/443 exposed for Backend API

---

## Environment Configuration

### AI Service `.env`
```bash
# LLM Configuration
LLM_BASE_URL=http://localhost:8000
LLM_MODEL=mistralai/Ministral-3-14B-Reasoning-2512
LLM_API_KEY=
LLM_TIMEOUT=300

# Agent persistence
AGENTS_FILE=/data/agents.json

# News & Web Search
TAVILY_API_KEY=your_tavily_key
EXASEARCH_API_KEY=your_exa_key

# Optional
MASSIVE_API_KEY=your_massive_key
USE_MASSIVE_API=false
LOG_LEVEL=info
```

### Frontend `.env`
```bash
REACT_APP_BE_API_URL=https://evth-api.hirodev.space/api
NODE_ENV=development
PORT=3021
```

---

## Technologies Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | React | User interface |
| Backend API | Node.js/Express | REST API, proxy |
| AI Service | Python/FastAPI | Multi-agent system |
| LLM | Mistral via vLLM | Local inference (OpenAI-compatible) |
| Observability | Opik | Tracing and monitoring |
| HTTP Client | httpx | Async LLM communication |
| News Data | Tavily (primary), Exa (fallback) | News/web search |
| Financial Data | yfinance | Stock/ETF data source |
| Chart Data | Yahoo Finance / Massive.com | OHLCV price data |
| Process Mgmt (BE) | PM2 | Backend process manager |
| Deployment | Docker / systemd | AI service deployment |

---

## Monitoring & Logs

### AI Service
```bash
# Docker
docker logs -f event-horizon-ai

# Direct
uvicorn app.main:app --host 0.0.0.0 --port 8030 --log-level info
```

### Backend
```bash
pm2 status
pm2 logs
pm2 monit
```

---

## Future Enhancements

### Planned Analyzer Teams
- [ ] Team 1: Analyst Team (multi-perspective parallel analysis)
- [ ] Team 3: Risk Management Team (position sizing debate)
- [ ] Team 4: Trader Agent (final execution decisions)

### Infrastructure
- [ ] Redis caching layer
- [ ] PostgreSQL for data persistence
- [ ] WebSocket for real-time updates

### Features
- [ ] Portfolio tracking
- [ ] Historical analysis
- [ ] Backtesting integration

---

**Current Status:** FastAPI v3.0.0 with full data pipeline + Bull-Bear Analyzer
**Port:** 8030
**Security:** AI Service isolated, localhost-only
