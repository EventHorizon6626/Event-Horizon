# Earnings Agent (formerly Report Analysis Agent) - Design Document

## Overview

The **Earnings Agent** (renamed from Report Analysis Agent) retrieves financial reports for securities in a portfolio:
- **Stocks**: Earnings reports (quarterly earnings, annual reports, financial statements)
- **ETFs**: Fund reports (holdings, performance, expense ratios, fund details)
- **Mutual Funds**: Fund information and metrics

**Location**: `event_horizon/data_pipeline/stage_1/agents/earnings_agent.py`
**Service**: `event_horizon/data_pipeline/stage_1/services/financial_data_client.py`

## Architecture

### Agent Responsibilities

1. **Security Type Identification**: Determine if symbol is stock, ETF, mutual fund, etc.
2. **Report Retrieval**: Fetch appropriate reports based on security type
3. **Data Standardization**: Format reports into consistent `EarningsData` structure
4. **Error Handling**: Handle missing data, API failures gracefully

### Data Flow

```
Portfolio Input -> Security Type Detection -> Report Fetching -> Data Formatting -> EarningsData
     |                    |                       |                  |               |
 [AAPL, SPY]      [Stock, ETF]          [Earnings, Fund]    [Standardize]    [Structured Output]
```

### Integration in Pipeline

```
Stage 1 Orchestrator (parallel)
  |-- CandlestickAgent  -> Yahoo Finance
  |-- EarningsAgent      -> Yahoo Finance       <-- this agent
  |-- NewsAgent          -> Tavily / Exa
  |-- TechnicalAgent     -> yfinance
  +-- FundamentalsAgent  -> yfinance
```

## Data Models

### Output: EarningsData

```python
@dataclass
class EarningsData:
    symbol: str
    security_type: str       # stock, etf, mutual_fund
    name: str
    earnings_reports: Dict   # Quarterly/annual earnings
    financial_statements: Dict  # Income, balance sheet, cash flow
    metrics: Dict            # Key financial metrics
    fund_info: Dict          # For ETFs/mutual funds
    error: Optional[str]
```

## Data Source: yfinance (Yahoo Finance)

The Earnings Agent uses **yfinance** via the `FinancialDataClient` service.

**Data Available**:
- Security type identification (`info['quoteType']`)
- Earnings calendar and history
- Financial statements (income, balance sheet, cash flow)
- Fund information for ETFs
- Key metrics (market cap, P/E, dividend yield, etc.)

**No API key required** -- yfinance is free.

## Configuration

```python
{
    "include_financials": True,    # Include full financial statements
    "earnings_periods": 4,        # Number of quarters to retrieve
    "top_holdings": 10            # Top N holdings for ETFs
}
```

## Usage

### Via FastAPI

```bash
curl -X POST http://localhost:8030/agents/earnings \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "SPY", "QQQ"]}'
```

### Via Python

```python
from event_horizon.data_pipeline.stage_1.agents.earnings_agent import EarningsAgent

config = {
    "include_financials": True,
    "earnings_periods": 4,
    "top_holdings": 10
}
agent = EarningsAgent(config=config)
result = agent.execute({"portfolio": ["AAPL", "SPY", "GOOGL"]})

for symbol, data in result["result"].items():
    print(f"{symbol} ({data.security_type}): {data.name}")
```

## Error Handling

- Returns `EarningsData` with `error` field set on failure
- Handles unknown security types gracefully
- Stage 1 orchestrator continues with partial results if this agent fails

## Future Enhancements

1. **SEC EDGAR Integration**: Download official 10-K, 10-Q filings
2. **Earnings Surprise Analysis**: Quantify earnings beats/misses
3. **Historical Trends**: Multi-year earnings growth analysis
4. **Peer Comparison**: Compare metrics to industry peers

## References

- [yfinance Documentation](https://github.com/ranaroussi/yfinance)
- [SEC EDGAR](https://www.sec.gov/edgar/searchedgar/companysearch.html)
- [Yahoo Finance](https://finance.yahoo.com/)

---

**Document Version**: 2.0
**Last Updated**: 2026-02-10
