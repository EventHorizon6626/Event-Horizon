# Stage 1: Data Retrieval Guide

## Overview

Stage 1 is the foundation of Event Horizon's three-stage architecture. It handles **heterogeneous data collection** from multiple sources, with each agent specializing in one data source.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STAGE 1: DATA RETRIEVAL                         │
│                     (Heterogeneous Data Collection)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ Candlestick  │  │   Earnings   │  │     News     │                 │
│  │    Agent     │  │    Agent     │  │    Agent     │                 │
│  │              │  │              │  │              │                 │
│  │  OHLCV Data  │  │  Financials  │  │   Articles   │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│                                                                         │
│                   Parallel, Independent Execution                       │
│                              ↓  ↓  ↓                                    │
│                                                                         │
│              Stage1Output (Heterogeneous Data)                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Principles

1. **Specialization**: Each agent retrieves data from ONE source only
2. **Independence**: Agents have no dependencies on each other
3. **Parallel Execution**: All agents run simultaneously for maximum speed
4. **Raw Output**: Data is kept in agent-specific formats (no normalization yet)

## Components

### Stage 1 Orchestrator

Manages parallel execution of all data retrieval agents.

**Location**: `stage_1/orchestrator/stage_1_orchestrator.py`

**Features**:
- Parallel agent execution using ThreadPoolExecutor
- Error handling and partial failure support
- Unified output aggregation
- Configurable agent selection

### Data Retrieval Agents

#### 1. Candlestick Agent

**Purpose**: Retrieve OHLCV (Open, High, Low, Close, Volume) price data

**Data Sources**:
- Yahoo Finance (default)
- Massive.com API (optional)

**Configuration**:
```python
{
    "period": "1mo",      # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max
    "interval": "1d",     # 1m, 5m, 15m, 1h, 1d, 1wk, 1mo
    "data_source": "yahoo"  # "yahoo" or "massive"
}
```

**Output Schema**:
```python
ChartData(
    symbol: str,
    candles: List[Dict],  # [{timestamp, open, high, low, close, volume}]
    period: str,
    interval: str,
    data_source: str,
    retrieved_at: str,
    error: Optional[str]
)
```

#### 2. Earnings Agent

**Purpose**: Retrieve earnings reports and financial statements

**Data Sources**:
- Yahoo Finance
- Financial data APIs

**Configuration**:
```python
{
    "include_financials": True,
    "earnings_periods": 4,  # Number of quarters
    "top_holdings": 10      # For ETFs
}
```

**Output Schema**:
```python
EarningsData(
    symbol: str,
    security_type: str,  # stock, etf, mutual_fund
    name: str,
    earnings_reports: Dict,
    financial_statements: Dict,
    metrics: Dict,
    fund_info: Dict,  # For ETFs
    data_source: str,
    retrieved_at: str,
    error: Optional[str]
)
```

#### 3. News Agent

**Purpose**: Retrieve news articles and headlines

**Data Sources**:
- NewsAPI
- Financial news providers

**Configuration**:
```python
{
    "max_articles_per_stock": 20,
    "days_back": 7,
    "language": "en"
}
```

**Output Schema**:
```python
NewsData(
    symbol: str,
    articles: List[Dict],  # [{title, source, url, published_at, ...}]
    total_articles: int,
    data_source: str,
    retrieved_at: str,
    error: Optional[str]
)
```

## Usage

### Basic Usage

```python
from stage_1 import Stage1Orchestrator

# Configure orchestrator
config = {
    "enabled_agents": ["candlestick", "earnings", "news"],
    "max_workers": 3,
    "agent_configs": {
        "candlestick": {"period": "1mo", "interval": "1d"},
        "earnings": {"include_financials": True},
        "news": {"max_articles_per_stock": 10, "days_back": 7}
    }
}

# Initialize orchestrator
orchestrator = Stage1Orchestrator(config=config)

# Execute data retrieval
portfolio = {
    "portfolio_id": "my_portfolio",
    "portfolio": ["AAPL", "TSLA", "SPY"]
}

result = orchestrator.execute(portfolio)

# Access results
stage1_output = result["stage1_output"]
print(f"Status: {result['status']}")
print(f"Execution time: {result['execution_time_seconds']:.2f}s")

# Access specific data
for symbol, chart_data in stage1_output.chart_data.items():
    print(f"{symbol}: {len(chart_data.candles)} candles")
```

### Running the Example Script

