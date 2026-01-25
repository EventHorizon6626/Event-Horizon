# Event Horizon - Multi-Agent Scalable Architecture

Guide for scaling Event Horizon to support many AI agents with orchestration.

---

## Table of Contents

1. [Three-Layer Agent Architecture (Vision)](#three-layer-agent-architecture-vision)
2. [Current Architecture](#current-architecture)
3. [Future Architecture (Multi-Agent)](#future-architecture-multi-agent)
4. [Adding New Agents](#adding-new-agents)
5. [Agent Orchestration](#agent-orchestration)
6. [Communication Patterns](#communication-patterns)
7. [Deployment Strategies](#deployment-strategies)
8. [Monitoring & Observability](#monitoring--observability)

---

## Three-Layer Agent Architecture (Vision)

### Overview

Event Horizon's ultimate architecture follows a three-layer data processing pipeline, where raw heterogeneous data flows through retrieval → normalization → feature extraction to produce actionable trading signals.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LAYER 1: DATA RETRIEVAL                         │
│                     (Heterogeneous Data Collection)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Candlestick  │  │   Earnings   │  │     News     │  │  SEC       │ │
│  │ Data Agent   │  │ Report Agent │  │ Agent        │  │  Filings   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Social Media │  │ Options Flow │  │ Insider      │  │  Macro     │ │
│  │ Sentiment    │  │ Agent        │  │ Trading      │  │  Economic  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│                                                                         │
│                              ↓  ↓  ↓                                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                  LAYER 2: NORMALIZATION & STANDARDIZATION               │
│                      (Create Unified "DNA" Dataset)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Data Filter  │  │ Time Sync    │  │ Symbol       │  │  Format    │ │
│  │ Agent        │  │ Agent        │  │ Mapper       │  │  Normalizer│ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│                                                                         │
│              ┌─────────────────────────────────────┐                   │
│              │  Standardized Tabular "DNA" Schema  │                   │
│              │  ┌───────────────────────────────┐  │                   │
│              │  │ • Company Health Metrics      │  │                   │
│              │  │ • Investor Sentiment Metrics  │  │                   │
│              │  │ • Market Technical Metrics    │  │                   │
│              │  │ • Macro/External Metrics      │  │                   │
│              │  │ • Risk Metrics                │  │                   │
│              │  └───────────────────────────────┘  │                   │
│              └─────────────────────────────────────┘                   │
│                              ↓                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    LAYER 3: FEATURE EXTRACTION                          │
│              (LLM/Neural AI - Intelligent Feature Discovery)            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │          Tabular LLM / Neural Network Feature Extractor          │  │
│  │                                                                  │  │
│  │  • Reads standardized tabular "DNA" data                        │  │
│  │  • Extracts non-obvious patterns and correlations               │  │
│  │  • Generates embeddings and latent features                     │  │
│  │  • Identifies predictive signals for trading                    │  │
│  │                                                                  │  │
│  │  Potential Frameworks:                                           │  │
│  │  - ToolOrchestra (multi-model orchestration)                    │  │
│  │  - TabLLM (LLM for tabular data)                                │  │
│  │  - Custom neural architectures                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│                              ↓                                          │
│                                                                         │
│                    🎯 Actionable Trading Signals                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Layer 1: Data Retrieval Agents

**Purpose**: Collect heterogeneous data from various sources

**Agent Types**:

| Agent Category | Examples | Data Output |
|----------------|----------|-------------|
| **Price Data** | Candlestick Agent, Options Chain Agent | OHLCV, Greeks, IV |
| **Fundamentals** | Earnings Report Agent, SEC Filings Agent | Revenue, EPS, Balance Sheet |
| **News & Media** | News Scraper, Social Media Agent, Reddit Sentiment | Articles, Posts, Sentiment Raw |
| **Market Data** | Options Flow Agent, Insider Trading Agent | Large trades, Executive buys/sells |
| **Macro Data** | Economic Indicators Agent, Sector Performance | GDP, Inflation, Sector Returns |

**Characteristics**:
- Each agent specializes in ONE data source
- Output format is agent-specific (JSON, CSV, raw text)
- Agents run independently and in parallel
- No standardization at this layer

---

### Layer 2: Normalization & Standardization Agents

**Purpose**: Transform heterogeneous data into a unified, standardized tabular format (the "DNA" dataset)

**Agent Responsibilities**:

1. **Data Filtering**
   - Remove duplicates
   - Filter by date ranges
   - Remove null/invalid entries

2. **Time Synchronization**
   - Align timestamps across sources
   - Handle different market hours (US, EU, Asia)
   - Forward-fill/backward-fill missing data

3. **Symbol Mapping**
   - Normalize ticker symbols (AAPL vs AAPL.US)
   - Handle splits, mergers, name changes
   - Map to unique identifiers (CUSIP, ISIN)

4. **Format Standardization**
   - Convert all data to tabular rows
   - Apply consistent column names
   - Normalize units (%, basis points, currency)

**Output: Standardized "DNA" Schema**

The unified dataset contains these column groups:

#### 1. Company Health Metrics
Core financial and operational health indicators:

```python
company_health = {
    # Income Statement
    'revenue': float,                    # Total revenue (quarterly)
    'revenue_growth_yoy': float,         # Year-over-year growth %
    'net_income': float,                 # Bottom line earnings
    'earnings_per_share': float,         # EPS (diluted)
    'earnings_surprise': float,          # Actual vs Expected EPS
    'operating_margin': float,           # Operating income / Revenue
    'net_margin': float,                 # Net income / Revenue
    'gross_margin': float,               # Gross profit / Revenue

    # Balance Sheet
    'total_assets': float,
    'total_liabilities': float,
    'shareholder_equity': float,
    'cash_and_equivalents': float,
    'total_debt': float,
    'current_ratio': float,              # Current assets / Current liabilities
    'debt_to_equity': float,             # Total debt / Equity
    'quick_ratio': float,                # (Current assets - Inventory) / Current liab.

    # Cash Flow
    'operating_cash_flow': float,
    'free_cash_flow': float,             # OCF - CapEx
    'capex': float,                      # Capital expenditures

    # Profitability Ratios
    'return_on_equity': float,           # Net income / Equity (ROE)
    'return_on_assets': float,           # Net income / Assets (ROA)
    'return_on_invested_capital': float, # NOPAT / Invested capital (ROIC)

    # Valuation
    'price_to_earnings': float,          # P/E ratio
    'price_to_book': float,              # P/B ratio
    'price_to_sales': float,             # P/S ratio
    'ev_to_ebitda': float,               # Enterprise value / EBITDA
}
```

#### 2. Investor Sentiment Metrics
Indicators of market participant sentiment and behavior:

```python
investor_sentiment = {
    # News Sentiment
    'news_sentiment_score': float,           # -1 (bearish) to +1 (bullish)
    'news_sentiment_volume': int,            # Number of articles
    'news_sentiment_trend': float,           # 7-day sentiment change
    'news_coverage_change': float,           # % change in article count

    # Social Media Sentiment
    'social_sentiment_score': float,         # Twitter/Reddit aggregate sentiment
    'social_mention_volume': int,            # Total mentions
    'social_engagement_score': float,        # Likes + Retweets + Comments
    'reddit_wsb_mentions': int,              # WallStreetBets mentions

    # Analyst Ratings
    'analyst_rating_consensus': float,       # 1 (strong sell) to 5 (strong buy)
    'analyst_target_price_avg': float,       # Average price target
    'analyst_upgrades_downgrades': int,      # Net upgrades - downgrades (30d)
    'analyst_coverage_count': int,           # Number of analysts covering

    # Options Market Sentiment
    'put_call_ratio': float,                 # Put volume / Call volume
    'implied_volatility': float,             # ATM IV
    'iv_percentile': float,                  # IV rank (0-100)
    'options_flow_sentiment': float,         # Net bullish/bearish flow

    # Insider Activity
    'insider_buying_count': int,             # Number of insider buy transactions (90d)
    'insider_selling_count': int,            # Number of insider sell transactions (90d)
    'insider_net_value': float,              # $ value of net insider buying
    'insider_ownership_change': float,       # % change in insider ownership

    # Institutional Sentiment
    'institutional_ownership': float,        # % of shares held by institutions
    'institutional_ownership_change': float, # % change in inst. ownership (quarterly)
    'short_interest': float,                 # % of float shorted
    'short_interest_change': float,          # % change in short interest
    'days_to_cover': float,                  # Short interest / Avg daily volume
}
```

#### 3. Market Technical Metrics
Price action and technical indicators:

```python
market_technical = {
    # Price & Volume
    'close': float,                          # Closing price
    'open': float,
    'high': float,
    'low': float,
    'volume': float,
    'dollar_volume': float,                  # Price * Volume
    'vwap': float,                           # Volume-weighted average price

    # Returns
    'return_1d': float,                      # Daily return
    'return_5d': float,                      # 5-day return
    'return_20d': float,                     # 20-day return
    'return_60d': float,                     # 60-day return

    # Volatility
    'volatility_20d': float,                 # 20-day historical volatility
    'atr': float,                            # Average True Range
    'bollinger_width': float,                # Width of Bollinger Bands

    # Momentum Indicators
    'rsi_14': float,                         # 14-period RSI
    'macd': float,                           # MACD line
    'macd_signal': float,                    # MACD signal line
    'macd_histogram': float,                 # MACD - Signal
    'stochastic_k': float,                   # Stochastic %K
    'stochastic_d': float,                   # Stochastic %D

    # Trend Indicators
    'sma_20': float,                         # 20-day simple moving average
    'sma_50': float,                         # 50-day SMA
    'sma_200': float,                        # 200-day SMA
    'ema_12': float,                         # 12-day exponential MA
    'ema_26': float,                         # 26-day EMA
    'adx': float,                            # Average Directional Index (trend strength)

    # Support/Resistance
    'distance_from_52w_high': float,         # % from 52-week high
    'distance_from_52w_low': float,          # % from 52-week low
    'days_since_52w_high': int,
    'days_since_52w_low': int,
}
```

#### 4. Macro/External Metrics
Broader market and economic context:

```python
macro_external = {
    # Sector & Market
    'sector_return_1d': float,               # Sector index return (1d)
    'sector_return_5d': float,
    'sector_relative_strength': float,       # Stock return vs Sector return
    'market_return_spy': float,              # SPY return (1d)
    'market_correlation': float,             # 60-day correlation with SPY

    # Economic Indicators (for reference date)
    'interest_rate_10y': float,              # 10-year treasury yield
    'vix': float,                            # CBOE Volatility Index
    'dollar_index': float,                   # DXY US Dollar Index

    # Relative Metrics
    'beta': float,                           # Beta vs SPY
    'relative_volume': float,                # Volume / Avg volume
    'relative_strength_vs_market': float,    # Stock return vs market
}
```

#### 5. Risk Metrics
Quantitative risk measurements:

```python
risk_metrics = {
    # Drawdown
    'max_drawdown_60d': float,               # Max peak-to-trough decline (60d)
    'current_drawdown': float,               # Current % from peak

    # Risk-Adjusted Returns
    'sharpe_ratio': float,                   # (Return - RFR) / Volatility
    'sortino_ratio': float,                  # Return / Downside deviation

    # Value at Risk
    'var_95': float,                         # 95% Value at Risk (daily)
    'cvar_95': float,                        # Conditional VaR (expected shortfall)

    # Liquidity Risk
    'bid_ask_spread': float,                 # % spread
    'avg_daily_volume': float,               # 20-day average
    'volume_volatility': float,              # Std dev of volume
}
```

**Full DNA Schema Example Row**:

| timestamp | symbol | revenue | eps | news_sentiment_score | put_call_ratio | close | rsi_14 | sector_return_1d | beta | max_drawdown_60d |
|-----------|--------|---------|-----|---------------------|----------------|-------|--------|------------------|------|------------------|
| 2025-01-17 | AAPL | 123.5B | 2.10 | 0.65 | 0.85 | 185.50 | 58.3 | 0.012 | 1.15 | -0.08 |

---

### Layer 3: Feature Extraction (LLM/Neural AI)

**Purpose**: Analyze the standardized tabular "DNA" dataset and extract high-level, predictive features for trading signals

**Why LLM/Neural AI for Tabular Data?**

Traditional feature engineering requires domain expertise and manual selection. LLM-based and neural approaches can:
- Discover non-obvious correlations across 50+ columns
- Generate embeddings that capture complex relationships
- Identify regime changes and pattern shifts
- Perform multi-modal reasoning (combine numeric and text features)

**Potential Frameworks**:

1. **ToolOrchestra** ([arXiv:2511.21689](https://arxiv.org/pdf/2511.21689))
   - Orchestrates multiple LLMs and specialized tools
   - Routes queries to appropriate models
   - Cost-effective inference through model selection

2. **TabLLM / Tabular Foundation Models**
   - Models pre-trained on tabular data
   - Can handle mixed data types (numeric, categorical, text)
   - Transfer learning from large-scale financial datasets

3. **Custom Neural Architectures**
   - Transformer-based models for time-series tabular data
   - Attention mechanisms to weigh important features
   - Multi-task learning (predict returns, volatility, sentiment)

**Feature Extraction Tasks**:

```python
# Example Layer 3 Agent Interface
class FeatureExtractionAgent:
    """
    Takes standardized DNA dataset and outputs extracted features
    """

    def extract_features(self, dna_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Args:
            dna_data: Standardized tabular dataset with all metric groups

        Returns:
            extracted_features: {
                'latent_embeddings': np.ndarray,      # 128-dim embedding per stock
                'predicted_return_5d': float,         # 5-day forward return prediction
                'predicted_volatility': float,        # Expected volatility
                'regime_classification': str,         # 'bullish', 'bearish', 'neutral'
                'feature_importance': Dict[str, float], # Which features matter most
                'confidence_score': float,            # Model confidence
            }
        """
        pass
```

**Example Output**:

```json
{
  "symbol": "AAPL",
  "timestamp": "2025-01-17",
  "extracted_features": {
    "latent_embedding": [0.45, -0.23, 0.67, ...],  // 128-dimensional vector
    "predicted_return_5d": 0.028,                   // +2.8% expected return
    "predicted_volatility": 0.015,                  // 1.5% daily volatility
    "regime_classification": "bullish",
    "feature_importance": {
      "news_sentiment_score": 0.32,                // Most important feature
      "earnings_surprise": 0.28,
      "rsi_14": 0.15,
      "institutional_ownership_change": 0.12
    },
    "confidence_score": 0.87,                       // High confidence
    "trading_signal": "BUY",
    "risk_adjusted_score": 8.5                      // Out of 10
  }
}
```

---

### Data Flow Example

**Input**: Portfolio of 10 stocks

**Layer 1** → Retrieve data:
- Candlestick agent fetches OHLCV for 10 stocks
- Earnings agent fetches Q4 earnings for 10 stocks
- News agent fetches 50 articles across 10 stocks
- Social agent fetches 1000+ tweets/posts

**Layer 2** → Normalize:
- Filter out duplicate articles
- Sync all timestamps to market close (16:00 EST)
- Map all tickers to standard format
- Create unified table: 10 rows (one per stock) × 80+ columns (all metrics)

**Layer 3** → Extract features:
- LLM/neural model reads the 10×80 table
- Generates embeddings for each stock
- Predicts 5-day returns, identifies key drivers
- Outputs trading signals for each stock

**Final Output**:
```
Symbol | Signal | Confidence | Expected Return | Key Drivers
-------|--------|------------|-----------------|-------------
AAPL   | BUY    | 87%        | +2.8%          | Earnings surprise, Positive sentiment
MSFT   | HOLD   | 72%        | +0.5%          | Neutral signals
TSLA   | SELL   | 91%        | -3.2%          | High put/call ratio, Insider selling
...
```

---

### Benefits of Three-Layer Architecture

1. **Modularity**: Each layer can be developed, tested, and scaled independently
2. **Standardization**: Layer 2 creates a single source of truth (DNA dataset)
3. **Flexibility**: Easy to add new data sources (Layer 1) without changing downstream
4. **Intelligence**: Layer 3 can apply cutting-edge ML/LLM techniques
5. **Scalability**: Parallel processing at each layer
6. **Debuggability**: Can inspect data quality at each layer boundary

---

### Implementation Roadmap

**Phase 1: Build Layer 1** (Current Focus)
- ✅ Candlestick agent
- ✅ Earnings report agent
- ✅ News agent
- 🔄 Options flow agent
- 🔄 Social media agent
- 🔄 SEC filings agent

**Phase 2: Build Layer 2**
- 📋 Define full DNA schema (80+ columns)
- 📋 Build normalization agents
- 📋 Implement time sync and symbol mapping
- 📋 Create standardized output format (Parquet/CSV)

**Phase 3: Build Layer 3**
- 📋 Research tabular LLM frameworks
- 📋 Train/fine-tune models on financial data
- 📋 Build feature extraction pipeline
- 📋 Integrate with trading signal generation

**Phase 4: Orchestration**
- 📋 Connect all three layers with message queues
- 📋 Implement monitoring and alerting
- 📋 Add caching and optimization
- 📋 Deploy to production

---

## Current Architecture

### Single Container, Multiple Agents

```
┌──────────────────────────────────────┐
│         Docker Container             │
│                                      │
│  ┌────────────────────────────────┐ │
│  │          main.py               │ │
│  │                                │ │
│  │  ┌──────────────────────────┐ │ │
│  │  │   config.yaml loader     │ │ │
│  │  └──────────────────────────┘ │ │
│  │                                │ │
│  │  if news_agent enabled:       │ │
│  │    ┌─────────────────┐        │ │
│  │    │  News Agent     │        │ │
│  │    │  - execute()    │        │ │
│  │    └─────────────────┘        │ │
│  │                                │ │
│  │  if report_agent enabled:     │ │
│  │    ┌─────────────────┐        │ │
│  │    │  Report Agent   │        │ │
│  │    │  - execute()    │        │ │
│  │    └─────────────────┘        │ │
│  │                                │ │
│  │  Save results to JSON         │ │
│  └────────────────────────────────┘ │
│                                      │
└──────────────────────────────────────┘
```

**Characteristics**:
- ✅ Simple, easy to deploy
- ✅ Low overhead
- ✅ Good for 2-5 agents
- ❌ Not scalable to 10+ agents
- ❌ All agents run sequentially
- ❌ No parallel processing
- ❌ Single point of failure

---

## Future Architecture (Multi-Agent)

### Microservices Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                           │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              API Gateway / Orchestrator                   │ │
│  │  - Receives portfolio requests                            │ │
│  │  - Dispatches work to agents                              │ │
│  │  - Aggregates results                                     │ │
│  │  - Handles errors and retries                             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                            │                                    │
│          ┌─────────────────┴──────────────────┐                │
│          ▼                 ▼                   ▼                │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐        │
│  │  News Agent   │ │ Report Agent  │ │ Sentiment     │        │
│  │  (Pod)        │ │  (Pod)        │ │  Agent (Pod)  │        │
│  │               │ │               │ │               │        │
│  │  - REST API   │ │  - REST API   │ │  - REST API   │        │
│  │  - Health chk │ │  - Health chk │ │  - Health chk │        │
│  └───────────────┘ └───────────────┘ └───────────────┘        │
│                                                                 │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐        │
│  │ Technical     │ │ Balance Sheet │ │  Risk         │        │
│  │ Analysis      │ │  Agent        │ │  Analysis     │        │
│  │  (Pod)        │ │  (Pod)        │ │  Agent (Pod)  │        │
│  └───────────────┘ └───────────────┘ └───────────────┘        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Message Queue (Redis/RabbitMQ)               │ │
│  │  - Task distribution                                      │ │
│  │  - Result collection                                      │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │               Database (PostgreSQL)                       │ │
│  │  - Portfolio data                                         │ │
│  │  - Historical results                                     │ │
│  │  - Execution logs                                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │               Cache Layer (Redis)                         │ │
│  │  - API response caching                                   │ │
│  │  - Rate limit tracking                                    │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Characteristics**:
- ✅ Highly scalable (10+ agents)
- ✅ Parallel execution
- ✅ Independent agent deployment
- ✅ Fault tolerance (if one agent fails, others continue)
- ✅ Easy to add new agents
- ❌ More complex to set up
- ❌ Higher infrastructure cost

---

## Adding New Agents

### Step 1: Create Agent Class

**`agents/sentiment_agent.py`**:

```python
"""Sentiment Analysis Agent"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from transformers import pipeline  # or your sentiment library


class SentimentAgent(BaseAgent):
    """Agent for analyzing sentiment of news articles"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("sentiment_agent", config)

        # Initialize sentiment model
        self.model_name = self.get_config("model_name", "finbert-tone")
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=f"ProsusAI/{self.model_name}"
        )

    def _execute_internal(self, input_data: Any) -> Dict[str, Any]:
        """
        Analyze sentiment of news articles

        Args:
            input_data: Dict with "articles" key

        Returns:
            Dict with sentiment scores per article
        """
        articles = input_data.get("articles", [])

        sentiments = []
        for article in articles:
            text = article.get("title", "") + " " + article.get("description", "")

            # Analyze sentiment
            result = self.sentiment_analyzer(text)[0]

            sentiments.append({
                "article_id": article.get("url"),
                "sentiment": result["label"],  # positive/negative/neutral
                "confidence": result["score"],
                "symbol": article.get("symbol")
            })

        return {
            "total_articles": len(articles),
            "sentiments": sentiments,
            "average_sentiment": self._calculate_average(sentiments)
        }

    def _calculate_average(self, sentiments):
        """Calculate average sentiment score"""
        # Implementation here
        pass
```

### Step 2: Register Agent in Config

**`config.yaml`**:

```yaml
agents:
  news_agent:
    enabled: true
    config:
      max_articles_per_stock: 5
      days_back: 7

  report_agent:
    enabled: true
    config:
      include_financials: true

  # NEW: Sentiment Agent
  sentiment_agent:
    enabled: true
    config:
      model_name: "finbert-tone"
      batch_size: 32
```

### Step 3: Update main.py

**`main.py`** (add sentiment agent):

```python
from agents.sentiment_agent import SentimentAgent

# In run_with_config():
if config.is_agent_enabled('sentiment_agent'):
    try:
        print_section("EXECUTING SENTIMENT AGENT", "=")
        agent_config = config.get_agent_config('sentiment_agent')
        sentiment_agent = SentimentAgent(config=agent_config)

        # Get articles from news agent result
        articles = news_result['result']['news_by_stock']

        print("🔄 Running Sentiment Agent...")
        sentiment_result = sentiment_agent.execute({"articles": articles})
        results['sentiment'] = sentiment_result

        # Display and save
        display_sentiment_results(sentiment_result)
        sentiment_file = save_results(sentiment_result, "sentiment_results.json")
        print(f"\n💾 Saved: {sentiment_file}")
    except Exception as e:
        print(f"❌ Sentiment Agent failed: {str(e)}")
```

### Step 4: Add Agent Dockerfile (Optional - Microservices)

**`agents/sentiment_agent/Dockerfile`**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements-sentiment.txt .
RUN pip install --no-cache-dir -r requirements-sentiment.txt

# Copy agent code
COPY agents/base_agent.py agents/
COPY agents/sentiment_agent.py agents/
COPY services/ services/

# Create API wrapper
COPY api_wrapper.py .

# Expose port
EXPOSE 8000

# Run as API
CMD ["uvicorn", "api_wrapper:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Agent Orchestration

### Pattern 1: Sequential (Current)

```python
# main.py
results = {}

# Run agents one by one
if enabled('news_agent'):
    results['news'] = news_agent.execute(portfolio)

if enabled('report_agent'):
    results['reports'] = report_agent.execute(portfolio)

if enabled('sentiment_agent'):
    # Uses news results
    results['sentiment'] = sentiment_agent.execute(results['news'])
```

**Pros**: Simple, easy to debug
**Cons**: Slow (each agent waits for previous)

---

### Pattern 2: Parallel (Independent Agents)

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def run_agents_parallel(portfolio):
    """Run independent agents in parallel"""

    with ThreadPoolExecutor(max_workers=5) as executor:
        # Launch all agents simultaneously
        futures = []

        if enabled('news_agent'):
            futures.append(executor.submit(news_agent.execute, portfolio))

        if enabled('report_agent'):
            futures.append(executor.submit(report_agent.execute, portfolio))

        # Wait for all to complete
        results = [f.result() for f in futures]

    return results
```

**Pros**: Fast (agents run simultaneously)
**Cons**: More complex, requires thread-safe agents

---

### Pattern 3: DAG (Directed Acyclic Graph)

For agents with dependencies:

```python
from typing import Dict, List, Callable

class AgentOrchestrator:
    """Orchestrate agents with dependencies"""

    def __init__(self):
        self.agents = {}
        self.dependencies = {}

    def register_agent(self, name: str, agent: BaseAgent, depends_on: List[str] = None):
        """Register agent and its dependencies"""
        self.agents[name] = agent
        self.dependencies[name] = depends_on or []

    def execute(self, portfolio: Dict) -> Dict:
        """Execute agents in dependency order"""

        results = {}
        executed = set()

        def can_execute(agent_name: str) -> bool:
            """Check if dependencies are satisfied"""
            deps = self.dependencies[agent_name]
            return all(dep in executed for dep in deps)

        while len(executed) < len(self.agents):
            # Find agents ready to execute
            ready = [name for name in self.agents if name not in executed and can_execute(name)]

            if not ready:
                raise RuntimeError("Circular dependency detected")

            # Execute ready agents in parallel
            for agent_name in ready:
                agent = self.agents[agent_name]

                # Prepare input (include results from dependencies)
                input_data = {"portfolio": portfolio}
                for dep in self.dependencies[agent_name]:
                    input_data[dep] = results[dep]

                # Execute
                results[agent_name] = agent.execute(input_data)
                executed.add(agent_name)

        return results

# Usage:
orchestrator = AgentOrchestrator()

# Register agents with dependencies
orchestrator.register_agent("news_agent", news_agent, depends_on=[])
orchestrator.register_agent("report_agent", report_agent, depends_on=[])
orchestrator.register_agent("sentiment_agent", sentiment_agent, depends_on=["news_agent"])
orchestrator.register_agent("summary_agent", summary_agent, depends_on=["news_agent", "report_agent", "sentiment_agent"])

# Execute all
results = orchestrator.execute(portfolio)
```

**Dependency Graph**:
```
news_agent ────────┐
                   ├──→ sentiment_agent ───┐
report_agent ──────┘                       ├──→ summary_agent
                                           │
technical_agent ───────────────────────────┘
```

**Pros**: Handles complex dependencies, maximizes parallelism
**Cons**: Most complex to implement

---

## Communication Patterns

### Pattern 1: Shared Database

```
Agent 1 → Write to DB → Agent 2 reads from DB
```

**Implementation**:
```python
# Agent 1 saves results
db.save_results(portfolio_id, results)

# Agent 2 retrieves
previous_results = db.get_results(portfolio_id)
```

---

### Pattern 2: Message Queue (Redis/RabbitMQ)

```
Agent 1 → Publish message → Queue → Agent 2 subscribes
```

**Implementation**:
```python
import redis

r = redis.Redis()

# Agent 1 publishes
r.publish('news_complete', json.dumps(news_results))

# Agent 2 subscribes
pubsub = r.pubsub()
pubsub.subscribe('news_complete')
for message in pubsub.listen():
    if message['type'] == 'message':
        news_results = json.loads(message['data'])
        # Process
```

---

### Pattern 3: API Calls

```
Orchestrator → HTTP POST → Agent API → Response
```

**Agent API** (`api_wrapper.py`):
```python
from fastapi import FastAPI
from agents.news_agent import NewsAgent

app = FastAPI()
agent = NewsAgent()

@app.post("/execute")
async def execute_agent(portfolio: dict):
    result = agent.execute(portfolio)
    return result

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

**Orchestrator calls**:
```python
import httpx

async with httpx.AsyncClient() as client:
    # Call news agent
    response = await client.post(
        "http://news-agent-service:8000/execute",
        json={"portfolio": portfolio}
    )
    news_results = response.json()
```

---

## Deployment Strategies

### Strategy 1: Single Container (Current)

**When to use**: 2-5 agents, simple deployment

```yaml
# docker-compose.yml
services:
  event-horizon:
    image: event-horizon:latest
    # All agents in one container
```

---

### Strategy 2: Sidecar Pattern

**When to use**: 5-10 agents, shared resources

```yaml
services:
  main-app:
    image: event-horizon-orchestrator:latest

  news-agent:
    image: news-agent:latest

  report-agent:
    image: report-agent:latest

  sentiment-agent:
    image: sentiment-agent:latest
```

---

### Strategy 3: Kubernetes Microservices

**When to use**: 10+ agents, high scale

```yaml
# k8s/news-agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: news-agent
spec:
  replicas: 3  # Scale independently
  template:
    spec:
      containers:
      - name: news-agent
        image: news-agent:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: news-agent-service
spec:
  selector:
    app: news-agent
  ports:
  - port: 8000
```

---

## Monitoring & Observability

### Metrics to Track

```python
from prometheus_client import Counter, Histogram, Gauge

# Agent execution metrics
agent_executions = Counter('agent_executions_total', 'Total agent executions', ['agent_name', 'status'])
agent_duration = Histogram('agent_duration_seconds', 'Agent execution duration', ['agent_name'])
agent_errors = Counter('agent_errors_total', 'Total agent errors', ['agent_name', 'error_type'])

# Usage in BaseAgent
class BaseAgent(ABC):
    def execute(self, input_data: Any) -> Dict[str, Any]:
        start_time = time.time()

        try:
            result = self._execute_internal(input_data)
            agent_executions.labels(agent_name=self.agent_name, status='success').inc()
            return result
        except Exception as e:
            agent_errors.labels(agent_name=self.agent_name, error_type=type(e).__name__).inc()
            raise
        finally:
            duration = time.time() - start_time
            agent_duration.labels(agent_name=self.agent_name).observe(duration)
```

### Logging

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "agent_execution_started",
    agent_name=self.agent_name,
    portfolio_id=portfolio_id,
    execution_id=execution_id
)
```

### Tracing

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("agent_execution") as span:
    span.set_attribute("agent.name", self.agent_name)
    span.set_attribute("portfolio.id", portfolio_id)

    result = self._execute_internal(input_data)
```

---

## Roadmap: Scaling to 20+ Agents

### Phase 1: Current (2-5 agents)
- ✅ Single container deployment
- ✅ Sequential execution
- ✅ Config-based enabling

### Phase 2: Parallel (5-10 agents)
- 🔄 Add async execution
- 🔄 Implement parallel agent runs
- 🔄 Add result aggregation

### Phase 3: Microservices (10-20 agents)
- 📋 Convert agents to REST APIs
- 📋 Deploy on Kubernetes
- 📋 Add message queue (Redis)
- 📋 Implement orchestrator service

### Phase 4: Enterprise (20+ agents)
- 📋 Add database persistence
- 📋 Implement caching layer
- 📋 Add comprehensive monitoring
- 📋 Auto-scaling based on load
- 📋 Multi-region deployment

---

## Quick Migration Guide

### From Monolith to Microservices

1. **Add FastAPI wrapper to each agent**
2. **Create separate Dockerfiles**
3. **Deploy to Kubernetes**
4. **Add orchestrator service**
5. **Migrate gradually** (start with one agent as microservice)

See full guide: `docs/migration-to-microservices.md` (coming soon)

---

## Summary

**Current**: Simple, works for 2-5 agents
**Future**: Scalable, supports 20+ agents with orchestration

**Next Steps**:
1. Keep current architecture until you have 5+ agents
2. When scaling, start with parallel execution
3. Move to microservices when you have 10+ agents
4. Use Kubernetes for production scale

Ready to scale? Start by adding your next agent using the guide above!
