# Layer 1 Quick Start Guide

Get started with Event Horizon Layer 1 data retrieval in 5 minutes.

## Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys:
# - NEWS_API_KEY (optional, for news data)
```

## 1. Basic Usage (30 seconds)

```python
from layer_1 import Layer1Orchestrator

# Create orchestrator
orchestrator = Layer1Orchestrator()

# Retrieve data for stocks
result = orchestrator.execute(["AAPL", "TSLA", "SPY"])

# Access results
layer1_output = result["layer1_output"]
print(f"Status: {result['status']}")
print(f"Execution time: {result['execution_time_seconds']:.2f}s")

# View data for each stock
for symbol, chart_data in layer1_output.chart_data.items():
    print(f"{symbol}: {len(chart_data.candles)} candles")
```

## 2. Run the Example (1 minute)

```bash
# Run the Layer 1 demo
python main_layer1.py
```

Expected output:
```
======================================================================
 EVENT HORIZON - LAYER 1 DATA RETRIEVAL
======================================================================

Test Portfolio:
  ID: layer1_test_001
  Symbols: AAPL, TSLA, SPY, NVDA

Enabled Agents: candlestick, earnings, news

======================================================================
 EXECUTING LAYER 1 DATA RETRIEVAL
======================================================================

🔄 Running Layer 1 agents in parallel...
✓ candlestick completed: success
✓ earnings completed: success
✓ news completed: success

======================================================================
 LAYER 1 DATA RETRIEVAL RESULTS
======================================================================

Status: SUCCESS
Execution Time: 7.12s
Agents Executed: candlestick, earnings, news

📰 News Data: 4 symbols, 28 articles
📊 Earnings Data: 4 symbols
📈 Chart Data: 4 symbols

💾 Results saved: layer1_output_20260125_153045.json
```

## 3. Custom Configuration (2 minutes)

```python
from layer_1 import Layer1Orchestrator

# Configure Layer 1
config = {
    # Choose which agents to run
    "enabled_agents": ["candlestick", "earnings", "news"],

    # Control parallelism
    "max_workers": 3,

    # Per-agent configuration
    "agent_configs": {
        "candlestick": {
            "period": "3mo",      # Last 3 months
            "interval": "1d"      # Daily candles
        },
        "earnings": {
            "include_financials": True,
            "earnings_periods": 4  # Last 4 quarters
        },
        "news": {
            "max_articles_per_stock": 20,
            "days_back": 14       # Last 2 weeks
        }
    }
}

# Create orchestrator with config
orchestrator = Layer1Orchestrator(config=config)

# Execute
portfolio = {
    "portfolio_id": "my_portfolio",
    "portfolio": ["NVDA", "AMD", "INTC"]
}

result = orchestrator.execute(portfolio)
```

## 4. Access Different Data Types (1 minute)

```python
result = orchestrator.execute(["AAPL"])
layer1_output = result["layer1_output"]

# Chart/Candlestick Data
chart = layer1_output.chart_data["AAPL"]
print(f"Candles: {len(chart.candles)}")
for candle in chart.candles[:3]:
    print(f"  {candle['date']}: ${candle['close']}")

# Earnings/Financial Data
earnings = layer1_output.earnings_data["AAPL"]
print(f"Company: {earnings.name}")
print(f"Type: {earnings.security_type}")
if earnings.earnings_reports:
    print(f"Latest EPS: {earnings.earnings_reports['quarterly'][0]['eps']}")

# News Data
news = layer1_output.news_data["AAPL"]
print(f"Articles: {news.total_articles}")
for article in news.articles[:3]:
    print(f"  - {article['title']}")
```

## 5. Error Handling (30 seconds)

```python
result = orchestrator.execute(["AAPL", "INVALID_SYMBOL"])

# Check overall status
if result["status"] == "partial_success":
    print("Some data retrieved successfully")

# Check individual symbol errors
for symbol, data in result["layer1_output"].chart_data.items():
    if data.error:
        print(f"❌ {symbol}: {data.error}")
    else:
        print(f"✓ {symbol}: {len(data.candles)} candles")

# View all errors
for error in result["errors"]:
    print(f"Error in {error['agent']}: {error['symbol']} - {error['error']}")
