# Event Horizon - Data Sources Explained

## Current Data Sources

Event Horizon uses multiple data sources across its pipeline:

| Source | Used By | Type | API Key Required |
|--------|---------|------|------------------|
| **Yahoo Finance (yfinance)** | CandlestickAgent, EarningsAgent, TechnicalAgent, FundamentalsAgent | Financial data | No (free) |
| **Tavily** | NewsAgent, web_search | News/web search | Yes (`TAVILY_API_KEY`) |
| **Exa** | NewsAgent (fallback), web_search (fallback) | News/web search | Yes (`EXASEARCH_API_KEY`) |
| **Massive.com** | CandlestickAgent (alternative) | OHLCV chart data | Yes (`MASSIVE_API_KEY`) |

---

## Yahoo Finance (yfinance)

### What It Provides

The primary data source for most Stage 1 agents.

#### For Stocks:
- OHLCV price data (candlestick charts)
- Earnings reports (quarterly/annual)
- Financial statements (income, balance sheet, cash flow)
- Key metrics (P/E, ROE, market cap, etc.)
- Technical indicator inputs (price history for SMA, RSI, MACD)
- Fundamental metrics (valuation, profitability, growth, dividends)

#### For ETFs:
- Fund information (expense ratio, total assets, yield)
- Top holdings
- Performance history
- Distribution history

#### For Mutual Funds:
- Fund characteristics and metrics
- Holdings data

### Agents Using yfinance

| Agent | What It Gets |
|-------|-------------|
| CandlestickAgent | OHLCV candles via `ChartDataClient` |
| EarningsAgent | Earnings, financials, metrics via `FinancialDataClient` |
| TechnicalAgent | Price history for indicator calculations via `stock_tools.py` |
| FundamentalsAgent | Company info, ratios via `stock_tools.py` |

### Pros & Cons

**Pros**:
- Free, no API key required
- Comprehensive data for stocks, ETFs, mutual funds
- Easy to use Python library
- Active community

**Cons**:
- Unofficial API (scrapes Yahoo Finance)
- Rate limiting possible
- No guaranteed SLA
- Not official SEC data

---

## Tavily Search API

### What It Provides

Primary source for **news articles** and **web search** results.

**Used By**:
- `NewsAgent` (Stage 1) via `news_search_client.py` -> `tavily_news_search()`
- `web_search` tool (FastAPI app) via `services/web_search.py`
- Thinking agent tool calls

### Features
- Financial news search with relevance ranking
- Structured article results (title, URL, source, content)
- Answer synthesis for web search queries
- Good coverage of financial news

### Configuration
```bash
TAVILY_API_KEY=your_tavily_key
```

---

## Exa Search API

### What It Provides

**Fallback** for Tavily in both news retrieval and web search.

**Used By**:
- `NewsAgent` (Stage 1) via `news_search_client.py` -> `exa_news_search()` (when Tavily fails)
- `web_search` tool via `services/web_search.py` (when Tavily fails)

### Configuration
```bash
EXASEARCH_API_KEY=your_exa_key
```

---

## Massive.com

### What It Provides

**Alternative** to Yahoo Finance for OHLCV chart data. Professional-grade market data with higher rate limits and real-time data options.

**Used By**: `CandlestickAgent` (when `USE_MASSIVE_API=true`)

### Configuration
```bash
MASSIVE_API_KEY=your_massive_key
USE_MASSIVE_API=true  # Set to true to use instead of Yahoo Finance
```

See [Massive API Setup Guide](./massive-api-setup.md) for details.

---

## Data Source Comparison

| Feature | yfinance | Tavily | Exa | Massive.com |
|---------|----------|--------|-----|-------------|
| **Data Type** | Financial data | News/web search | News/web search | OHLCV charts |
| **Cost** | Free | Paid (API key) | Paid (API key) | Paid (API key) |
| **Rate Limits** | Unofficial | Per plan | Per plan | Per plan |
| **Reliability** | Good (unofficial) | High | High | High |
| **Real-time** | Delayed | Near real-time | Near real-time | Plan-dependent |
| **Used For** | Prices, earnings, fundamentals, technicals | News, web search | News fallback | Chart data (alt) |

---

## Legacy: NewsAPI.org

The `news_api_client.py` file still exists in `event_horizon/data_pipeline/stage_1/services/` for backward compatibility, but it is **no longer used** by the current News Agent. The migration from NewsAPI.org to Tavily/Exa provides:

- Better financial news relevance
- No free-tier article content truncation
- More reliable search results
- Integrated web search capability

---

## Official SEC Filings

SEC EDGAR integration is not yet implemented but planned as a future enhancement. See the original data-sources discussion for details on SEC filing types (10-K, 10-Q, 8-K, etc.).

---

## Recommended Setup

### Minimum (free):
- yfinance for all financial data (no API key needed)
- News agent will be limited without Tavily/Exa keys

### Standard:
- yfinance + `TAVILY_API_KEY` for full news/web search support
- This covers all current functionality

### Full:
- yfinance + `TAVILY_API_KEY` + `EXASEARCH_API_KEY` (fallback) + `MASSIVE_API_KEY` (professional charts)
