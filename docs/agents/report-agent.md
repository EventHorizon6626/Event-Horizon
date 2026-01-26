# Report Analysis Agent - Design Document

## Overview

The Report Analysis Agent retrieves financial reports for securities in a portfolio:
- **Stocks**: Earnings reports (quarterly earnings, annual reports, earnings calls)
- **ETFs**: Fund reports (holdings, performance, expense ratios, fund details)
- **Other**: Equivalent financial disclosures

## Architecture

### Agent Responsibilities

1. **Security Type Identification**: Determine if symbol is stock, ETF, mutual fund, etc.
2. **Report Retrieval**: Fetch appropriate reports based on security type
3. **Data Standardization**: Format reports into consistent structure
4. **Error Handling**: Handle missing data, API failures gracefully

### Data Flow

```
Portfolio Input → Security Type Detection → Report Fetching → Data Formatting → Structured Output
     ↓                    ↓                       ↓                  ↓               ↓
 [AAPL, SPY]      [Stock, ETF]          [Earnings, Fund]    [Standardize]    [JSON Results]
```

## Data Models

### Input Format

```python
{
    "portfolio_id": "port_001",
    "user_id": "user_123",
    "portfolio": ["AAPL", "SPY", "GOOGL", "QQQ"]
}
```

### Output Format

```python
{
    "portfolio_id": "port_001",
    "status": "success",  # success | partial_success | failed
    "reports_by_symbol": {
        "AAPL": {
            "symbol": "AAPL",
            "security_type": "stock",
            "company_name": "Apple Inc.",
            "reports": {
                "earnings": {
                    "quarterly": [...],  # Last 4 quarters
                    "annual": [...]      # Last 3 years
                },
                "calendar": {...},       # Upcoming earnings dates
                "financials": {
                    "income_statement": {...},
                    "balance_sheet": {...},
                    "cash_flow": {...}
                }
            },
            "retrieved_at": "2024-01-15T10:30:00Z"
        },
        "SPY": {
            "symbol": "SPY",
            "security_type": "etf",
            "fund_name": "SPDR S&P 500 ETF Trust",
            "reports": {
                "fund_info": {
                    "category": "Large Blend",
                    "total_assets": "...",
                    "expense_ratio": 0.0945,
                    "inception_date": "1993-01-22",
                    "manager": "State Street"
                },
                "holdings": [...],       # Top holdings
                "performance": {...},     # Historical returns
                "distributions": [...]    # Dividend history
            },
            "retrieved_at": "2024-01-15T10:30:05Z"
        }
    },
    "total_reports": 2,
    "stocks_processed": 4,
    "errors": [],
    "config_used": {...}
}
```

### Earnings Report Structure (Stocks)

```python
{
    "date": "2024-01-25",
    "fiscal_quarter": "Q1 2024",
    "fiscal_year": 2024,
    "reported": True,  # False if estimated
    "revenue": {
        "actual": 119.58,  # in billions
        "estimated": 117.91,
        "surprise_pct": 1.42
    },
    "earnings_per_share": {
        "actual": 2.18,
        "estimated": 2.10,
        "surprise_pct": 3.81
    },
    "report_time": "AMC",  # AMC = after market close, BMO = before market open
    "report_url": "https://..."
}
```

### Fund Report Structure (ETFs)

```python
{
    "fund_info": {
        "name": "SPDR S&P 500 ETF Trust",
        "category": "Large Blend",
        "family": "SPDR State Street Global Advisors",
        "total_assets": 450000000000,  # $450B
        "expense_ratio": 0.0945,
        "yield": 1.45,
        "inception_date": "1993-01-22"
    },
    "holdings": [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "weight": 7.1,  # percentage
            "shares": 175000000,
            "value": 30000000000
        },
        # ... top 10 holdings
    ],
    "sector_allocation": {
        "Technology": 28.5,
        "Healthcare": 13.2,
        "Financials": 12.8,
        # ...
    },
    "performance": {
        "1_month": 2.5,
        "3_month": 8.2,
        "ytd": 15.3,
        "1_year": 24.5,
        "3_year_avg": 12.1,
        "5_year_avg": 15.7
    }
}
```

