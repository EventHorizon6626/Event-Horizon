# Migration Guide: Moving to Stage 1 Architecture

This guide documents the migration from the old agent system to the Stage 1 architecture.

> **Note**: Stages 2 and 3 are now also implemented. The full pipeline runs Stage 1 (data retrieval) -> Stage 2 (normalization) -> Stage 3 (LLM feature extraction). The primary entry point is now the FastAPI app on port 8030.

## What Changed?

### Old Structure (Before Stage 1)
```
agents/
|-- base_agent.py
|-- news_agent.py
|-- report_agent.py
+-- chart_agent.py

main.py - Sequential execution
```

### New Structure (Current)
```
event_horizon/
|-- data_pipeline/
|   |-- stage_1/              # Data Retrieval [IMPLEMENTED]
|   |   |-- agents/           # 5 agents (candlestick, earnings, news, technical, fundamentals)
|   |   |-- services/         # API clients (yfinance, Tavily, Exa, Massive)
|   |   |-- models/           # Output schemas
|   |   +-- orchestrator/     # Parallel execution
|   |-- stage_2/              # Normalization [IMPLEMENTED]
|   |   |-- normalizer/       # DataNormalizer, quality scoring
|   |   +-- orchestrator/
|   +-- stage_3/              # Feature Extraction [IMPLEMENTED]
|       |-- extractors/       # LLMFeatureExtractor (Opik-traced)
|       +-- orchestrator/
|-- analyzer_system/
|   +-- bull_bear_analyzer/   # 3-agent debate [IMPLEMENTED]
+-- thinking-multi-agent/
    +-- app/                  # FastAPI app (port 8030)
```

## Key Improvements

| Feature | Old System | Current System |
|---------|-----------|----------------|
| **Execution** | Sequential | Parallel (Stage 1), Pipeline (1->2->3) |
| **Speed** | ~15s for 3 agents | ~7s for 5 agents (parallel) |
| **Architecture** | Monolithic | 3-stage pipeline + analyzer system |
| **Data Format** | Mixed | Structured schemas (dataclasses) |
| **Error Handling** | All-or-nothing | Partial failures OK |
| **Entry Point** | `main.py` script | FastAPI app (REST API) |
| **News Source** | NewsAPI.org | Tavily (primary), Exa (fallback) |
| **LLM** | None | Mistral via vLLM (Stage 3, Bull-Bear) |
| **Observability** | None | Opik tracing |

## Migration Steps

### Step 1: Update Imports

**Before:**
```python
from agents.news_agent import NewsAgent
from agents.report_agent import ReportAnalysisAgent
from agents.chart_agent import ChartDataAgent
```

**After:**
```python
from event_horizon.data_pipeline.stage_1.agents.news_agent import NewsAgent
from event_horizon.data_pipeline.stage_1.agents.earnings_agent import EarningsAgent
from event_horizon.data_pipeline.stage_1.agents.candlestick_agent import CandlestickAgent
# Or use the orchestrator
from event_horizon.data_pipeline.stage_1.orchestrator.stage_1_orchestrator import Stage1Orchestrator
```

### Step 2: Use FastAPI Endpoints (Recommended)

Instead of running agents directly in Python, use the FastAPI API:

```bash
# Run all Stage 1 agents
curl -X POST http://localhost:8030/api/v1/analyze-portfolio \
  -H "Content-Type: application/json" \
  -d '{"portfolio": ["AAPL", "TSLA", "NVDA"]}'

# Run individual agents
curl -X POST http://localhost:8030/agents/candlestick \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL"]}'
```

### Step 3: Update Agent Names

| Old Name | New Name | Location |
|----------|----------|----------|
| `ChartDataAgent` | `CandlestickAgent` | `event_horizon.data_pipeline.stage_1.agents` |
| `ReportAnalysisAgent` | `EarningsAgent` | `event_horizon.data_pipeline.stage_1.agents` |
| `NewsAgent` | `NewsAgent` | `event_horizon.data_pipeline.stage_1.agents` (same name, new data source) |
| N/A (new) | `TechnicalAgent` | `event_horizon.data_pipeline.stage_1.agents` |
| N/A (new) | `FundamentalsAgent` | `event_horizon.data_pipeline.stage_1.agents` |

### Step 4: Update Data Access

**Before:**
```python
news_result = news_agent.execute(portfolio)
articles = news_result["result"]["news_by_stock"]
```

**After (via orchestrator):**
```python
result = orchestrator.execute(portfolio)
stage1_output = result["stage1_output"]

for symbol in stage1_output.symbols:
    news_data = stage1_output.news_data[symbol]
    chart_data = stage1_output.chart_data[symbol]
    earnings_data = stage1_output.earnings_data[symbol]
```

## Next Steps

Beyond Stage 1, the full pipeline is now available:

1. **Stage 2** (Normalization): Unifies heterogeneous Stage 1 data into `NormalizedSymbolData` with quality scoring
2. **Stage 3** (Feature Extraction): LLM extracts structured `SymbolFeatures` per symbol
3. **Bull-Bear Analyzer**: 3-agent debate generating `InvestmentThesis` per symbol
4. **Thinking Agent**: ReAct-style iterative reasoning with autonomous tool selection

All accessible via the FastAPI app at `http://localhost:8030`.

## See Also

- [Stage 1 Guide](./stage-1-guide.md)
- [Usage Guide](./usage.md)
- [Multi-Agent Architecture](../architecture/multi-agent-architecture.md)
