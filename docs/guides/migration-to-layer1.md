# Migration Guide: Moving to Layer 1 Architecture

This guide helps you migrate from the old agent system to the new Layer 1 architecture.

## What Changed?

### Old Structure (Before Layer 1)
```
agents/
├── base_agent.py
├── news_agent.py
├── report_agent.py
└── chart_agent.py

main.py - Sequential execution
```

### New Structure (Layer 1)
```
layer_1/
├── agents/
│   ├── base_agent.py
│   ├── news_agent.py
│   ├── earnings_agent.py
│   └── candlestick_agent.py
├── models/
│   └── schemas.py
└── orchestrator/
    └── layer_1_orchestrator.py

main_layer1.py - Parallel execution
```

## Key Improvements

| Feature | Old System | Layer 1 |
|---------|-----------|---------|
| **Execution** | Sequential | Parallel |
| **Speed** | ~15s for 3 agents | ~7s for 3 agents |
| **Architecture** | Monolithic | Layered (3-layer vision) |
| **Data Format** | Mixed | Structured schemas |
| **Error Handling** | All-or-nothing | Partial failures OK |
| **Scalability** | Limited | Designed for 10+ agents |

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
from layer_1.agents import NewsAgent, EarningsAgent, CandlestickAgent
# Or use the orchestrator
from layer_1 import Layer1Orchestrator
```

### Step 2: Replace Sequential Execution

**Before:**
```python
# Sequential - slow
news_agent = NewsAgent(config=news_config)
news_result = news_agent.execute(portfolio)

report_agent = ReportAnalysisAgent(config=report_config)
report_result = report_agent.execute(portfolio)

chart_agent = ChartDataAgent(config=chart_config)
chart_result = chart_agent.execute(portfolio)
```

**After:**
```python
# Parallel - fast
orchestrator = Layer1Orchestrator(config={
    "enabled_agents": ["news", "earnings", "candlestick"],
    "agent_configs": {
        "news": news_config,
        "earnings": report_config,
        "candlestick": chart_config
    }
})

result = orchestrator.execute(portfolio)
layer1_output = result["layer1_output"]
```

### Step 3: Update Agent Names

| Old Name | New Name | Location |
|----------|----------|----------|
| `ChartDataAgent` | `CandlestickAgent` | `layer_1.agents` |
| `ReportAnalysisAgent` | `EarningsAgent` | `layer_1.agents` |
| `NewsAgent` | `NewsAgent` | `layer_1.agents` (same name) |

### Step 4: Update Data Access

**Before:**
```python
# Old format - agent-specific result structure
news_result = news_agent.execute(portfolio)
articles = news_result["result"]["news_by_stock"]

chart_result = chart_agent.execute(portfolio)
candles = chart_result["result"]["chart_data"]
```

**After:**
```python
# New format - unified Layer1Output
result = orchestrator.execute(portfolio)
layer1_output = result["layer1_output"]

# Access by symbol
for symbol in layer1_output.symbols:
    news_data = layer1_output.news_data[symbol]
    chart_data = layer1_output.chart_data[symbol]
    earnings_data = layer1_output.earnings_data[symbol]

    print(f"{symbol}:")
    print(f"  Articles: {news_data.total_articles}")
    print(f"  Candles: {len(chart_data.candles)}")
```

### Step 5: Update Error Handling

**Before:**
```python
try:
    news_result = news_agent.execute(portfolio)
    if news_result["status"] == "failed":
        print(f"Error: {news_result['error']}")
except Exception as e:
    print(f"Failed: {e}")
```

**After:**
```python
result = orchestrator.execute(portfolio)

# Graceful partial failures
if result["status"] == "partial_success":
    print("Some agents succeeded, some failed")

# Check individual data
for symbol, data in result["layer1_output"].news_data.items():
    if data.error:
        print(f"{symbol} news failed: {data.error}")
    else:
        print(f"{symbol}: {data.total_articles} articles")