## API Selection

### Option 1: yfinance (Recommended for MVP)
**Pros**:
- Free, no API key required
- Comprehensive data for stocks and ETFs
- Easy to use Python library
- Active community support

**Cons**:
- Unofficial API (scrapes Yahoo Finance)
- Rate limiting possible
- No guaranteed SLA
- May break if Yahoo changes structure

**Data Available**:
- Security type identification
- Earnings calendar and history
- Financial statements
- Fund information for ETFs
- Holdings data

### Option 2: Financial Modeling Prep (Production)
**Pros**:
- Official API with SLA
- 250 requests/day free tier
- Comprehensive financial data
- SEC filings integration

**Cons**:
- Requires API key
- Rate limits on free tier
- Limited ETF data

**Pricing**: Free (250/day) → $15/mo (300/day) → $30/mo (750/day)

### Option 3: Alpha Vantage
**Pros**:
- Free tier available
- Good earnings data
- Official API

**Cons**:
- 5 calls/minute, 500/day free limit
- Limited ETF data
- Requires API key

### Option 4: Polygon.io
**Pros**:
- Real-time and historical data
- Reference data for security types
- Earnings and financials

**Cons**:
- $99/month (free tier very limited)
- Overkill for basic reports

## Implementation Strategy

### Phase 1: MVP with yfinance
1. Use yfinance for both stocks and ETFs
2. Identify security type using `info['quoteType']`
3. Fetch earnings for stocks: `ticker.earnings`, `ticker.quarterly_earnings`, `ticker.calendar`
4. Fetch fund data for ETFs: `ticker.info`, `ticker.holdings`
5. Implement retry logic and caching

### Phase 2: Enhanced Features
1. Add Financial Modeling Prep as alternative data source
2. Implement caching stage (24-hour cache for reports)
3. Add SEC EDGAR direct access for official filings
4. Parallel processing for multiple symbols
5. Add earnings call transcripts (from third-party providers)

### Phase 3: Advanced Analysis
1. Historical earnings trend analysis
2. Earnings surprise patterns
3. Fund performance comparison
4. Holdings overlap analysis
5. Sector exposure analysis

## Component Design

### 1. FinancialDataClient (`services/financial_data_client.py`)

```python
class FinancialDataClient:
    """Client for fetching financial reports and data"""

    def get_security_type(self, symbol: str) -> str:
        """Determine if symbol is stock, ETF, mutual fund, etc."""

    def get_stock_earnings(self, symbol: str) -> Dict:
        """Fetch earnings reports for stock"""

    def get_etf_reports(self, symbol: str) -> Dict:
        """Fetch fund information and holdings for ETF"""

    def get_financial_statements(self, symbol: str) -> Dict:
        """Fetch income statement, balance sheet, cash flow"""
```

### 2. ReportAnalysisAgent (`agents/report_agent.py`)

```python
class ReportAnalysisAgent(BaseAgent):
    """Agent for retrieving financial reports"""

    def _execute_internal(self, input_data: Any) -> Dict:
        """
        1. Parse portfolio input
        2. For each symbol:
           - Identify security type
           - Fetch appropriate reports
           - Format and aggregate
        3. Return structured results
        """
```

## Error Handling

### Common Errors

1. **Symbol Not Found**: Invalid or delisted symbol
2. **No Data Available**: Symbol exists but no earnings/fund data
3. **API Rate Limit**: Too many requests
4. **Network Timeout**: Connection issues
5. **Data Format Changed**: Unexpected API response structure

### Handling Strategy

- Return empty reports with error flag instead of failing
- Use `partial_success` status when some symbols fail
- Log all errors for debugging
- Implement retry logic with exponential backoff
- Cache successful responses to reduce API calls

## Configuration Options

```python
agent_config = {
    "data_source": "yfinance",  # yfinance | fmp | alpha_vantage
    "cache_enabled": True,
    "cache_ttl_hours": 24,
    "earnings_periods": 4,      # Number of quarters to retrieve
    "top_holdings": 10,         # Top N holdings for ETFs
    "include_financials": True  # Include full financial statements
}
```

## Testing Strategy

### Unit Tests

