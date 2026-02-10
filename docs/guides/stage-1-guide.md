# Stage 1: Data Retrieval Guide

## Overview

Stage 1 is the foundation of Event Horizon's three-stage data pipeline. It handles **heterogeneous data collection** from multiple sources, with each agent specializing in one data type. All agents run in parallel for maximum speed.

## Architecture

```
+-------------------------------------------------------------------------+
|                         STAGE 1: DATA RETRIEVAL                         |
|                     (Heterogeneous Data Collection)                     |
|-------------------------------------------------------------------------|
|                                                                         |
|  +----------+  +----------+  +----------+  +----------+  +----------+  |
|  |Candlestick|  | Earnings |  |   News   |  |Technical |  |Fundament-|  |
|  |  Agent    |  |  Agent   |  |  Agent   |  |  Agent   |  |als Agent |  |
|  |           |  |          |  |          |  |          |  |          |  |
|  | OHLCV    |  |Financial |  |Articles &|  |SMA, RSI, |  |P/E, ROE, |  |
|  | data     |  | reports  |  |headlines |  |MACD      |  |ratios    |  |
|  +----------+  +----------+  +----------+  +----------+  +----------+  |
|       |             |            |             |             |          |
|       v             v            v             v             v          |
|  +----------+  +----------+  +----------+  +----------+  +----------+  |
|  |  Chart   |  |Financial |  |  News    |  |  Stock   |  |  Stock   |  |
|  | Service  |  | Service  |  | Search   |  |  Tools   |  |  Tools   |  |
|  +----------+  +----------+  +----------+  +----------+  +----------+  |
|       |             |            |             |             |          |
|       v             v            v             v             v          |
|  +----------+  +----------+  +----------+  +----------+  +----------+  |
|  |  Yahoo   |  |  Yahoo   |  |  Tavily  |  | yfinance |  | yfinance |  |
|  | Finance  |  | Finance  |  |  / Exa   |  |          |  |          |  |
|  |Massive.com|  |          |  |          |  |          |  |          |  |
|  +----------+  +----------+  +----------+  +----------+  +----------+  |
|                                                                         |
|                   Parallel, Independent Execution                       |
|                            v  v  v  v  v                               |
|                                                                         |
|              Stage1Output (Heterogeneous Data)                          |
+-------------------------------------------------------------------------+
```

## Key Principles

1. **Specialization**: Each agent retrieves data from ONE source only
2. **Independence**: Agents have no dependencies on each other
3. **Parallel Execution**: All agents run simultaneously for maximum speed
4. **Raw Output**: Data is kept in agent-specific formats (normalization happens in Stage 2)

## Components

### Stage 1 Orchestrator

Manages parallel execution of all data retrieval agents.

**Location**: `event_horizon/data_pipeline/stage_1/orchestrator/stage_1_orchestrator.py`

**Features**:
- Parallel agent execution using ThreadPoolExecutor (default: 5 workers)
- Error handling and partial failure support
- Unified output aggregation into Stage1Output
- Configurable agent selection

### Data Retrieval Agents

#### 1. Candlestick Agent

**Purpose**: Retrieve OHLCV (Open, High, Low, Close, Volume) price data

**File**: `event_horizon/data_pipeline/stage_1/agents/candlestick_agent.py`

**Data Sources**:
- Yahoo Finance (default)
- Massive.com API (set `USE_MASSIVE_API=true`)

**Configuration**:
```python
{
    "period": "1mo",      # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max
    "interval": "1d",     # 1m, 5m, 15m, 1h, 1d, 1wk, 1mo
    "data_source": "yahoo"  # "yahoo" or "massive"
}
```

**Output**: `ChartData` (symbol, candles, period, interval)

#### 2. Earnings Agent

**Purpose**: Retrieve earnings reports and financial statements

**File**: `event_horizon/data_pipeline/stage_1/agents/earnings_agent.py`

**Data Source**: Yahoo Finance (handles stocks, ETFs, and mutual funds)

**Configuration**:
```python
{
    "include_financials": True,
    "earnings_periods": 4,  # Number of quarters
    "top_holdings": 10      # For ETFs
}
```

**Output**: `EarningsData` (symbol, security_type, name, earnings_reports, financial_statements, metrics)

#### 3. News Agent

**Purpose**: Retrieve news articles about stocks

**File**: `event_horizon/data_pipeline/stage_1/agents/news_agent.py`

**Data Source**: Tavily (primary), Exa (fallback) via `news_search_client.py`

**Configuration**:
```python
{
    "max_articles_per_stock": 10,
    "days_back": 7
}
```

**Output**: `NewsData` (symbol, articles, total_articles, data_source)

#### 4. Technical Agent

**Purpose**: Calculate technical indicators

**File**: `event_horizon/data_pipeline/stage_1/agents/technical_agent.py`