```

## Backward Compatibility

The old `agents/` directory is maintained for backward compatibility:

```python
# Old code still works
from agents.news_agent import NewsAgent
news_agent = NewsAgent()
result = news_agent.execute(portfolio)
```

However, **new code should use Layer 1** for:
- Better performance (parallel execution)
- Structured data schemas
- Future-proof architecture

## Configuration Changes

### Old Config (config.yaml)

```yaml
agents:
  news_agent:
    enabled: true
    config:
      max_articles_per_stock: 20
      days_back: 7

  report_agent:
    enabled: true
    config:
      include_financials: true
```

### New Config (Layer 1)

```python
layer1_config = {
    "enabled_agents": ["news", "earnings", "candlestick"],
    "max_workers": 3,
    "agent_configs": {
        "news": {
            "max_articles_per_stock": 20,
            "days_back": 7
        },
        "earnings": {
            "include_financials": True
        },
        "candlestick": {
            "period": "1mo",
            "interval": "1d"
        }
    }
}
```

## Running Examples

### Old Way

```bash
# Sequential execution
python main.py
```

### New Way

```bash
# Parallel Layer 1 execution
python main_layer1.py
```

## Common Pitfalls

### 1. Agent Name Confusion

❌ **Wrong:**
```python
from layer_1.agents import ChartDataAgent  # Old name
```

✅ **Correct:**
```python
from layer_1.agents import CandlestickAgent  # New name
```

### 2. Direct Agent Instantiation

❌ **Not Recommended:**
```python
# Still works but doesn't use parallel execution
agent = CandlestickAgent()
result = agent.execute(portfolio)
```

✅ **Recommended:**
```python
# Use orchestrator for parallel execution
orchestrator = Layer1Orchestrator()
result = orchestrator.execute(portfolio)
```

### 3. Result Format Assumptions

❌ **Wrong:**
```python
# Old result format
articles = result["result"]["news_by_stock"]
```

✅ **Correct:**
```python
# New Layer1Output format
layer1_output = result["layer1_output"]
articles = layer1_output.news_data
```

## Performance Comparison

### Benchmark: 4 Stocks, 3 Agents

| Metric | Old System | Layer 1 | Improvement |
|--------|-----------|---------|-------------|
| **Total Time** | 15.2s | 7.1s | **2.1x faster** |
| **News Agent** | 3.1s | 3.1s | Same |
| **Earnings Agent** | 7.2s | 7.1s | Same |
| **Candlestick Agent** | 4.9s | 5.0s | Same |
| **Execution Pattern** | Sequential | Parallel | - |

Time savings come from parallel execution, not individual agent speed.

## Feature Comparison

| Feature | Old System | Layer 1 | Notes |
|---------|-----------|---------|-------|
| Parallel execution | ❌ | ✅ | ThreadPoolExecutor |
| Structured schemas | ❌ | ✅ | Dataclass models |
| Partial failures | ❌ | ✅ | Continue on error |
| Unified output | ❌ | ✅ | Layer1Output |
| Future-ready | ❌ | ✅ | Supports Layer 2/3 |
| Config flexibility | ⚠️ | ✅ | Per-agent config |
| Error tracking | ⚠️ | ✅ | Per-agent, per-symbol |

## Timeline

- **Now**: Both systems work (backward compatible)
- **Recommended**: Start using Layer 1 for new code
- **Future**: Layer 2 and Layer 3 will build on Layer 1

## Need Help?

- See [Layer 1 Guide](./layer-1-guide.md) for detailed documentation
- Check [examples/](../../layer_1/examples/) for sample code
- Review [main_layer1.py](../../main_layer1.py) for working example

## Summary

**To migrate to Layer 1:**

1. Replace `from agents` with `from layer_1.agents`
2. Use `Layer1Orchestrator` instead of sequential agent calls
3. Update result access to use `Layer1Output` structure
4. Rename `ChartDataAgent` → `CandlestickAgent`
5. Rename `ReportAnalysisAgent` → `EarningsAgent`

**Benefits:**
- 2x faster execution (parallel agents)
- Better error handling (partial failures)
- Structured data schemas
- Future-proof for Layer 2 and Layer 3