1. Test security type identification
2. Test earnings data parsing
3. Test ETF data parsing
4. Test error handling
5. Mock API responses

### Integration Tests

1. Test with real symbols (AAPL, SPY, etc.)
2. Test with invalid symbols
3. Test with mixed portfolio
4. Test rate limiting behavior

### Test Portfolio

```python
test_portfolio = {
    "portfolio_id": "test_reports_001",
    "portfolio": [
        "AAPL",   # Large cap stock
        "SPY",    # S&P 500 ETF
        "QQQ",    # Nasdaq 100 ETF
        "TSLA",   # Growth stock
        "INVALID" # Should handle gracefully
    ]
}
```

## Usage Example

```python
from agents.report_agent import ReportAnalysisAgent

# Create agent
config = {
    "earnings_periods": 4,
    "top_holdings": 10,
    "include_financials": True
}
agent = ReportAnalysisAgent(config=config)

# Execute
portfolio = {
    "portfolio_id": "my_portfolio",
    "portfolio": ["AAPL", "SPY", "GOOGL"]
}
result = agent.execute(portfolio)

# Access results
for symbol, report in result['result']['reports_by_symbol'].items():
    print(f"{symbol} ({report['security_type']})")
    if report['security_type'] == 'stock':
        earnings = report['reports']['earnings']['quarterly']
        print(f"  Latest EPS: ${earnings[0]['earnings_per_share']['actual']}")
    elif report['security_type'] == 'etf':
        info = report['reports']['fund_info']
        print(f"  Expense Ratio: {info['expense_ratio']}%")
```

## Integration with News Agent

Both agents can be used together for comprehensive portfolio analysis:

```python
news_agent = NewsAgent(config=news_config)
report_agent = ReportAnalysisAgent(config=report_config)

# Get both news and reports
news_result = news_agent.execute(portfolio)
report_result = report_agent.execute(portfolio)

# Combine insights
combined_analysis = {
    "portfolio_id": portfolio['portfolio_id'],
    "news": news_result['result'],
    "reports": report_result['result'],
    "timestamp": datetime.now().isoformat()
}
```

## Future Enhancements

1. **Earnings Surprise Analysis**: Quantify earnings beats/misses
2. **Guidance Tracking**: Track forward guidance from companies
3. **Earnings Call Sentiment**: Analyze tone from transcripts
4. **Peer Comparison**: Compare metrics to industry peers
5. **Historical Trends**: Multi-year earnings growth analysis
6. **ETF Performance Attribution**: Analyze what drives fund returns
7. **Holdings Change Tracking**: Track when funds rebalance
8. **Dividend Analysis**: Dividend growth, yield, payout ratios

## Security Considerations

1. **API Key Management**: Store keys in environment variables
2. **Rate Limiting**: Respect API rate limits to avoid bans
3. **Data Privacy**: Don't log sensitive portfolio information
4. **Input Validation**: Sanitize stock symbols to prevent injection
5. **Error Messages**: Don't expose internal details to end users

## Performance Optimization

1. **Caching**: Cache report data for 24 hours
2. **Parallel Requests**: Fetch multiple symbols concurrently
3. **Lazy Loading**: Only fetch detailed financials if requested
4. **Batch API Calls**: Use batch endpoints when available
5. **Connection Pooling**: Reuse HTTP connections

## Monitoring and Logging

```python
# Log structure
{
    "agent": "report_agent",
    "execution_id": "uuid",
    "symbol": "AAPL",
    "security_type": "stock",
    "data_source": "yfinance",
    "reports_retrieved": ["earnings", "financials"],
    "execution_time_ms": 1250,
    "status": "success"
}
```

Track metrics:
- Average execution time per symbol
- Success rate by security type
- API error rates
- Cache hit ratio
- Data freshness

## References

- [yfinance Documentation](https://github.com/ranaroussi/yfinance)
- [Financial Modeling Prep API](https://financialmodelingprep.com/developer/docs)
- [Alpha Vantage API](https://www.alphavantage.co/documentation/)
- [SEC EDGAR](https://www.sec.gov/edgar/searchedgar/companysearch.html)
- [Yahoo Finance](https://finance.yahoo.com/)