```bash
# Set environment variables
export NEWS_API_KEY=your_newsapi_key

# Run Stage 1 example
python main_stage1.py
```

## Output Format

### Stage1Output

The complete output from Stage 1 execution:

```python
Stage1Output(
    portfolio_id: str,
    symbols: List[str],

    # Data by agent type
    news_data: Dict[str, NewsData],
    earnings_data: Dict[str, EarningsData],
    chart_data: Dict[str, ChartData],
    options_data: Dict[str, OptionsFlowData],  # Future
    social_data: Dict[str, SocialMediaData],   # Future
    sec_data: Dict[str, SECFilingsData],       # Future

    # Metadata
    execution_time_seconds: float,
    agents_executed: List[str],
    timestamp: str,
    status: str,  # success, partial_success, failed
    errors: List[Dict]
)
```

### Saving Results

```python
import json

# Convert to dict
output_dict = result["stage1_output"].to_dict()

# Save to file
with open("stage1_output.json", "w") as f:
    json.dump(output_dict, f, indent=2, default=str)
```

## Error Handling

Stage 1 supports partial failures:

- **Success**: All agents completed successfully
- **Partial Success**: Some agents succeeded, some failed
- **Failed**: All agents failed

```python
result = orchestrator.execute(portfolio)

if result["status"] == "failed":
    print("All agents failed!")
    for error in result["errors"]:
        print(f"  {error['agent']}: {error['error']}")

elif result["status"] == "partial_success":
    print("Some agents failed:")
    for error in result["errors"]:
        print(f"  {error['agent']}: {error['error']}")
```

## Performance

### Parallel Execution

All Stage 1 agents run in parallel using ThreadPoolExecutor:

```python
# Sequential (old way): 15s total
# - Candlestick: 5s
# - Earnings: 7s
# - News: 3s

# Parallel (Stage 1): 7s total (max of individual times)
# All agents run simultaneously
```

### Configuration

Adjust parallelism with `max_workers`:

```python
config = {
    "max_workers": 5,  # Max number of concurrent agents
    "enabled_agents": ["candlestick", "earnings", "news"]
}
```

## Adding New Agents

### Step 1: Create Agent Class

Create a new agent in `stage_1/agents/`:

```python
from stage_1.agents.base_agent import BaseAgent
from stage_1.models.schemas import OptionsFlowData

class OptionsFlowAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__("options_flow_agent", config)
        # Initialize client

    def _execute_internal(self, input_data):
        # Fetch options data
        # Return structured result
        pass
```

### Step 2: Add Output Schema

Add schema to `stage_1/models/schemas.py`:

```python
@dataclass
class OptionsFlowData:
    symbol: str
    options_chain: Dict
    large_trades: List[Dict]
    # ... other fields
```

### Step 3: Update Orchestrator

Register in `stage_1/orchestrator/stage_1_orchestrator.py`:

```python
def _execute_single_agent(self, agent_name, input_data):
    if agent_name == "options_flow":
        agent = OptionsFlowAgent(config=agent_config)
    # ... other agents
```

### Step 4: Enable in Config

```python
config = {
    "enabled_agents": ["candlestick", "earnings", "news", "options_flow"],
    "agent_configs": {
        "options_flow": {
            "include_greeks": True
        }
    }
}
```

## Next Steps

After Stage 1 retrieves heterogeneous data:

1. **Stage 2** (Future): Normalize and standardize data into unified "DNA" schema
2. **Stage 3** (Future): Extract features using LLM/Neural AI for trading signals

## Troubleshooting

### Agent Timeouts

Increase timeout in agent configuration:

```python
{
    "timeout_seconds": 30  # Per agent
}
```

### API Rate Limits

Stage 1 respects rate limits through service clients. Configure in services:

```python
# In services/news_api_client.py
rate_limit = RateLimiter(calls=100, period=60)
```

### Missing Data

Check individual agent errors:

```python
for symbol, data in stage1_output.chart_data.items():
    if data.error:
        print(f"{symbol} failed: {data.error}")
```

## Best Practices

1. **Enable only needed agents**: Don't fetch data you won't use
2. **Use appropriate time windows**: Smaller periods = faster retrieval
3. **Handle partial failures**: Stage 1 continues even if some agents fail
4. **Cache results**: Save Stage1Output to avoid redundant API calls
5. **Monitor execution time**: Track agent performance over time

## See Also

- [Multi-Agent Design Architecture](../architecture/multi-agent-design.md)
- [Configuration Guide](./configuration.md)
- [Data Sources](./data-sources.md)
