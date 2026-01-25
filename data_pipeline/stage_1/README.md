# Layer 1: Data Retrieval

Layer 1 is the foundation of Event Horizon's three-layer architecture, responsible for collecting heterogeneous data from multiple sources.

## Quick Start

```python
from layer_1 import Layer1Orchestrator

# Configure and execute
orchestrator = Layer1Orchestrator(config={
    "enabled_agents": ["candlestick", "earnings", "news"],
    "agent_configs": {
        "candlestick": {"period": "1mo", "interval": "1d"},
        "earnings": {"include_financials": True},
        "news": {"max_articles_per_stock": 10}
    }
})

result = orchestrator.execute(["AAPL", "TSLA", "SPY"])
```

## Directory Structure

```
layer_1/
├── agents/                      # Data retrieval agents
│   ├── base_agent.py           # Base class for all agents
│   ├── candlestick_agent.py    # OHLCV price data
│   ├── earnings_agent.py       # Financial reports
│   └── news_agent.py           # News articles
│
├── models/                      # Data schemas
│   └── schemas.py              # Output data models
│
├── orchestrator/                # Coordination logic
│   └── layer_1_orchestrator.py # Parallel execution manager
│
└── __init__.py
```

## Available Agents

| Agent | Purpose | Data Source | Status |
|-------|---------|-------------|--------|
| **CandlestickAgent** | OHLCV price data | Yahoo Finance, Massive.com | ✅ Active |
| **EarningsAgent** | Financial reports & earnings | Yahoo Finance | ✅ Active |
| **NewsAgent** | News articles & headlines | NewsAPI | ✅ Active |
| OptionsFlowAgent | Options chain & flow | - | 📋 Planned |
| SocialMediaAgent | Social sentiment | Twitter, Reddit | 📋 Planned |
| SECFilingsAgent | SEC filings | EDGAR | 📋 Planned |

## Agent Categories

### Price Data
- **CandlestickAgent**: Open, High, Low, Close, Volume

### Fundamentals
- **EarningsAgent**: Earnings, Balance Sheet, Income Statement, Cash Flow

### News & Media
- **NewsAgent**: Articles, headlines, sentiment raw data

### Market Data (Future)
- **OptionsFlowAgent**: Large trades, unusual activity, Greeks
- **InsiderTradingAgent**: Executive buys/sells

### Alternative Data (Future)
- **SocialMediaAgent**: Twitter, Reddit, social sentiment
- **SECFilingsAgent**: 10-K, 10-Q, 8-K filings

## Key Features

### 1. Parallel Execution
All agents run simultaneously using ThreadPoolExecutor for maximum speed.

```python
# Instead of sequential (15s total):
candlestick (5s) → earnings (7s) → news (3s)

# Parallel execution (7s total):
candlestick (5s) ┐
earnings (7s)    ├─→ Combined output
news (3s)        ┘
```

### 2. Independent Agents
Each agent:
- Specializes in ONE data source
- Has no dependencies on other agents
- Can fail without affecting others

### 3. Heterogeneous Output
Data remains in agent-specific formats:
- No normalization at this layer
- Raw data for maximum flexibility
- Layer 2 handles standardization

### 4. Error Resilience
Supports partial failures:
- Continue execution if some agents fail
- Track errors per agent
- Return partial results

## Usage Examples

### Basic Execution

```python
from layer_1 import Layer1Orchestrator

orchestrator = Layer1Orchestrator()
result = orchestrator.execute(["AAPL", "TSLA"])

# Access data
layer1_output = result["layer1_output"]
print(layer1_output.chart_data["AAPL"])
print(layer1_output.earnings_data["TSLA"])
```

### Custom Configuration

```python
config = {
    "enabled_agents": ["candlestick", "news"],  # Only these agents
    "max_workers": 2,
    "agent_configs": {
        "candlestick": {
            "period": "3mo",
            "interval": "1h",
            "data_source": "massive"  # Use Massive.com
        },
        "news": {
            "max_articles_per_stock": 20,
            "days_back": 14
        }
    }
}

orchestrator = Layer1Orchestrator(config=config)
result = orchestrator.execute({
    "portfolio_id": "my_portfolio",
    "portfolio": ["NVDA", "AMD"]
})
```

### Error Handling

```python
result = orchestrator.execute(["AAPL", "INVALID_SYMBOL"])

if result["status"] == "partial_success":
    print("Some data retrieved, some failed")
    print(f"Errors: {result['errors']}")

# Check individual symbol errors
for symbol, data in result["layer1_output"].chart_data.items():
    if data.error:
        print(f"{symbol} failed: {data.error}")
```

## Output Schema

### Layer1Output

```python
Layer1Output(
    portfolio_id: str,
    symbols: List[str],

    # Data collections (Dict[symbol -> Data])
    chart_data: Dict[str, ChartData],
    earnings_data: Dict[str, EarningsData],
    news_data: Dict[str, NewsData],

    # Metadata
    execution_time_seconds: float,
    agents_executed: List[str],
    status: str,  # success, partial_success, failed
    errors: List[Dict]
)
```

### Data Models

All agent outputs inherit from common base:
```python
@dataclass
class ChartData:
    symbol: str
    candles: List[Dict]  # OHLCV data
    period: str
    interval: str
    data_source: str
    retrieved_at: str
    error: Optional[str]
```

See `models/schemas.py` for complete schemas.

## Performance

### Benchmarks (4 stocks)

| Configuration | Time | Notes |
|--------------|------|-------|
| Sequential | ~15s | Old approach |
| Parallel (3 agents) | ~7s | Layer 1 orchestrator |
| Parallel (5 workers) | ~6s | Increased parallelism |

### Optimization Tips

1. **Disable unused agents**: Only enable what you need
2. **Adjust time windows**: Smaller periods = faster
3. **Increase workers**: For many agents (diminishing returns after 5)
4. **Cache results**: Save Layer1Output to avoid redundant calls

## Integration

### With Main Application

```python
# main.py
from layer_1 import Layer1Orchestrator

orchestrator = Layer1Orchestrator(config=load_config())
layer1_result = orchestrator.execute(portfolio)

# Pass to Layer 2 (future)
layer2_result = normalize_data(layer1_result["layer1_output"])
```

### Standalone Usage

```bash
# Run Layer 1 example script
python main_layer1.py
```

## Development

### Adding a New Agent

1. Create agent class in `agents/`:
```python
from layer_1.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def _execute_internal(self, input_data):
        # Implement data retrieval
        return {"data": ...}
```

2. Add schema in `models/schemas.py`
3. Register in `orchestrator/layer_1_orchestrator.py`
4. Update `__init__.py` exports

See [Layer 1 Guide](../docs/guides/layer-1-guide.md) for detailed instructions.

## Architecture Context

```
Layer 1 (Current)
    ↓
Layer 2 (Future) - Normalization
    ↓
Layer 3 (Future) - Feature Extraction
    ↓
Trading Signals
```

Layer 1 focuses solely on data retrieval. Future layers will handle:
- **Layer 2**: Normalize heterogeneous data into unified "DNA" schema
- **Layer 3**: Extract features using LLM/Neural AI

## Documentation

- [Layer 1 Guide](../docs/guides/layer-1-guide.md) - Comprehensive usage guide
- [Multi-Agent Design](../docs/architecture/multi-agent-design.md) - Architecture overview
- [Core References](../docs/core-refs/README.md) - Research and inspiration

## See Also

- [Services Layer](../services/README.md) - External API clients
- [Configuration Guide](../docs/guides/configuration.md) - Config options
- [Data Sources](../docs/guides/data-sources.md) - Supported APIs
