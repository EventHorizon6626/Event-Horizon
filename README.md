# Event Horizon AI

Multi-agent trading system with two integrated systems:
1. **Data Processing Pipeline** - Transforms raw market data into feature vectors (3 stages)
2. **Decision-Making System** - Makes trading decisions from feature vectors (4 teams)

---

## Quick Start

```bash
# Configure
cp .env.example .env
nano .env  # Set NEWS_API_KEY

# Run Stage 1 Demo
python main_stage1.py
```

---

## Architecture

```
╔═══════════════════════════════════════════════════════════════════╗
║                 SYSTEM 1: DATA PROCESSING PIPELINE                 ║
╠═══════════════════════════════════════════════════════════════════╣
║  Stage 1: Data Retrieval    [IMPLEMENTED]                          ║
║    5 agents collect raw data in parallel                           ║
║                    ↓                                                ║
║  Stage 2: Normalization     [PLANNED]                              ║
║    Standardize formats and timestamps                              ║
║                    ↓                                                ║
║  Stage 3: Feature Extraction [PLANNED]                             ║
║    LLM/Neural AI extracts patterns                                 ║
╚═══════════════════════════════════════════════════════════════════╝
                              ↓
╔═══════════════════════════════════════════════════════════════════╗
║                 SYSTEM 2: DECISION-MAKING SYSTEM                   ║
╠═══════════════════════════════════════════════════════════════════╣
║  Team 1: Analyst Team       [PLANNED]                              ║
║    4 analysts run in parallel                                      ║
║                    ↓                                                ║
║  Team 2: Researcher Team    [PLANNED]                              ║
║    Bull/Bear debate                                                ║
║                    ↓                                                ║
║  Team 3: Risk Management    [PLANNED]                              ║
║    Position sizing debate                                          ║
║                    ↓                                                ║
║  Team 4: Trader Agent       [PLANNED]                              ║
║    Final decision & execution                                      ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## Project Structure

```
Event-Horizon-AI/
├── data_pipeline/              # System 1: Data Processing
│   ├── stage_1/                # Data Retrieval [IMPLEMENTED]
│   │   ├── agents/             # 5 specialized agents
│   │   ├── services/           # API clients
│   │   ├── models/             # Output schemas
│   │   └── orchestrator/       # Parallel execution
│   ├── stage_2/                # Normalization [PLANNED]
│   └── stage_3/                # Feature Extraction [PLANNED]
│
├── decision_system/            # System 2: Decision-Making [PLANNED]
│   ├── team_1_analysts/        # Multi-perspective analysis
│   ├── team_2_researchers/     # Bull/Bear debate
│   ├── team_3_risk/            # Position sizing
│   └── team_4_trader/          # Final execution
│
├── core/                       # Shared base classes
│   └── base/                   # BaseAgent, BaseOrchestrator
│
├── docs/                       # Documentation
│   ├── architecture/           # System architecture
│   ├── guides/                 # Usage guides
│   └── financial-library/      # Educational resources
│
├── main_stage1.py              # Stage 1 demo script
└── requirements.txt            # Python dependencies
```

---

## Stage 1 Agents

Currently implemented agents in `data_pipeline/stage_1/agents/`:

| Agent | Data Type | Source |
|-------|-----------|--------|
| CandlestickAgent | OHLCV price data | Yahoo Finance |
| EarningsAgent | Financial reports | Yahoo Finance |
| NewsAgent | News articles | NewsAPI |
| TechnicalAgent | Technical indicators (SMA, RSI, MACD) | yfinance |
| FundamentalsAgent | Fundamental metrics (P/E, ROE) | yfinance |

---

## Usage

### Python API

```python
from data_pipeline import Stage1Orchestrator

config = {
    "enabled_agents": ["candlestick", "earnings", "news", "technical", "fundamentals"],
    "max_workers": 5,
}

orchestrator = Stage1Orchestrator(config=config)
result = orchestrator.execute(["AAPL", "TSLA", "NVDA"])

# Access results
stage1_output = result["stage1_output"]
print(stage1_output.chart_data["AAPL"].candles)
print(stage1_output.technical_data["AAPL"].indicators["RSI"])
```

### Command Line

```bash
# Run Stage 1 demo
python main_stage1.py
```

---

## Environment Variables

```bash
# Required
NEWS_API_KEY=your_newsapi_key_here    # Get from newsapi.org

# Optional
LOG_LEVEL=INFO
```

---

## Documentation

- **[Multi-Agent Architecture](docs/architecture/multi-agent-architecture.md)** - Complete system design
- **[Stage 1 Guide](docs/guides/layer-1-guide.md)** - Data retrieval details
- **[Data Sources](docs/guides/data-sources.md)** - API information

---

## Tech Stack

- **Python 3.11+** - Core runtime
- **ThreadPoolExecutor** - Parallel agent execution
- **yfinance** - Stock data retrieval
- **NewsAPI** - News articles

---

## Implementation Status

- [x] Stage 1: Data Retrieval (5 agents)
- [ ] Stage 2: Normalization
- [ ] Stage 3: Feature Extraction
- [ ] Team 1: Analyst Team
- [ ] Team 2: Researcher Team
- [ ] Team 3: Risk Management
- [ ] Team 4: Trader Agent

---

## References

Inspired by [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
