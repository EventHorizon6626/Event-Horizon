# Tauric Research Integration - Layer 1 Data Retrieval

This document describes the integration of **data retrieval patterns** from Tauric Research's TradingAgents framework into Event Horizon's Layer 1.

## Overview

Event Horizon Layer 1 has been enhanced with **data tools** inspired by the [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) framework.

**Important**: Layer 1 is **ONLY** for data retrieval (market data, news, fundamentals, technicals, etc.). The Tauric analyst/researcher/trader/risk management multi-agent system will be implemented separately as described in `docs/architecture/multi-agent-design-for-analyzer-researcher-trader-riskmgmt.md`.

## What Was Added

### 1. New Agents

#### Technical Indicators Agent
- **Location**: `layer_1/agents/technical_agent.py`
- **Purpose**: Calculate technical indicators for stocks
- **Indicators**: SMA, EMA, RSI, MACD
- **Data Source**: Yahoo Finance via yfinance
- **Inspired by**: Tauric's `technical_indicators_tools.py`

#### Fundamentals Analysis Agent
- **Location**: `layer_1/agents/fundamentals_agent.py`
- **Purpose**: Retrieve fundamental metrics and financial ratios
- **Metrics**: P/E, ROE, ROA, Debt/Equity, Profit Margins, etc.
- **Data Source**: Yahoo Finance via yfinance
- **Inspired by**: Tauric's `fundamental_data_tools.py`

### 2. Utility Tools

#### Stock Data Tools
- **Location**: `layer_1/agents/utils/stock_tools.py`
- **Functions**:
  - `get_stock_data()`: Retrieve OHLCV data for date ranges
  - `get_indicators()`: Calculate technical indicators
  - `get_fundamentals()`: Retrieve fundamental metrics
- **Inspired by**: Tauric's utility tool modules

### 3. Updated Schemas

Added new data models in `layer_1/models/schemas.py`:
- `TechnicalData`: Schema for technical indicator outputs
- `FundamentalsData`: Schema for fundamental metrics outputs

### 4. Enhanced Orchestrator

Updated `layer_1/orchestrator/layer_1_orchestrator.py`:
- Support for `technical` and `fundamentals` agents
- Parallel execution of all 5 agents
- Aggregation of new data types into `Layer1Output`

## Key Differences

### Event Horizon Approach (Our Architecture)
- **Pattern**: Orchestrator-based with parallel execution
- **Focus**: Modular, independent agents for data retrieval
- **Philosophy**: Clean separation of data sources
- **Execution**: ThreadPoolExecutor for parallelism

### Tauric Approach
- **Pattern**: LangGraph-based with LangChain tools
- **Focus**: LLM-powered agents with tool calling
- **Philosophy**: Agents as reasoning entities
- **Execution**: LangGraph workflow with state management

### Our Integration
We've taken the **best of both worlds**:
- ✅ Keep our clean orchestrator pattern
- ✅ Add Tauric's comprehensive data tools
- ✅ Maintain independent, testable agents
- ✅ Expand coverage to technical & fundamental analysis

## Architecture Comparison

### Tauric's Multi-Agent System
```
TradingAgentsGraph
  ├─ Analyst Team (market, news, fundamentals, social)
  ├─ Researcher Team (bull/bear debate)
  ├─ Trader Agent
  └─ Risk Management Team
```

### Event Horizon Layer 1 (Enhanced)
```
Layer1Orchestrator
  ├─ CandlestickAgent (OHLCV data)
  ├─ EarningsAgent (financial reports)
  ├─ NewsAgent (news articles)
  ├─ TechnicalAgent (technical indicators) ← Tauric-inspired
  └─ FundamentalsAgent (fundamental metrics) ← Tauric-inspired
```

## Usage Example

```python
from layer_1 import Layer1Orchestrator

# Configure with all agents including Tauric-inspired ones
config = {
    "enabled_agents": ["candlestick", "earnings", "news", "technical", "fundamentals"],
    "max_workers": 5,
    "agent_configs": {
        "candlestick": {"period": "1mo", "interval": "1d"},
        "earnings": {"include_financials": True},
        "news": {"max_articles_per_stock": 10, "days_back": 7},
        "technical": {
            "indicators": ["SMA", "RSI", "MACD"],
            "look_back_days": 30
        },
        "fundamentals": {
            "include_ratios": True,
            "include_financials": True
        }
    }
}

orchestrator = Layer1Orchestrator(config=config)
result = orchestrator.execute(["AAPL", "TSLA", "NVDA"])

# Access all data types
layer1_output = result["layer1_output"]
print(layer1_output.chart_data)        # OHLCV candles
print(layer1_output.technical_data)    # Technical indicators
print(layer1_output.fundamentals_data) # Fundamental metrics
```

## Benefits of Integration

1. **Comprehensive Data**: Layer 1 now retrieves all data types needed for analysis
2. **Proven Patterns**: Leverages Tauric's battle-tested data tools
3. **Modularity**: Maintains our clean agent architecture
4. **Extensibility**: Easy to add more Tauric-inspired agents
5. **Compatibility**: Works with existing Layer 1 code

## Future Enhancements

Potential additions from Tauric:
- Social media sentiment tools (Reddit, Twitter)
- Insider trading data
- Global macroeconomic news
- Advanced indicator calculations
- Balance sheet/cash flow detailed analysis

## Reference

- **Tauric Repository**: https://github.com/TauricResearch/TradingAgents
- **Paper**: [TradingAgents: Multi-Agents LLM Financial Trading Framework](https://arxiv.org/abs/2412.20138)
- **Cloned to**: `core_refs/TradingAgents/`

## What's NOT in Layer 1

The following Tauric components are **NOT** part of Layer 1 and will be implemented in a separate Financial Analysis Multi-Agent System:

### Not Included (Future Implementation)
- ❌ Analyst Agents (fundamentals_analyst, market_analyst, news_analyst, social_media_analyst)
- ❌ Researcher Team (bull_researcher, bear_researcher, research_manager)
- ❌ Risk Management Team (conservative/neutral/aggressive debators, risk_manager)
- ❌ Trader Agent
- ❌ LangGraph workflow orchestration
- ❌ Multi-agent debate and consensus mechanisms

These will be built as a **separate system** that consumes the output from Layer 3 (feature-extracted data). See `docs/architecture/multi-agent-design-for-analyzer-researcher-trader-riskmgmt.md` for details.

### Clear Separation

```
┌─────────────────────────────────────────────────────────────┐
│           DATA PROCESSING PIPELINE (This Layer)            │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Data Retrieval (candlestick, news, technical)   │
│  Layer 2: Normalization                                    │
│  Layer 3: Feature Extraction                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│        FINANCIAL ANALYSIS MULTI-AGENT SYSTEM (Future)      │
├─────────────────────────────────────────────────────────────┤
│  Analyst Team → Researcher Team → Risk Mgmt → Trader       │
└─────────────────────────────────────────────────────────────┘
```

Layer 1's job: **Get the data**
Financial Analysis System's job: **Make trading decisions**

## Credits

This integration was inspired by and references the excellent work from:
- Tauric Research (https://tauric.ai/)
- TradingAgents Framework by Yijia Xiao, Edward Sun, Di Luo, Wei Wang