**Data Source**: Yahoo Finance via yfinance + custom calculations in `stock_tools.py`

**Configuration**:
```python
{
    "indicators": ["SMA", "EMA", "RSI", "MACD"],
    "look_back_days": 30
}
```

**Supported Indicators**: SMA (20/50 day), EMA (12/26 day), RSI (14 period), MACD

**Output**: `TechnicalData` (symbol, indicators, trade_date, look_back_days)

#### 5. Fundamentals Agent

**Purpose**: Retrieve fundamental metrics and financial ratios

**File**: `event_horizon/data_pipeline/stage_1/agents/fundamentals_agent.py`

**Data Source**: Yahoo Finance via yfinance + `stock_tools.py`

**Metrics**: P/E, Forward P/E, PEG, Price/Book, Price/Sales, profit margins, ROE, ROA, debt/equity, dividends

**Output**: `FundamentalsData` (symbol, fundamentals_text)

### Services

Located in `event_horizon/data_pipeline/stage_1/services/`:

| Service | File | Description |
|---------|------|-------------|
| ChartDataClient | `chart_data_client.py` | Yahoo Finance OHLCV retrieval |
| MassiveChartClient | `massive_chart_client.py` | Massive.com OHLCV (alternative) |
| FinancialDataClient | `financial_data_client.py` | Yahoo Finance earnings, financials, metrics |
| `tavily_news_search()` | `news_search_client.py` | Tavily news search (primary) |
| `exa_news_search()` | `news_search_client.py` | Exa news search (fallback) |
| NewsAPIClient | `news_api_client.py` | NewsAPI.org (legacy, not used) |

### Utility Functions

Located in `event_horizon/data_pipeline/stage_1/agents/utils/stock_tools.py`:

- `get_stock_data()` -- raw OHLCV text via yfinance
- `get_indicators()` -- calculates SMA, EMA, RSI, MACD using pandas
- `get_fundamentals()` -- formatted text with company info, valuation, profitability, financial health, growth, dividends

## Usage

### Via FastAPI (Recommended)

```bash
# Run all Stage 1 agents on a portfolio
curl -X POST http://localhost:8030/api/v1/analyze-portfolio \
  -H "Content-Type: application/json" \
  -d '{"portfolio": ["AAPL", "TSLA", "NVDA"]}'

# Run individual agents
curl -X POST http://localhost:8030/agents/candlestick \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "TSLA"]}'
```

### Via Python

```python
from event_horizon.data_pipeline.stage_1.orchestrator.stage_1_orchestrator import Stage1Orchestrator

config = {
    "enabled_agents": ["candlestick", "earnings", "news", "technical", "fundamentals"],
    "max_workers": 5,
    "agent_configs": {
        "candlestick": {"period": "3mo", "interval": "1d"},
        "technical": {"indicators": ["SMA", "RSI", "MACD", "EMA"], "look_back_days": 60}
    }
}

orchestrator = Stage1Orchestrator(config=config)
result = orchestrator.execute(["AAPL", "TSLA", "NVDA"])

stage1_output = result["stage1_output"]
print(stage1_output.chart_data["AAPL"].candles)
print(stage1_output.technical_data["AAPL"].indicators["RSI"])
```

## Output Format

### Stage1Output

```python
Stage1Output(
    portfolio_id: str,
    symbols: List[str],

    # Data by agent type (Dict[symbol, DataType])
    news_data: Dict[str, NewsData],
    earnings_data: Dict[str, EarningsData],
    chart_data: Dict[str, ChartData],
    technical_data: Dict[str, TechnicalData],
    fundamentals_data: Dict[str, FundamentalsData],
    web_search_data: Dict[str, WebSearchData],
    options_data: Dict[str, OptionsFlowData],    # Future
    social_data: Dict[str, SocialMediaData],     # Future
    sec_data: Dict[str, SECFilingsData],         # Future

    # Metadata
    metadata: Dict[str, Any]
)
```

## Error Handling

Stage 1 supports partial failures:

- **Success**: All agents completed successfully
- **Partial Success**: Some agents succeeded, some failed
- **Failed**: All agents failed

Individual data objects contain an `error` field when their agent failed.

## Performance

### Parallel Execution

All Stage 1 agents run in parallel using ThreadPoolExecutor:

**Typical Execution Times** (4 stocks, all 5 agents):
- Sequential: ~25-30s
- Parallel (5 workers): ~7-10s
- **Speedup**: ~3x faster

## Next Steps

After Stage 1 retrieves heterogeneous data:

1. **Stage 2** ✅ Implemented: Normalize and standardize data, compute quality scores per symbol
2. **Stage 3** ✅ Implemented: Extract structured features using LLM (Mistral/vLLM) for trading signals

## See Also

- [Multi-Agent Architecture](../architecture/multi-agent-architecture.md)
- [Data Sources](./data-sources.md)
- [Usage Guide](./usage.md)
