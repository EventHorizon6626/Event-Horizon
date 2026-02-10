# Event Horizon - Multi-Agent Architecture

**Status**: Data Pipeline Stages 1-3 ✅ Implemented | Bull-Bear Analyzer ✅ Implemented | Remaining Teams ⏳ Planned
**Last Updated**: 2026-02-10

Complete multi-agent architecture for Event Horizon, consisting of:
- **Data Processing Pipeline** (3 stages): Raw data -> Normalized data -> Feature vectors
- **Analyzer System**: Bull-Bear Analyzer (implemented) + planned teams (Analysts, Risk, Trader)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Data Processing Pipeline](#data-processing-pipeline)
   - [Stage 1: Data Retrieval](#stage-1-data-retrieval)
   - [Stage 2: Normalization](#stage-2-normalization)
   - [Stage 3: Feature Extraction](#stage-3-feature-extraction)
3. [Analyzer System](#analyzer-system)
   - [Bull-Bear Analyzer](#bull-bear-analyzer)
   - [Team 1: Analyst Team](#team-1-analyst-team)
   - [Team 3: Risk Management Team](#team-3-risk-management-team)
   - [Team 4: Trader Agent](#team-4-trader-agent)
4. [Thinking Agent System](#thinking-agent-system)
5. [Observability (Opik)](#observability-opik)
6. [Workflow & Communication](#workflow--communication)
7. [Implementation Status](#implementation-status)

---

## System Overview

Event Horizon uses **two separate multi-agent systems** that work together:

### System 1: Data Processing Pipeline
**Purpose**: Transform raw market data into feature vectors
**Stages**: 3 (Data Retrieval -> Normalization -> Feature Extraction)
**Status**: All 3 stages ✅ Implemented

### System 2: Analyzer System
**Purpose**: Make intelligent trading decisions from feature vectors
**Components**: Bull-Bear Analyzer (implemented) + 3 planned teams
**Status**: Bull-Bear Analyzer ✅ Implemented, Teams 1/3/4 ⏳ Planned

### Complete Architecture

```
+=========================================================================+
|                   SYSTEM 1: DATA PROCESSING PIPELINE                      |
+=========================================================================+

+-------------------------------------------------------------------------+
|                   STAGE 1: DATA RETRIEVAL ✅                              |
|                  (Heterogeneous Data Collection)                        |
|-------------------------------------------------------------------------|
|  5 Agents Running in Parallel:                                         |
|  1. Candlestick Agent -> OHLCV price data (Yahoo Finance / Massive)    |
|  2. Earnings Agent    -> Financial reports (Yahoo Finance)              |
|  3. News Agent        -> News articles (Tavily / Exa)                  |
|  4. Technical Agent   -> Technical indicators (SMA/RSI/MACD)           |
|  5. Fundamentals Agent -> Fundamental metrics (P/E/ROE/etc.)           |
|                                                                         |
|  Output: Raw, heterogeneous data in agent-specific formats             |
+-------------------------------------------------------------------------+
                                |
+-------------------------------------------------------------------------+
|             STAGE 2: NORMALIZATION & QUALITY SCORING ✅                   |
|                 (Create Unified Dataset Per Symbol)                      |
|-------------------------------------------------------------------------|
|  * DataNormalizer: unify 6 data categories per symbol                  |
|  * Quality scoring (0-1) based on data completeness                    |
|  * Symbol categorization: complete (>=0.9), partial (>=0.5), error     |
|                                                                         |
|  Output: NormalizedSymbolData with unified structure + quality scores   |
+-------------------------------------------------------------------------+
                                |
+-------------------------------------------------------------------------+
|                  STAGE 3: FEATURE EXTRACTION ✅                           |
|             (LLM-Powered Structured Insight Extraction)                  |
|-------------------------------------------------------------------------|
|  * LLMFeatureExtractor calls Mistral/vLLM for each symbol              |
|  * Extracts: sentiment, technical signal, fundamental health,          |
|    key patterns, risks, opportunities, news sentiment                  |
|  * Full Opik tracing for observability                                 |
|                                                                         |
|  Output: SymbolFeatures with structured insights per symbol            |
+-------------------------------------------------------------------------+
                                |
+=========================================================================+
|                   SYSTEM 2: ANALYZER SYSTEM                              |
+=========================================================================+

+-------------------------------------------------------------------------+
|                  BULL-BEAR ANALYZER ✅                                    |
|                    (3-Agent Debate System)                               |
|-------------------------------------------------------------------------|
|  +----------+   +----------+   +-----------+                           |
|  |   Bull   |   |   Bear   |   | Research  |                           |
|  |Researcher|   |Researcher|   | Manager   |                           |
|  +----------+   +----------+   +-----------+                           |
|         (Bull argues -> Bear rebuts -> Manager synthesizes)             |
|                                                                         |
|  Output: InvestmentThesis with probability-weighted scenarios           |
+-------------------------------------------------------------------------+
                                |
+-------------------------------------------------------------------------+
|                      TEAM 1: ANALYST TEAM ⏳                             |
|                  (Parallel Multi-Perspective Analysis)                   |
+-------------------------------------------------------------------------+
                                |
+-------------------------------------------------------------------------+
|                  TEAM 3: RISK MANAGEMENT TEAM ⏳                         |
|                   (Risk Assessment Debate)                              |
+-------------------------------------------------------------------------+
                                |
+-------------------------------------------------------------------------+
|                      TEAM 4: TRADER AGENT ⏳                             |
|                    (Final Decision & Execution)                          |
+-------------------------------------------------------------------------+
                                |
                         Trading Actions
```

**Legend**: ✅ = Implemented, ⏳ = Planned

---

## Data Processing Pipeline

The Data Processing Pipeline (System 1) transforms raw market data into feature vectors through 3 sequential stages.

---

## Stage 1: Data Retrieval

### Overview

Stage 1 is responsible for **heterogeneous data retrieval** from multiple external sources. It runs 5 specialized agents in parallel to collect different types of market data.

**Status**: ✅ Fully Implemented

### Directory Structure

```
event_horizon/data_pipeline/stage_1/
|-- __init__.py
|-- agents/
|   |-- __init__.py
|   |-- candlestick_agent.py       # OHLCV price data
|   |-- earnings_agent.py          # Financial reports
|   |-- news_agent.py              # News articles (Tavily/Exa)
|   |-- technical_agent.py         # Technical indicators
|   |-- fundamentals_agent.py      # Fundamental metrics
|   +-- utils/
|       +-- stock_tools.py         # get_stock_data, get_indicators, get_fundamentals
|-- services/
|   |-- chart_data_client.py       # Yahoo Finance OHLCV
|   |-- massive_chart_client.py    # Massive.com OHLCV (alternative)
|   |-- financial_data_client.py   # Yahoo Finance earnings/financials
|   |-- news_api_client.py         # NewsAPI.org client (legacy)
|   +-- news_search_client.py      # Tavily + Exa news search (current)
|-- models/
|   +-- schemas.py                 # Stage1Output, NewsData, EarningsData, ChartData, etc.
+-- orchestrator/
    +-- stage_1_orchestrator.py    # Stage1Orchestrator (parallel execution)
```

### Implemented Agents

#### 1. Candlestick Agent ✅

**Purpose**: Retrieve OHLCV (Open, High, Low, Close, Volume) price data

**File**: `event_horizon/data_pipeline/stage_1/agents/candlestick_agent.py`

**Data Sources**:
- Primary: Yahoo Finance (yfinance)
- Alternative: Massive.com API (set `USE_MASSIVE_API=true`)

**Output**: `ChartData` (symbol, candles, period, interval)

#### 2. Earnings Agent ✅

**Purpose**: Retrieve financial reports and earnings data

**File**: `event_horizon/data_pipeline/stage_1/agents/earnings_agent.py`

**Data Source**: Yahoo Finance (stocks, ETFs, mutual funds)

**Output**: `EarningsData` (symbol, security_type, name, earnings_reports, financial_statements, metrics, fund_info)

#### 3. News Agent ✅

**Purpose**: Retrieve news articles about stocks

**File**: `event_horizon/data_pipeline/stage_1/agents/news_agent.py`

**Data Source**: Tavily (primary), Exa (fallback) via `news_search_client.py`

**Output**: `NewsData` (symbol, articles, total_articles, data_source)

#### 4. Technical Agent ✅

**Purpose**: Calculate technical indicators

**File**: `event_horizon/data_pipeline/stage_1/agents/technical_agent.py`

**Data Source**: Yahoo Finance via yfinance + custom calculations

**Supported Indicators**: SMA (20/50 day), EMA (12/26 day), RSI (14 period), MACD

**Output**: `TechnicalData` (symbol, indicators, trade_date, look_back_days)

#### 5. Fundamentals Agent ✅

**Purpose**: Retrieve fundamental metrics and financial ratios

**File**: `event_horizon/data_pipeline/stage_1/agents/fundamentals_agent.py`

**Data Source**: Yahoo Finance via yfinance

**Metrics**: P/E, Forward P/E, PEG, Price/Book, ROE, ROA, profit margins, debt/equity, dividends

**Output**: `FundamentalsData` (symbol, fundamentals_text)

### Services

| Service | File | Purpose |
|---------|------|---------|
| ChartDataClient | `chart_data_client.py` | yfinance OHLCV retrieval |
| MassiveChartClient | `massive_chart_client.py` | Massive.com OHLCV (alternative) |
| FinancialDataClient | `financial_data_client.py` | yfinance earnings, financials, metrics |
| `tavily_news_search()` | `news_search_client.py` | Tavily news search (primary) |
| `exa_news_search()` | `news_search_client.py` | Exa news search (fallback) |
| NewsAPIClient | `news_api_client.py` | NewsAPI.org client (legacy, not used) |

### Performance

**Typical Execution Times** (4 stocks, all 5 agents):
- Sequential: ~25-30s
- Parallel (5 workers): ~7-10s
- **Speedup**: ~3x faster with parallel execution

---

## Stage 2: Normalization

### Overview

**Status**: ✅ Implemented

Stage 2 transforms heterogeneous Stage 1 data into a standardized dataset with unified schemas and data quality scoring per symbol.

### Directory Structure

```
event_horizon/data_pipeline/stage_2/
|-- models/
|   +-- schemas.py                  # NormalizedSymbolData, Stage2Output
|-- normalizer/
|   +-- data_normalizer.py          # DataNormalizer
+-- orchestrator/
    +-- stage_2_orchestrator.py     # Stage2Orchestrator
```

### How It Works

- **DataNormalizer** unifies 6 data categories per symbol: price, technical, fundamentals, news, earnings, web_search
- **Quality scoring** (0-1) based on data completeness across categories, with 20% penalty for errors
- **Symbol categorization**: complete (>=0.9), partial (>=0.5), or error (<0.5)
- Sequential processing: each symbol normalized independently

### Output Schema

```python
@dataclass
class NormalizedSymbolData:
    symbol: str
    price_data: Optional[str]
    technical_indicators: Optional[str]
    fundamentals: Optional[str]
    news: Optional[str]
    earnings: Optional[str]
    web_search: Optional[str]
    data_quality_score: float  # 0.0 - 1.0

@dataclass
class Stage2Output:
    portfolio_id: str
    symbols: List[str]
    normalized_data: Dict[str, NormalizedSymbolData]
    # + quality metrics
```

---

## Stage 3: Feature Extraction

### Overview

**Status**: ✅ Implemented

Stage 3 uses LLM (Mistral via vLLM) to extract structured, analytical features from normalized data for each symbol.

### Directory Structure

```
event_horizon/data_pipeline/stage_3/
|-- models/
|   +-- schemas.py                   # SymbolFeatures, Stage3Output
|-- extractors/
|   +-- llm_feature_extractor.py     # LLMFeatureExtractor (Opik-traced)
+-- orchestrator/
    +-- stage_3_orchestrator.py      # Stage3Orchestrator
```

### How It Works

- **LLMFeatureExtractor** prepares context from normalized data (price, technicals, fundamentals, news, web search)
- Prompts LLM for **structured JSON output** with: market_sentiment, technical_signal, fundamental_health, key_patterns, risk_factors, opportunities, news_sentiment
- Temperature: 0.3 (low for analytical precision)
- Tracks LLM call count, total tokens, average extraction time
- Full **Opik tracing** for observability

### Output Schema

```python
@dataclass
class SymbolFeatures:
    symbol: str
    market_sentiment: str        # bullish, bearish, neutral
    sentiment_confidence: float  # 0-1
    technical_signal: str        # buy, sell, hold
    technical_confidence: float
    fundamental_health: str      # strong, weak, neutral
    fundamental_confidence: float
    key_patterns: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    news_sentiment: str
    news_summary: str
    feature_vector: Dict[str, float]
```

---

## Analyzer System

The Analyzer System (System 2) operates **after** the Data Processing Pipeline. It consumes Stage 3 output (SymbolFeatures) to make trading decisions.

### System Position

```
DATA PROCESSING PIPELINE              ANALYZER SYSTEM
Stage 1 -> Stage 2 -> Stage 3  ->   Bull-Bear -> [Team 1] -> [Team 3] -> [Team 4]
  |          |          |               |
Raw       Unified    Feature       Investment
Data       Data      Vectors        Theses
```

---

## Bull-Bear Analyzer

### Overview

**Status**: ✅ Implemented

**Purpose**: Generate balanced investment theses through a structured 3-agent debate per symbol.

**Location**: `event_horizon/analyzer_system/bull_bear_analyzer/`

### Architecture

```
event_horizon/analyzer_system/bull_bear_analyzer/
|-- __init__.py                    # Exports BullBearAnalyzer, BullBearAnalysisOutput
|-- agents/
|   |-- bull_researcher.py         # BullResearcher (argues for buying)
|   |-- bear_researcher.py         # BearResearcher (argues for selling, rebuts bull)
|   +-- research_manager.py        # ResearchManager (synthesizes balanced thesis)
|-- models/
|   +-- schemas.py                 # BullArgument, BearArgument, InvestmentThesis
+-- orchestrator/
    +-- bull_bear_orchestrator.py   # BullBearAnalyzer (debate coordinator)
```

### Debate Flow (Per Symbol)

1. **BullResearcher** generates bullish argument (BUY/STRONG_BUY) - focuses on growth, catalysts, upside. Temperature: 0.7.
2. **BearResearcher** generates bearish counter-argument (SELL/STRONG_SELL/SHORT) - receives bull argument for rebuttal. Temperature: 0.7.
3. **ResearchManager** synthesizes both into balanced `InvestmentThesis` (BUY/HOLD/SELL) with probability-weighted scenarios. Temperature: 0.4.

### Auto-Data-Fetch

The orchestrator automatically discovers and fetches missing data: if Stage 3 output has symbols without features, it runs the full Stage 1->2->3 pipeline to populate them before running the debate.

### API Endpoint

`POST /agents/bull-bear-analyzer` has 3 paths:
- **Path A** (no data): Discovers required agents via single-shot tool discovery, returns `needs_data` response
- **Path B** (`raw_data` provided): Processes through Stage 1->2->3 pipeline, then runs debate
- **Path C** (pre-processed `data`): Runs debate directly with SymbolFeatures

### Output

```python
@dataclass
class InvestmentThesis:
    symbol: str
    recommendation: str     # BUY, HOLD, SELL
    confidence: float       # 0-1
    position_size: str
    thesis_summary: str
    bull_case_summary: str
    bear_case_summary: str
    bull_probability: float
    bear_probability: float
    base_case: str
    bull_case: str
    bear_case: str
```

---

## Team 1: Analyst Team

**Status**: ⏳ Planned

Multi-perspective parallel analysis (Fundamentals, Market, News, Social Media analysts).

---

## Team 3: Risk Management Team

**Status**: ⏳ Planned

Risk assessment debate (Conservative, Neutral, Aggressive debators + Risk Manager).

---

## Team 4: Trader Agent

**Status**: ⏳ Planned

Final decision and execution based on all upstream outputs.

---

## Thinking Agent System

### Overview

The Thinking Agent system adds **ReAct-style iterative reasoning** to custom agents. This allows agents to autonomously decide what data they need and request it through tool calls.

**Status**: ✅ Implemented

### Architecture

```
Portfolio -> Thinking Agent -> [Iteration Loop] -> Final Output
                |
           +--------------------------------------------+
           |  1. Analyze input (portfolio or data)       |
           |  2. Decide: Need more data?                 |
           |     -> Yes: Call tool (candlestick,         |
           |            earnings, news, technical,       |
           |            fundamentals, web_search)        |
           |     -> No: Generate analysis                |
           |  3. Loop until max iterations               |
           +--------------------------------------------+
```

### Key Features

- **Iterative Reasoning**: Agent thinks step-by-step about what data it needs
- **6 Tools**: candlestick, earnings, news, technical, fundamentals, web_search
- **Single-Shot Tool Discovery**: `discover_required_tools()` identifies all needed tools at once
- **Custom Data Agent Creation**: Can suggest exotic data agents (scoped to web_search tool)
- **Thinking Transparency**: All reasoning steps captured for UI display
- **Configurable Iterations**: Max iterations (1-10) prevent infinite loops

### API Endpoint

```
POST /agents/think
{
  "stocks": ["AAPL", "TSLA"],
  "system_prompt": "You are a dividend-focused analyst...",
  "max_iterations": 5,
  "available_tools": ["candlestick", "earnings", "news", "technical", "fundamentals", "web_search"]
}
```

### Documentation

See [Thinking Agent Guide](../guides/thinking-agent.md) for full API documentation and usage examples.

---

## Observability (Opik)

Opik tracing is integrated across Stage 3 and the Bull-Bear Analyzer with a safe fallback pattern:

```python
try:
    from opik import track
except ImportError:
    track = lambda **kw: lambda fn: fn  # no-op when opik not installed
```

**Traced operations**:
- Stage 3: `stage3_pipeline`, `extract_features`, `llm_extraction_call`
- Bull-Bear: `bull_bear_debate_pipeline`, `symbol_debate`, `bull_research_argument`, `bear_research_argument`, `synthesize_thesis`, and individual LLM calls

---

## Workflow & Communication

### Complete System Flow

```
1. Stage 1: Data Retrieval (Parallel)
   - 5 agents collect raw data simultaneously
   |
2. Stage 2: Normalization (Sequential per symbol)
   - Unify data, compute quality scores
   |
3. Stage 3: Feature Extraction (LLM per symbol)
   - Extract structured insights via Mistral/vLLM
   |
   SymbolFeatures Output
   |
4. Bull-Bear Analyzer (Sequential per symbol)
   - Bull argument -> Bear rebuttal -> Manager synthesis
   |
   InvestmentThesis Output
```

### Communication Pattern

**Framework**: FastAPI + custom orchestration (no LangGraph dependency)

The FastAPI app (`event_horizon/thinking-multi-agent/app/main.py`) serves as the primary entry point. All data flows through REST endpoints, with the services layer coordinating between the data pipeline and analyzer system.

---

## Implementation Status

### System 1: Data Processing Pipeline

#### Phase 1: Stage 1 Implementation ✅ COMPLETED
- ✅ 5 data retrieval agents running in parallel
- ✅ Orchestrator with ThreadPoolExecutor (5 workers)
- ✅ Tavily/Exa news search (replaced NewsAPI)
- ✅ Services: ChartDataClient, FinancialDataClient, news_search_client

#### Phase 2: Stage 2 Implementation ✅ COMPLETED
- ✅ DataNormalizer: unify 6 data categories per symbol
- ✅ Quality scoring (0-1) with symbol categorization
- ✅ Stage2Orchestrator: sequential per-symbol processing

#### Phase 3: Stage 3 Implementation ✅ COMPLETED
- ✅ LLMFeatureExtractor: structured JSON output via Mistral/vLLM
- ✅ SymbolFeatures: sentiment, signals, patterns, risks, opportunities
- ✅ Opik tracing integration
- ✅ Token usage and timing metrics

### System 2: Analyzer System

#### Phase 4: Bull-Bear Analyzer ✅ COMPLETED
- ✅ BullResearcher, BearResearcher, ResearchManager agents
- ✅ 3-step debate: bull -> bear rebuttal -> manager synthesis
- ✅ Auto-data-fetch for missing symbol features
- ✅ Opik tracing for full debate pipeline
- ✅ InvestmentThesis with probability-weighted scenarios

#### Phase 5: Team 1 - Analyst Team ⏳ PLANNED
- [ ] Implement 4 analyst agents (fundamentals, market, news, social)
- [ ] Create analyst orchestrator for parallel execution

#### Phase 6: Team 3 - Risk Management ⏳ PLANNED
- [ ] Implement 3 risk debators (conservative, neutral, aggressive)
- [ ] Implement risk manager with debate orchestration

#### Phase 7: Team 4 - Trader Agent ⏳ PLANNED
- [ ] Implement trader agent decision logic
- [ ] Create execution plan generator
- [ ] End-to-end system integration

### FastAPI Application ✅ COMPLETED
- ✅ v3.0.0 with 20+ endpoints
- ✅ Agent CRUD with JSON persistence
- ✅ Thinking Agent (ReAct-style iterative reasoning)
- ✅ Tool discovery and custom agent creation
- ✅ Streaming analysis (SSE)
- ✅ Web search integration (Tavily + Exa)

---

## Tauric Research Integration

This architecture is inspired by [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents).

### What We Integrated from Tauric ✅

**Data Processing Pipeline (System 1)**:
- ✅ Technical indicator calculation tools (Stage 1)
- ✅ Fundamental metrics retrieval patterns (Stage 1)
- ✅ Stock data utility functions (`stage_1/agents/utils/stock_tools.py`)
- ✅ Multi-source data collection approach

**Analyzer System (System 2)**:
- ✅ Bull/Bear debate pattern (implemented as Bull-Bear Analyzer)

---

## Future Enhancements

### Advanced Features
- **Portfolio-Level Analysis**: Multi-stock correlation and portfolio construction
- **Continuous Learning**: Agent performance tracking and strategy refinement
- **Market Regime Detection**: Adapt strategy based on market conditions
- **Backtesting Integration**: Historical simulation of agent decisions
- **Real-Time Monitoring**: Live position tracking and dynamic adjustment

### Scalability
- **Agent Versioning**: A/B test different agent implementations
- **Parallel Portfolio Processing**: Handle multiple portfolios simultaneously
- **Distributed Execution**: Scale agents across multiple machines
- **Caching & Optimization**: Reduce redundant computation

---

## Key Principles

1. **Two-System Architecture**: Data Processing Pipeline (System 1) and Analyzer System (System 2) are separate but connected
2. **Separation of Concerns**: Data transformation != Trading decisions
3. **Multi-Perspective Analysis**: Debate and consensus for robust decisions
4. **Risk-Aware**: Explicit risk management team prevents reckless trades
5. **Inspired by Research**: Leverages proven patterns from Tauric framework
6. **Extensible Architecture**: Easy to add new agents to either system

---

## References

- **Thinking Agent Guide**: `docs/guides/thinking-agent.md`
- **Stage 1 Guide**: `docs/guides/stage-1-guide.md`
- **System Architecture**: `docs/architecture/system-architecture.md`

---

**Version**: 3.0.0
**Last Updated**: 2026-02-10