```

## What You Get

### Data Types

Layer 1 retrieves three types of heterogeneous data:

1. **Chart Data (OHLCV)**
   - Open, High, Low, Close, Volume
   - Configurable time period and interval
   - Source: Yahoo Finance or Massive.com

2. **Earnings Data**
   - Quarterly/annual earnings
   - Financial statements
   - Key metrics (P/E, market cap, etc.)
   - Source: Yahoo Finance

3. **News Data**
   - Recent news articles
   - Headlines and descriptions
   - Publication dates and sources
   - Source: NewsAPI

### Output Format

```python
Layer1Output(
    portfolio_id="my_portfolio",
    symbols=["AAPL", "TSLA"],

    # Data by symbol
    chart_data={
        "AAPL": ChartData(...),
        "TSLA": ChartData(...)
    },
    earnings_data={
        "AAPL": EarningsData(...),
        "TSLA": EarningsData(...)
    },
    news_data={
        "AAPL": NewsData(...),
        "TSLA": NewsData(...)
    },

    # Metadata
    execution_time_seconds=7.12,
    agents_executed=["candlestick", "earnings", "news"],
    status="success"
)
```

## Performance

- **Parallel Execution**: All agents run simultaneously
- **Speed**: ~2x faster than sequential execution
- **Typical Time**: 5-10s for 4 stocks with 3 agents

## Next Steps

### Learn More
- [Layer 1 Guide](docs/guides/layer-1-guide.md) - Comprehensive documentation
- [Layer 1 Architecture](docs/architecture/layer-1-architecture.md) - Technical details
- [Migration Guide](docs/guides/migration-to-layer1.md) - Migrating from old system

### Customize
- Add more stocks to your portfolio
- Enable/disable specific agents
- Adjust time periods and intervals
- Change article count and date ranges

### Extend
- Add new data sources
- Create custom agents
- Build on top of Layer 1 output
- Prepare for Layer 2 (normalization)

## Common Tasks

### Save Results to File

```python
import json

result = orchestrator.execute(["AAPL"])
layer1_output = result["layer1_output"]

# Convert to dict
output_dict = layer1_output.to_dict()

# Save as JSON
with open("layer1_output.json", "w") as f:
    json.dump(output_dict, f, indent=2, default=str)
```

### Only Fetch Specific Data

```python
# Only candlestick data (no earnings or news)
config = {
    "enabled_agents": ["candlestick"],
    "agent_configs": {
        "candlestick": {"period": "1y", "interval": "1d"}
    }
}

orchestrator = Layer1Orchestrator(config=config)
result = orchestrator.execute(["SPY"])
```

### Use Massive.com Instead of Yahoo Finance

```python
config = {
    "enabled_agents": ["candlestick"],
    "agent_configs": {
        "candlestick": {
            "period": "1mo",
            "interval": "1d",
            "data_source": "massive"  # Use Massive.com API
        }
    }
}

# Also set environment variable
# export USE_MASSIVE_API=true
```

## Troubleshooting

### Agent Not Running

**Problem**: Specific agent doesn't execute

**Solution**: Check enabled_agents list
```python
config = {
    "enabled_agents": ["candlestick", "earnings", "news"],  # Include all you need
}
```

### Missing News Data

**Problem**: News agent returns empty results

**Solution**: Set NEWS_API_KEY environment variable
```bash
export NEWS_API_KEY=your_newsapi_key
```

### Slow Execution

**Problem**: Takes longer than expected

**Solution**: Reduce time periods or article counts
```python
config = {
    "agent_configs": {
        "candlestick": {"period": "1mo"},  # Smaller period
        "news": {"max_articles_per_stock": 5}  # Fewer articles
    }
}
```

## Architecture Overview

```
Your Code
    ↓
Layer1Orchestrator
    ↓
├─ CandlestickAgent → ChartService → Yahoo/Massive API
├─ EarningsAgent    → FinancialService → Yahoo API
└─ NewsAgent        → NewsService → NewsAPI
    ↓
Layer1Output (with all data)
```

## Complete Example

```python
from layer_1 import Layer1Orchestrator

# 1. Configure
config = {
    "enabled_agents": ["candlestick", "earnings", "news"],
    "max_workers": 3,
    "agent_configs": {
        "candlestick": {"period": "1mo", "interval": "1d"},
        "earnings": {"include_financials": True},
        "news": {"max_articles_per_stock": 10, "days_back": 7}
    }
}

# 2. Create orchestrator
orchestrator = Layer1Orchestrator(config=config)

# 3. Execute
portfolio = ["AAPL", "TSLA", "SPY", "NVDA"]
result = orchestrator.execute(portfolio)

# 4. Check status
print(f"Status: {result['status']}")
print(f"Time: {result['execution_time_seconds']:.2f}s")

# 5. Access data
layer1_output = result["layer1_output"]
for symbol in portfolio:
    print(f"\n{symbol}:")
    print(f"  Candles: {len(layer1_output.chart_data[symbol].candles)}")
    print(f"  Articles: {layer1_output.news_data[symbol].total_articles}")
    print(f"  Company: {layer1_output.earnings_data[symbol].name}")

# 6. Save results
import json
with open("output.json", "w") as f:
    json.dump(layer1_output.to_dict(), f, indent=2, default=str)
```

## Ready to Build?

Layer 1 provides the foundation for Event Horizon's three-layer architecture:

- ✅ **Layer 1**: Data Retrieval (You are here!)
- 📋 **Layer 2**: Normalization (Future)
- 📋 **Layer 3**: Feature Extraction (Future)

Start building your trading algorithms on top of Layer 1's structured data!

---

**Need Help?** See [docs/guides/layer-1-guide.md](docs/guides/layer-1-guide.md) for detailed documentation.
