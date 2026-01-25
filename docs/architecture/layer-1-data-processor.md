# Layer 1: Data Retrieval Architecture

**Status**: ✅ Implemented
**Last Updated**: 2026-01-25

This document describes Layer 1 of Event Horizon's three-layer data processing pipeline. Layer 1 is responsible for **heterogeneous data retrieval** from multiple external sources.

---

## Quick Links

- 📚 [Quick Start Guide](../../QUICKSTART_LAYER1.md)
- 🔧 [Tauric Integration Details](../../layer_1/TAURIC_INTEGRATION.md)
- 📝 [Update Summary](../../LAYER1_UPDATE_SUMMARY.md)
- 🤖 [Financial Analysis System (Future)](./multi-agent-design-for-analyzer-researcher-trader-riskmgmt.md)

---

## Table of Contents

1. [Overview & Position](#overview--position)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Layers](#component-layers)
4. [Implemented Agents (5 Total)](#implemented-agents)
5. [Data Flow](#data-flow)
6. [Tauric Research Integration](#tauric-research-integration)
7. [Usage Examples](#usage-examples)
8. [Adding New Agents](#adding-new-agents)

---

## Overview & Position

### Three-Layer Data Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LAYER 1: DATA RETRIEVAL ✅                            │
│                  (Heterogeneous Data Collection)                        │
├─────────────────────────────────────────────────────────────────────────┤
│  5 Agents Running in Parallel:                                         │
│  1. Candlestick Agent → OHLCV price data                                │
│  2. Earnings Agent    → Financial reports                               │
│  3. News Agent        → News articles                                   │
│  4. Technical Agent   → Technical indicators (SMA/RSI/MACD)            │
│  5. Fundamentals Agent → Fundamental metrics (P/E/ROE/etc.)            │
│                                                                         │
│  Output: Raw, heterogeneous data in agent-specific formats             │
└─────────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│              LAYER 2: NORMALIZATION & STANDARDIZATION ⏳                 │
│                  (Create Unified "DNA" Dataset)                         │
├─────────────────────────────────────────────────────────────────────────┤
│  • Time synchronization across data sources                            │
│  • Symbol mapping and normalization                                    │
│  • Format standardization to tabular schema                            │
│                                                                         │
│  Output: Standardized tabular "DNA" dataset                            │
└─────────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                  LAYER 3: FEATURE EXTRACTION ⏳                          │
│          (LLM/Neural AI - Intelligent Feature Discovery)                │
├─────────────────────────────────────────────────────────────────────────┤
│  • Extract non-obvious patterns from normalized data                   │
│  • Generate embeddings and latent features                             │
│  • Identify predictive signals for trading                             │
│                                                                         │
│  Output: Feature vectors ready for trading decisions                   │
└─────────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│          FINANCIAL ANALYSIS MULTI-AGENT SYSTEM ⏳                        │
│        (Analyst → Researcher → Risk Mgmt → Trader)                      │
├─────────────────────────────────────────────────────────────────────────┤
│  Separate system that consumes Layer 3 output                          │
│  See: multi-agent-design-for-analyzer-researcher-trader-riskmgmt.md    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Legend**: ✅ = Implemented, ⏳ = Planned

---

## Architecture Diagram

### Complete Layer 1 System

```
┌────────────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                                  │
│                      main_layer1.py                                     │
│  • Configuration setup                                                 │
│  • Result display                                                      │
│  • Output persistence                                                  │
└────────────────────────────────────────────────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                                  │
│               layer_1/orchestrator/layer_1_orchestrator.py             │
│                                                                         │
│  Layer1Orchestrator:                                                   │
│  • Parallel execution (ThreadPoolExecutor, 5 workers)                  │
│  • Agent lifecycle management                                          │
│  • Result aggregation into Layer1Output                                │
│  • Error handling and status tracking                                  │
└────────────────────────────────────────────────────────────────────────┘
      │            │           │           │           │
      ▼            ▼           ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Candlestick│ │ Earnings │ │   News   │ │Technical │ │Fundament-│
│  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │ │als Agent │
│          │ │          │ │          │ │          │ │          │
│OHLCV data│ │Financial │ │Articles &│ │SMA, RSI, │ │P/E, ROE, │
│          │ │ reports  │ │headlines │ │MACD      │ │ratios    │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
      │            │           │           │           │
      ▼            ▼           ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  Chart   │ │Financial │ │   News   │ │  Stock   │ │  Stock   │
│ Service  │ │ Service  │ │ Service  │ │  Tools   │ │  Tools   │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
      │            │           │           │           │
      ▼            ▼           ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  Yahoo   │ │  Yahoo   │ │ NewsAPI  │ │ yfinance │ │ yfinance │
│ Finance  │ │ Finance  │ │          │ │          │ │          │
│Massive.com│ │          │ │          │ │          │ │          │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

---

## Component Layers

### Directory Structure

```
layer_1/
├── __init__.py                 # Layer 1 exports
├── agents/                     # Data retrieval agents
│   ├── __init__.py
│   ├── candlestick_agent.py   # OHLCV price data
│   ├── earnings_agent.py      # Financial reports
│   ├── news_agent.py          # News articles
│   ├── technical_agent.py     # Technical indicators (Tauric)
│   ├── fundamentals_agent.py  # Fundamental metrics (Tauric)
│   └── utils/
│       └── stock_tools.py     # Utility functions (Tauric)
├── services/                   # API client layer
│   ├── __init__.py
│   ├── chart_data_client.py   # Yahoo Finance charts
│   ├── massive_chart_client.py # Massive.com alternative
│   ├── financial_data_client.py # Yahoo Finance fundamentals
│   └── news_api_client.py     # NewsAPI client
├── models/                     # Data schemas
│   ├── __init__.py
│   └── schemas.py             # Layer1Output and data classes
├── orchestrator/               # Parallel execution
│   ├── __init__.py
│   └── layer_1_orchestrator.py # Layer1Orchestrator class
└── TAURIC_INTEGRATION.md      # Integration details
```

---

## Implemented Agents

### 1. Candlestick Agent ✅

**Purpose**: Retrieve OHLCV (Open, High, Low, Close, Volume) price data

**File**: `layer_1/agents/candlestick_agent.py`

**Data Sources**:
- Primary: Yahoo Finance
- Alternative: Massive.com API

**Configuration**:
```python
{
    "period": "1mo",        # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max
    "interval": "1d",       # 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
    "data_source": "yahoo"  # or "massive"
}
```

**Output**: `ChartData`
- `symbol`, `candles`, `period`, `interval`, `data_source`, `error`

---

### 2. Earnings Agent ✅

**Purpose**: Retrieve financial reports and earnings data

**File**: `layer_1/agents/earnings_agent.py`

**Data Source**: Yahoo Finance

**Configuration**:
```python
{
    "include_financials": True,
    "earnings_periods": 4  # Number of quarters
}
```

**Output**: `EarningsData`
- `symbol`, `security_type`, `name`, `earnings_reports`, `financial_statements`, `metrics`, `error`

---

### 3. News Agent ✅

**Purpose**: Retrieve news articles about stocks

**File**: `layer_1/agents/news_agent.py`

**Data Source**: NewsAPI (requires API key)

**Configuration**:
```python
{
    "max_articles_per_stock": 10,
    "days_back": 7
}
```

**Output**: `NewsData`
- `symbol`, `articles`, `total_articles`, `data_source`, `error`

---

### 4. Technical Agent ✅ (Tauric-Inspired)

**Purpose**: Calculate technical indicators

**File**: `layer_1/agents/technical_agent.py`

**Data Source**: Yahoo Finance via yfinance

**Configuration**:
```python
{
    "indicators": ["SMA", "EMA", "RSI", "MACD"],
    "look_back_days": 30
}
```

**Supported Indicators**:
- **SMA** - Simple Moving Average (20/50 day)
- **EMA** - Exponential Moving Average (12/26 day)
- **RSI** - Relative Strength Index (14 period)
- **MACD** - Moving Average Convergence Divergence

**Output**: `TechnicalData`
- `symbol`, `indicators`, `trade_date`, `look_back_days`, `data_source`, `error`

---

### 5. Fundamentals Agent ✅ (Tauric-Inspired)

**Purpose**: Retrieve fundamental metrics and financial ratios

**File**: `layer_1/agents/fundamentals_agent.py`

**Data Source**: Yahoo Finance via yfinance

**Configuration**:
```python
{
    "include_ratios": True,
    "include_financials": True
}
```

**Metrics Retrieved**:
- **Valuation**: P/E, Forward P/E, PEG, Price/Book, Price/Sales
- **Profitability**: Profit margin, operating margin, ROE, ROA
- **Financial Health**: Total cash/debt, current ratio, debt/equity
- **Growth**: Revenue growth, earnings growth
- **Dividends**: Dividend yield, payout ratio

**Output**: `FundamentalsData`
- `symbol`, `fundamentals_text`, `data_source`, `error`

---

## Data Flow

### Step-by-Step Execution

```python
# 1. User creates orchestrator with config
from layer_1 import Layer1Orchestrator

orchestrator = Layer1Orchestrator(config={
    "enabled_agents": ["candlestick", "earnings", "news", "technical", "fundamentals"],
    "max_workers": 5
})

# 2. User executes with portfolio
result = orchestrator.execute(["AAPL", "TSLA", "NVDA"])

# 3. Orchestrator coordinates parallel execution
#    - Spawns 5 workers in ThreadPoolExecutor
#    - Each agent fetches data independently
#    - No cross-agent dependencies

# 4. Agents return results
#    - candlestick → chart_data_by_symbol
#    - earnings → earnings_data_by_symbol
#    - news → news_data_by_symbol
#    - technical → technical_data_by_symbol
#    - fundamentals → fundamentals_data_by_symbol

# 5. Orchestrator aggregates into Layer1Output
layer1_output = Layer1Output(
    portfolio_id="...",
    symbols=["AAPL", "TSLA", "NVDA"],
    chart_data={...},
    earnings_data={...},
    news_data={...},
    technical_data={...},
    fundamentals_data={...},
    execution_time_seconds=7.5,
    agents_executed=["candlestick", "earnings", "news", "technical", "fundamentals"],
    status="success"
)

# 6. User accesses heterogeneous data
print(layer1_output.chart_data["AAPL"].candles)
print(layer1_output.technical_data["AAPL"].indicators["RSI"])
print(layer1_output.fundamentals_data["AAPL"].fundamentals_text)
```

---

## Tauric Research Integration

Layer 1 integrates **data tools** from [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents).

### What We Integrated ✅

- ✅ Technical indicator calculation tools
- ✅ Fundamental metrics retrieval patterns
- ✅ Stock data utility functions (`layer_1/agents/utils/stock_tools.py`)
- ✅ Multi-source data collection approach

### What's NOT in Layer 1 ❌

The following Tauric components will be in a **separate Financial Analysis System**:

- ❌ Analyst agents (fundamentals_analyst, market_analyst, news_analyst, social_media_analyst)
- ❌ Researcher team (bull/bear debate, research manager)
- ❌ Risk management team (conservative/neutral/aggressive debators)
- ❌ Trader agent
- ❌ LangGraph workflow orchestration

See `docs/architecture/multi-agent-design-for-analyzer-researcher-trader-riskmgmt.md` for details.

### Clear Separation

```
DATA PROCESSING (Layers 1-3)          DECISION MAKING (Separate System)
├─ Layer 1: Get the data              ├─ Analyst Team: Analyze data
├─ Layer 2: Normalize data            ├─ Researcher Team: Debate thesis
├─ Layer 3: Extract features          ├─ Risk Mgmt: Size positions
                ↓                      └─ Trader: Execute trades
        Feature vectors
```

---

## Usage Examples

### Basic Usage

```python
from layer_1 import Layer1Orchestrator

# Simple config
config = {
    "enabled_agents": ["candlestick", "news", "technical"]
}

orchestrator = Layer1Orchestrator(config=config)
result = orchestrator.execute(["AAPL"])

# Access data
layer1_output = result["layer1_output"]
print(layer1_output.chart_data["AAPL"].candles)
```

### Complete Configuration

```python
config = {
    "enabled_agents": ["candlestick", "earnings", "news", "technical", "fundamentals"],
    "max_workers": 5,
    "agent_configs": {
        "candlestick": {
            "period": "3mo",
            "interval": "1d",
            "data_source": "yahoo"
        },
        "earnings": {
            "include_financials": True,
            "earnings_periods": 4
        },
        "news": {
            "max_articles_per_stock": 20,
            "days_back": 14
        },
        "technical": {
            "indicators": ["SMA", "RSI", "MACD", "EMA"],
            "look_back_days": 60
        },
        "fundamentals": {
            "include_ratios": True,
            "include_financials": True
        }
    }
}

orchestrator = Layer1Orchestrator(config=config)
result = orchestrator.execute({
    "portfolio_id": "tech_stocks",
    "portfolio": ["AAPL", "TSLA", "NVDA", "MSFT"]
})

# Save results
import json
with open("layer1_output.json", "w") as f:
    json.dump(result["layer1_output"].to_dict(), f, indent=2, default=str)
```

### Running the Demo

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env
# Add NEWS_API_KEY to .env

# Run
python main_layer1.py
```

---

## Adding New Agents

### Step 1: Create Agent

`layer_1/agents/your_new_agent.py`:

```python
from core.base import BaseAgent
from layer_1.models.schemas import YourDataSchema

class YourNewAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("your_new_agent", config)
        self.your_config = self.get_config("your_param", "default_value")

    def _execute_internal(self, input_data: Any) -> Dict[str, Any]:
        symbols, portfolio_id = self._parse_input(input_data)

        data_by_symbol = {}
        for symbol in symbols:
            # Fetch data
            data = self._fetch_your_data(symbol)
            data_by_symbol[symbol] = YourDataSchema(...)

        return {
            "status": "success",
            "your_data_by_symbol": data_by_symbol
        }
```

### Step 2: Define Schema

`layer_1/models/schemas.py`:

```python
@dataclass
class YourDataSchema:
    symbol: str
    your_field: Any
    data_source: str = "your_api"
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None

# Update Layer1Output
@dataclass
class Layer1Output:
    # ... existing fields ...
    your_data: Dict[str, YourDataSchema] = field(default_factory=dict)
```

### Step 3: Register in Orchestrator

`layer_1/orchestrator/layer_1_orchestrator.py`:

```python
# Import
from layer_1.agents.your_new_agent import YourNewAgent

# In _execute_single_agent method
elif agent_name == "your_new":
    agent = YourNewAgent(config=agent_config)

# In result aggregation
elif agent_name == "your_new":
    layer1_output.your_data = result.get("your_data_by_symbol", {})

# In set_enabled_agents
valid_agents = [..., "your_new"]
```

### Step 4: Update Exports

`layer_1/agents/__init__.py`:

```python
from layer_1.agents.your_new_agent import YourNewAgent

__all__ = [..., "YourNewAgent"]
```

---

## Performance

**Typical Execution Times** (4 stocks, all 5 agents):
- Sequential: ~25-30s
- Parallel (5 workers): ~7-10s
- **Speedup**: ~3x faster with parallel execution

**Scalability**:
- Handles 10+ symbols efficiently
- ThreadPoolExecutor scales with CPU cores
- Network I/O is the primary bottleneck

---

## References

- **Quick Start**: `QUICKSTART_LAYER1.md`
- **Tauric Integration**: `layer_1/TAURIC_INTEGRATION.md`
- **Update Summary**: `LAYER1_UPDATE_SUMMARY.md`
- **Financial Analysis**: `docs/architecture/multi-agent-design-for-analyzer-researcher-trader-riskmgmt.md`
- **Tauric Codebase**: `core_refs/TradingAgents/`

---

**Status**: ✅ Fully Implemented
**Version**: 1.0.0 (with Tauric integration)
**Last Updated**: 2026-01-25
