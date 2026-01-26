# Event Horizon - Multi-Agent Architecture

**Status**: Data Pipeline Stage 1 ✅ Implemented | Data Pipeline Stages 2-3 & Decision System ⏳ Planned
**Last Updated**: 2026-01-25

Complete multi-agent architecture for Event Horizon, consisting of:
- **Data Processing Pipeline** (3 stages): Raw data → Normalized data → Feature vectors
- **Decision-Making System** (4 teams): Analysis → Research → Risk Management → Trading

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Data Processing Pipeline](#data-processing-pipeline)
   - [Stage 1: Data Retrieval](#stage-1-data-retrieval)
   - [Stage 2: Normalization](#stage-2-normalization)
   - [Stage 3: Feature Extraction](#stage-3-feature-extraction)
3. [Decision-Making System](#decision-making-system)
   - [Team 1: Analyst Team](#team-1-analyst-team)
   - [Team 2: Researcher Team](#team-2-researcher-team)
   - [Team 3: Risk Management Team](#team-3-risk-management-team)
   - [Team 4: Trader Agent](#team-4-trader-agent)
4. [Workflow & Communication](#workflow--communication)
5. [Implementation Status](#implementation-status)

---

## System Overview

Event Horizon uses **two separate multi-agent systems** that work together:

### System 1: Data Processing Pipeline
**Purpose**: Transform raw market data into feature vectors
**Stages**: 3 (Data Retrieval → Normalization → Feature Extraction)
**Status**: Stage 1 ✅ Implemented, Stages 2-3 ⏳ Planned

### System 2: Decision-Making System
**Purpose**: Make intelligent trading decisions from feature vectors
**Teams**: 4 (Analyst → Researcher → Risk Management → Trader)
**Status**: ⏳ Planned

### Complete Architecture

```
╔═════════════════════════════════════════════════════════════════════════╗
║                   SYSTEM 1: DATA PROCESSING PIPELINE                    ║
╚═════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────┐
│                   STAGE 1: DATA RETRIEVAL ✅                             │
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
│             STAGE 2: NORMALIZATION & STANDARDIZATION ⏳                  │
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
│                  STAGE 3: FEATURE EXTRACTION ⏳                          │
│          (LLM/Neural AI - Intelligent Feature Discovery)                │
├─────────────────────────────────────────────────────────────────────────┤
│  • Extract non-obvious patterns from normalized data                   │
│  • Generate embeddings and latent features                             │
│  • Identify predictive signals for trading                             │
│                                                                         │
│  Output: Feature vectors ready for trading decisions                   │
└─────────────────────────────────────────────────────────────────────────┘
                                ↓
╔═════════════════════════════════════════════════════════════════════════╗
║                   SYSTEM 2: DECISION-MAKING SYSTEM                      ║
╚═════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────┐
│                        TEAM 1: ANALYST TEAM ⏳                           │
│                    (Parallel Multi-Perspective Analysis)                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ Fundamentals │  │    Market    │  │     News     │                 │
│  │   Analyst    │  │   Analyst    │  │   Analyst    │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│  ┌──────────────┐                                                      │
│  │ Social Media │                                                      │
│  │   Analyst    │                                                      │
│  └──────────────┘                                                      │
│                                                                         │
│  Output: Multi-dimensional analysis reports                            │
└─────────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                     TEAM 2: RESEARCHER TEAM ⏳                           │
│                      (Bull vs Bear Debate)                              │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │     Bull     │  │     Bear     │  │   Research   │                 │
│  │  Researcher  │  │  Researcher  │  │   Manager    │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│                 (Multi-Round Debate & Consensus)                       │
│                                                                         │
│  Output: Investment thesis with bull/bear cases                        │
└─────────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                  TEAM 3: RISK MANAGEMENT TEAM ⏳                         │
│                   (Risk Assessment Debate)                              │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ Conservative │  │   Neutral    │  │  Aggressive  │                 │
│  │   Debator    │  │   Debator    │  │   Debator    │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│  ┌──────────────┐                                                      │
│  │     Risk     │                                                      │
│  │   Manager    │                                                      │
│  └──────────────┘                                                      │
│                                                                         │
│  Output: Risk parameters & position sizing                             │
└─────────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      TEAM 4: TRADER AGENT ⏳                             │
│                      (Final Decision & Execution)                       │
├─────────────────────────────────────────────────────────────────────────┤
│  • Reviews all team outputs                                            │
│  • Makes final trading decision                                        │
│  • Determines portfolio allocation                                     │
│  • Generates order execution strategy                                  │
│                                                                         │
│  Output: Trading actions & execution plan                              │
└─────────────────────────────────────────────────────────────────────────┘
                                ↓
                        🎯 Trading Actions
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

### Quick Links

- 📚 [Quick Start Guide](../../QUICKSTART_STAGE1.md)
- 🔧 [Tauric Integration Details](../../stage_1/TAURIC_INTEGRATION.md)
- 📝 [Update Summary](../../STAGE1_UPDATE_SUMMARY.md)

**Note**: The codebase uses `stage_1/` directory naming, which refers to Stage 1 of the Data Processing Pipeline.

### Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                      APPLICATION STAGE                                  │
│                      main_stage1.py                                     │
│  • Configuration setup                                                 │
│  • Result display                                                      │
│  • Output persistence                                                  │
└────────────────────────────────────────────────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION STAGE                                  │
│               stage_1/orchestrator/stage_1_orchestrator.py             │
│                                                                         │
│  Stage1Orchestrator:                                                   │
│  • Parallel execution (ThreadPoolExecutor, 5 workers)                  │
│  • Agent lifecycle management                                          │
│  • Result aggregation into Stage1Output                                │
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

### Directory Structure

```
stage_1/
├── __init__.py                 # Stage 1 exports
├── agents/                     # Data retrieval agents
│   ├── __init__.py
│   ├── candlestick_agent.py   # OHLCV price data
│   ├── earnings_agent.py      # Financial reports
│   ├── news_agent.py          # News articles
│   ├── technical_agent.py     # Technical indicators (Tauric)
│   ├── fundamentals_agent.py  # Fundamental metrics (Tauric)
│   └── utils/
│       └── stock_tools.py     # Utility functions (Tauric)
├── services/                   # API client stage
│   ├── __init__.py
│   ├── chart_data_client.py   # Yahoo Finance charts
│   ├── massive_chart_client.py # Massive.com alternative
│   ├── financial_data_client.py # Yahoo Finance fundamentals
│   └── news_api_client.py     # NewsAPI client
├── models/                     # Data schemas
│   ├── __init__.py
│   └── schemas.py             # Stage1Output and data classes
├── orchestrator/               # Parallel execution
│   ├── __init__.py
│   └── stage_1_orchestrator.py # Stage1Orchestrator class
└── TAURIC_INTEGRATION.md      # Integration details
```

### Implemented Agents

#### 1. Candlestick Agent ✅

**Purpose**: Retrieve OHLCV (Open, High, Low, Close, Volume) price data

**File**: `stage_1/agents/candlestick_agent.py`

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

#### 2. Earnings Agent ✅

**Purpose**: Retrieve financial reports and earnings data

**File**: `stage_1/agents/earnings_agent.py`

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

#### 3. News Agent ✅

**Purpose**: Retrieve news articles about stocks

**File**: `stage_1/agents/news_agent.py`

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

#### 4. Technical Agent ✅ (Tauric-Inspired)

**Purpose**: Calculate technical indicators

**File**: `stage_1/agents/technical_agent.py`

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

#### 5. Fundamentals Agent ✅ (Tauric-Inspired)

**Purpose**: Retrieve fundamental metrics and financial ratios

**File**: `stage_1/agents/fundamentals_agent.py`

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

### Usage Example

```python
from stage_1 import Stage1Orchestrator

# Configure orchestrator
config = {
    "enabled_agents": ["candlestick", "earnings", "news", "technical", "fundamentals"],
    "max_workers": 5,
    "agent_configs": {
        "candlestick": {
            "period": "3mo",
            "interval": "1d",
            "data_source": "yahoo"
        },
        "technical": {
            "indicators": ["SMA", "RSI", "MACD", "EMA"],
            "look_back_days": 60
        }
    }
}

# Execute
orchestrator = Stage1Orchestrator(config=config)
result = orchestrator.execute(["AAPL", "TSLA", "NVDA"])

# Access data
stage1_output = result["stage1_output"]
print(stage1_output.chart_data["AAPL"].candles)
print(stage1_output.technical_data["AAPL"].indicators["RSI"])
```

### Performance

**Typical Execution Times** (4 stocks, all 5 agents):
- Sequential: ~25-30s
- Parallel (5 workers): ~7-10s
- **Speedup**: ~3x faster with parallel execution

---

## Stage 2: Normalization

### Overview

**Status**: ⏳ Planned

Stage 2 transforms heterogeneous Stage 1 data into a standardized "DNA" dataset with unified schemas, time synchronization, and format normalization.

### Responsibilities

- **Time Synchronization**: Align data from different sources to common timestamps
- **Symbol Mapping**: Normalize ticker symbols across data sources
- **Format Standardization**: Convert all data to tabular schema
- **Data Quality**: Handle missing values, outliers, and inconsistencies

### Output Schema

```python
@dataclass
class Stage2Output:
    portfolio_id: str
    symbols: List[str]
    normalized_data: pd.DataFrame  # Unified tabular format
    metadata: Dict[str, Any]
    timestamp: str
```

---

## Stage 3: Feature Extraction

### Overview

**Status**: ⏳ Planned

Stage 3 uses LLM/Neural AI to extract non-obvious patterns and generate predictive features from normalized data.

### Responsibilities

- **Pattern Recognition**: Identify hidden patterns in time-series data
- **Embedding Generation**: Create semantic embeddings from text (news, earnings)
- **Latent Features**: Extract features not directly observable in raw data
- **Signal Discovery**: Identify predictive signals for trading decisions

### Output Schema

```python
@dataclass
class Stage3Output:
    portfolio_id: str
    symbols: List[str]
    features: Dict[str, FeatureVector]
    metadata: Dict[str, Any]

@dataclass
class FeatureVector:
    company_health_score: float
    investor_sentiment_score: float
    technical_momentum_score: float
    macro_alignment_score: float
    risk_score: float
    # Additional extracted features
```

---

## Decision-Making System

The Decision-Making System (System 2) operates **after** the Data Processing Pipeline. It consumes Stage 3 output (feature vectors) to make intelligent trading decisions through 4 specialized teams.

### System Position

```
DATA PROCESSING PIPELINE          DECISION-MAKING SYSTEM
Stage 1 → Stage 2 → Stage 3  →   Team 1 → Team 2 → Team 3 → Team 4
  ↓         ↓         ↓              ↓        ↓        ↓        ↓
Raw      Standard   Feature      Analysis  Research   Risk   Trading
Data       DNA      Vectors                                  Actions
```

---

## Team 1: Analyst Team

### Overview

**Status**: ⏳ Planned

**Purpose**: Analyze different aspects of market data and provide specialized insights

**Execution**: Parallel (all analysts run simultaneously)

### Agents

**Fundamentals Analyst**
- **Input**: Company financial data, earnings reports, balance sheets
- **Analysis**: Financial health, valuation ratios, growth metrics
- **Output**: Fundamental strength score and reasoning

**Market Analyst**
- **Input**: Price action, technical indicators, volume patterns
- **Analysis**: Trend identification, support/resistance, momentum
- **Output**: Technical outlook and key levels

**News Analyst**
- **Input**: News articles, headlines, sentiment
- **Analysis**: News impact, sentiment shift, event catalysis
- **Output**: News sentiment score and key narratives

**Social Media Analyst**
- **Input**: Twitter/Reddit mentions, sentiment, trending topics
- **Analysis**: Retail sentiment, hype detection, community pulse
- **Output**: Social sentiment score and viral trends

### Team Output

Multi-dimensional analysis report consolidating all perspectives

---

## Team 2: Researcher Team

### Overview

**Status**: ⏳ Planned

**Purpose**: Debate investment thesis from bull and bear perspectives to reach balanced conclusion

**Execution**: Sequential debate with configurable rounds

### Agents

**Bull Researcher**
- **Role**: Advocate for long positions
- **Analysis**: Find positive catalysts, growth opportunities, upside potential
- **Stance**: Optimistic, growth-focused

**Bear Researcher**
- **Role**: Advocate for short positions or caution
- **Analysis**: Identify risks, overvaluation, downside scenarios
- **Stance**: Skeptical, risk-focused

**Research Manager**
- **Role**: Facilitate debate, synthesize perspectives
- **Process**:
  1. Present analyst team findings to bull/bear researchers
  2. Conduct multi-round debate (configurable rounds)
  3. Weigh arguments based on data strength
  4. Generate consensus investment thesis

### Team Output

Balanced investment recommendation with bull/bear case and probability-weighted scenarios

---

## Team 3: Risk Management Team

### Overview

**Status**: ⏳ Planned

**Purpose**: Assess risk and determine appropriate position sizing through multi-perspective debate

**Execution**: Sequential debate with configurable rounds

### Agents

**Conservative Debator**
- **Stance**: Risk-averse, capital preservation focused
- **Analysis**: Downside protection, worst-case scenarios
- **Recommendation**: Smaller positions, tight stops

**Neutral Debator**
- **Stance**: Balanced risk-reward assessment
- **Analysis**: Expected value, risk-adjusted returns
- **Recommendation**: Moderate positions, standard risk parameters

**Aggressive Debator**
- **Stance**: Return-maximizing, higher risk tolerance
- **Analysis**: Upside potential, asymmetric opportunities
- **Recommendation**: Larger positions, wider stops

**Risk Manager**
- **Role**: Facilitate risk debate, determine final risk parameters
- **Process**:
  1. Present investment thesis from researcher team
  2. Conduct risk assessment debate
  3. Synthesize risk perspectives
  4. Set position size, stop loss, take profit levels

### Team Output

Risk-adjusted position sizing with entry/exit parameters

---

## Team 4: Trader Agent

### Overview

**Status**: ⏳ Planned

**Purpose**: Execute final trading decision based on all team inputs

**Responsibilities**:
- Review all team outputs (analyst, researcher, risk management)
- Make final go/no-go decision
- Determine exact position sizing within risk parameters
- Generate order execution strategy
- Monitor position post-entry

**Decision Framework**:
```python
if analyst_score > threshold and investment_thesis == "BUY":
    if risk_parameters.acceptable:
        execute_trade(
            symbol=symbol,
            direction=direction,
            size=risk_parameters.position_size,
            entry=entry_price,
            stop_loss=risk_parameters.stop_loss,
            take_profit=risk_parameters.take_profit
        )
```

---

## Workflow & Communication

### Complete System Flow

```
╔═════════════════════════════════════════════════════════════════════╗
║             SYSTEM 1: DATA PROCESSING PIPELINE                      ║
╚═════════════════════════════════════════════════════════════════════╝

1. Stage 1: Data Retrieval (Parallel)
   - 5 agents collect raw data simultaneously
   ↓
2. Stage 2: Normalization
   - Standardize formats and timestamps
   ↓
3. Stage 3: Feature Extraction
   - LLM/Neural AI extracts patterns
   ↓
   Feature Vectors Output

╔═════════════════════════════════════════════════════════════════════╗
║             SYSTEM 2: DECISION-MAKING SYSTEM                        ║
╚═════════════════════════════════════════════════════════════════════╝

4. Team 1: Analyst Team (Parallel)
   - All 4 analysts run simultaneously
   - Consolidate findings
   ↓
5. Team 2: Researcher Team (Sequential Debate)
   - Bull/Bear debate in rounds
   - Research Manager synthesizes
   ↓
6. Team 3: Risk Management Team (Sequential Debate)
   - Conservative/Neutral/Aggressive debate
   - Risk Manager sets parameters
   ↓
7. Team 4: Trader Agent (Final Decision)
   - Review all inputs
   - Execute or reject trade
   ↓
   Trading Actions
```

### Communication Pattern

**Framework**: LangGraph for state management and workflow orchestration

**State Object**:
```python
@dataclass
class TradingAgentState:
    # Input from System 1 (Data Processing Pipeline)
    portfolio: List[str]
    feature_vectors: Dict[str, FeatureVector]  # From Stage 3

    # Team 1 Output (Analyst Team)
    analyst_reports: Dict[str, AnalystReport]

    # Team 2 Output (Researcher Team)
    investment_thesis: InvestmentThesis
    bull_case: str
    bear_case: str
    confidence: float

    # Team 3 Output (Risk Management Team)
    risk_parameters: RiskParameters
    position_size: float
    stop_loss: float
    take_profit: float

    # Team 4 Output (Trader Agent)
    trading_decision: TradingDecision
    execution_plan: ExecutionPlan
```

### System Interfaces

**Data Processing Pipeline → Decision-Making System**:
```python
# Stage 3 Output → Team 1 Input (Feature Vectors)
{
    "portfolio_id": "...",
    "symbols": ["AAPL", "TSLA"],
    "features": {
        "AAPL": {
            "company_health_score": 0.85,
            "investor_sentiment_score": 0.72,
            "technical_momentum_score": 0.68,
            "macro_alignment_score": 0.55,
            "risk_score": 0.33,
            # ... extracted features
        }
    },
    "metadata": {...}
}
```

**Decision-Making System → Trading Execution**:
```python
{
    "trading_decisions": [
        {
            "symbol": "AAPL",
            "action": "BUY",
            "position_size": 100,
            "entry_price": 185.50,
            "stop_loss": 178.00,
            "take_profit": 198.00,
            "confidence": 0.78,
            "rationale": "Strong fundamentals + bullish technical setup..."
        }
    ]
}
```

---

## Tauric Research Integration

This architecture is inspired by [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents).

### Clear Separation

```
SYSTEM 1: DATA PROCESSING PIPELINE    SYSTEM 2: DECISION-MAKING SYSTEM
├─ Stage 1: Get the data              ├─ Team 1: Analyze data
├─ Stage 2: Normalize data            ├─ Team 2: Debate thesis
├─ Stage 3: Extract features          ├─ Team 3: Size positions
                ↓                      └─ Team 4: Execute trades
        Feature vectors
```

### What We Integrated from Tauric ✅

**Data Processing Pipeline (System 1)**:
- ✅ Technical indicator calculation tools (Stage 1)
- ✅ Fundamental metrics retrieval patterns (Stage 1)
- ✅ Stock data utility functions (`stage_1/agents/utils/stock_tools.py`)
- ✅ Multi-source data collection approach

**Decision-Making System (System 2)** ⏳:
- Multi-agent debate patterns (bull/bear, risk debators)
- Hierarchical team structure (analysts → researchers → risk → trader)
- LangGraph workflow orchestration
- Configurable debate rounds

### Tauric Agent Mapping

| Tauric Agent | Event Horizon Equivalent | System/Team |
|--------------|-------------------------|-------------|
| fundamentals_analyst | Fundamentals Analyst | System 2 - Team 1 |
| market_analyst | Market Analyst | System 2 - Team 1 |
| news_analyst | News Analyst | System 2 - Team 1 |
| social_media_analyst | Social Media Analyst | System 2 - Team 1 |
| bull_researcher | Bull Researcher | System 2 - Team 2 |
| bear_researcher | Bear Researcher | System 2 - Team 2 |
| research_manager | Research Manager | System 2 - Team 2 |
| safe_debator | Conservative Debator | System 2 - Team 3 |
| neutral_debator | Neutral Debator | System 2 - Team 3 |
| risky_debator | Aggressive Debator | System 2 - Team 3 |
| risk_manager | Risk Manager | System 2 - Team 3 |
| trader | Trader Agent | System 2 - Team 4 |

**Reference Location**: `core_refs/TradingAgents/`

---

## Implementation Status

### System 1: Data Processing Pipeline

#### Phase 1: Stage 1 Implementation ✅ COMPLETED
- ✅ Stage 1 data retrieval agents implemented
- ✅ Tauric repository cloned for reference
- ✅ 5 agents running in parallel (candlestick, earnings, news, technical, fundamentals)
- ✅ Orchestrator with ThreadPoolExecutor

#### Phase 2: Stage 2 Implementation ⏳ PLANNED
- [ ] Stage 2 normalization pipeline
- [ ] Time synchronization across data sources
- [ ] Symbol mapping and standardization
- [ ] Unified tabular schema

#### Phase 3: Stage 3 Implementation ⏳ PLANNED
- [ ] Stage 3 feature extraction with LLM/Neural AI
- [ ] Pattern recognition in time-series data
- [ ] Embedding generation for text data
- [ ] Predictive signal discovery

### System 2: Decision-Making System

#### Phase 4: Team 1 Implementation ⏳ PLANNED
- [ ] Implement 4 analyst agents (fundamentals, market, news, social)
- [ ] Create analyst orchestrator for parallel execution
- [ ] Define analyst report schema
- [ ] Test analyst team on sample data

#### Phase 5: Team 2 Implementation ⏳ PLANNED
- [ ] Implement bull/bear researchers
- [ ] Implement research manager with debate logic
- [ ] Create investment thesis schema
- [ ] Test multi-round debate mechanism

#### Phase 6: Team 3 Implementation ⏳ PLANNED
- [ ] Implement 3 risk debators (conservative, neutral, aggressive)
- [ ] Implement risk manager with debate orchestration
- [ ] Define risk parameters schema
- [ ] Test position sizing logic

#### Phase 7: Team 4 Implementation ⏳ PLANNED
- [ ] Implement trader agent decision logic
- [ ] Create execution plan generator
- [ ] Integrate with all upstream teams
- [ ] End-to-end system testing

#### Phase 8: System Integration ⏳ PLANNED
- [ ] Design state machine for workflow
- [ ] Implement LangGraph orchestration
- [ ] Add checkpointing and retry logic
- [ ] Performance optimization

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

1. **Two-System Architecture**: Data Processing Pipeline (System 1) and Decision-Making System (System 2) are separate but connected
2. **Separation of Concerns**: Data transformation ≠ Trading decisions
3. **Multi-Perspective Analysis**: Debate and consensus for robust decisions
4. **Risk-Aware**: Explicit risk management team prevents reckless trades
5. **Inspired by Research**: Leverages proven patterns from Tauric framework
6. **Extensible Architecture**: Easy to add new agents to either system

---

## References

- **Quick Start**: `QUICKSTART_STAGE1.md`
- **Tauric Integration**: `stage_1/TAURIC_INTEGRATION.md`
- **Update Summary**: `STAGE1_UPDATE_SUMMARY.md`
- **Tauric Codebase**: `core_refs/TradingAgents/`

---

**Version**: 1.0.0
**Last Updated**: 2026-01-25
