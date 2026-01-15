# Event Horizon - Data Sources Explained

## Current Implementation: What the Report Agent Does

### Current Data Source: yfinance (Yahoo Finance)

The **Report Analysis Agent** currently uses **yfinance**, which provides:

❌ **NOT Official SEC Filings** - Does not download actual PDF/HTML reports
✅ **Parsed Financial Data** - Extracts and formats data from Yahoo Finance
✅ **Free & No API Key** - Unlimited access
✅ **Easy to Use** - Simple Python library

### What You Currently Get:

#### For Stocks:
```python
{
  "earnings": {
    "quarterly": [
      {"date": "2024-01-25", "revenue": 119580000000, "earnings": 33920000000}
    ],
    "annual": [
      {"year": "2023", "revenue": 383930000000, "earnings": 96990000000}
    ]
  },
  "metrics": {
    "market_cap": 3000000000000,
    "pe_ratio": 28.5,
    "dividend_yield": 0.0045
  },
  "financials": {
    "income_statement": {...},
    "balance_sheet": {...},
    "cash_flow": {...}
  }
}
```

**What this is**:
- Pre-processed, parsed numerical data
- Extracted from Yahoo Finance's database
- Already calculated metrics
- Summarized financial statements

**What this is NOT**:
- Not the official PDF report filed with SEC
- Not the original 10-K, 10-Q, or 8-K documents
- Not earnings call transcripts
- Not the original company press releases

#### For ETFs:
```python
{
  "fund_info": {
    "expense_ratio": 0.0945,
    "total_assets": 450000000000,
    "yield": 0.0145
  },
  "holdings": [...],  # Top holdings list
  "distributions": [...]  # Dividend history
}
```

**What this is**:
- Fund characteristics and metrics
- List of top holdings (usually top 10-15)
- Historical performance data

**What this is NOT**:
- Not the official fund prospectus PDF
- Not the complete holdings list (just top holdings)
- Not the SAI (Statement of Additional Information)

---

## Official SEC Filings: What You Can Download

### SEC EDGAR (Electronic Data Gathering, Analysis, and Retrieval)

The SEC requires public companies to file official reports. These are the **actual documents**:

### Stock Filings:

| Filing Type | Description | Frequency | What It Contains |
|-------------|-------------|-----------|------------------|
| **10-K** | Annual Report | Yearly | Comprehensive financial statements, business description, risk factors, MD&A |
| **10-Q** | Quarterly Report | Quarterly | Unaudited financial statements, updates since last 10-K |
| **8-K** | Current Report | Event-driven | Material events (acquisitions, executive changes, earnings releases) |
| **DEF 14A** | Proxy Statement | Yearly | Executive compensation, board proposals, shareholder voting |
| **S-1** | IPO Registration | One-time | Initial public offering registration document |
| **Form 4** | Insider Trading | As needed | Insider buy/sell transactions |

### ETF Filings:

| Filing Type | Description | Frequency | What It Contains |
|-------------|-------------|-----------|------------------|
| **485BPOS** | Prospectus | Annual/Updates | Fund objectives, fees, risks, performance |
| **N-CSR** | Certified Shareholder Report | Semi-annual | Complete list of all holdings, financial statements |
| **N-Q** | Quarterly Holdings | Quarterly | Complete portfolio holdings |
| **497** | Summary Prospectus | Updates | Condensed fund information |

### Example URLs:

**Apple 10-K (Annual Report):**
```
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=10-K&dateb=&owner=exclude&count=40
```

**SPY Fund Holdings (N-CSR):**
```
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000884394&type=N-CSR&dateb=&owner=exclude&count=40
```

---

## Comparison: yfinance vs SEC EDGAR

| Feature | yfinance (Current) | SEC EDGAR (Official) |
|---------|-------------------|---------------------|
| **Data Format** | Parsed JSON/Python objects | Raw PDF/HTML/XBRL documents |
| **Processing** | Pre-processed, cleaned | Raw, requires parsing |
| **Completeness** | Summary data | Complete official documents |
| **Authentication** | None required | None required (public data) |
| **Rate Limits** | No official limits (scraping) | No limits (but be respectful) |
| **Reliability** | Depends on Yahoo Finance | Official government source |
| **Historical Data** | Limited years | Complete history since filing |
| **Legal Status** | Not official source | Official regulatory filings |
| **Use Case** | Quick analysis, metrics | Legal/audit, deep research, compliance |
| **Holdings (ETF)** | Top 10-15 | Complete list (all holdings) |
| **Earnings Details** | Revenue/EPS summary | Complete financial statements with notes |
| **Transcripts** | No | No (need third-party provider) |

---

## What Each Approach Is Best For:

### yfinance (Current Implementation)

✅ **Best for:**
- Quick portfolio screening
- Getting key metrics fast
- Building dashboards
- Real-time/recent data
- Automated trading signals
- Educational projects
- MVP/prototype development

❌ **Not suitable for:**
- Legal compliance
- Audit requirements
- Academic research requiring official sources
- Deep due diligence
- Complete holdings analysis (ETFs)
- Historical analysis beyond a few years

### SEC EDGAR Filings

✅ **Best for:**
- Legal compliance and audit
- Academic research
- Deep due diligence
- Historical analysis (10+ years)
- Complete ETF holdings
- Reading management commentary (MD&A)
- Risk factor analysis
- Executive compensation research

❌ **Not suitable for:**
- Real-time data (filings have delays)
- Quick screening
- Algorithmic trading
- Simple metric extraction (requires parsing)

---

## How to Add SEC EDGAR Integration

If you want to download actual official reports, I can add:

### Option 1: SEC EDGAR Direct Access (Free)

```python
class SECEdgarClient:
    """Download official SEC filings"""

    def get_company_filings(self, ticker: str, filing_type: str) -> List[Dict]:
        """Get list of filings for a company"""

    def download_filing(self, filing_url: str, output_path: str):
        """Download PDF/HTML filing"""

    def get_latest_10k(self, ticker: str) -> str:
        """Get latest annual report URL"""

    def get_latest_10q(self, ticker: str) -> str:
        """Get latest quarterly report URL"""
```

**What you get:**
- Direct links to PDF/HTML documents
- Complete official filings
- Free access
- No API key needed

**Limitations:**
- You get the raw document (PDF/HTML)
- Need to parse if you want structured data
- File sizes can be large (10-50 MB)
- Need to handle XBRL format for structured data

### Option 2: SEC API (Third-party, Parsed)

Services like **sec-api.io** or **Financial Modeling Prep** provide:
- Pre-parsed SEC data
- Structured JSON format
- Historical data
- API access

**Cost**: $49-99/month for API access

---

## Recommended Approach:

### For Your Use Case:

1. **Current Setup (yfinance)** - Keep using for:
   - Quick portfolio analysis
   - Key metrics extraction
   - Earnings summaries
   - ETF basic info

2. **Add SEC EDGAR** - If you need:
   - Official source citations
   - Complete ETF holdings (not just top 10)
   - Historical filings (10+ years)
   - Management discussion & analysis text
   - Risk factors
   - Audit-quality data

### Hybrid Approach (Recommended):

```python
# Quick metrics from yfinance
metrics = financial_client.get_security_info("AAPL")

# Official documents from SEC if needed
if user_requests_official_document:
    sec_client.download_filing("AAPL", "10-K", "latest")
```

---

## Current Configuration in config.yaml:

```yaml
agents:
  report_agent:
    enabled: true
    config:
      download_sec_filings: false  # Set to true to enable SEC downloads

data_sources:
  yfinance:
    enabled: true
    description: "Parsed earnings data, fund info"

  sec_edgar:
    enabled: false  # Set to true to enable SEC downloads
    description: "Download actual PDF/HTML reports filed with SEC"
```

---

## Should You Add SEC EDGAR Integration?

### Add SEC EDGAR if:
- ✅ You need official source documents
- ✅ You want complete ETF holdings (all positions, not just top 10)
- ✅ You need to cite official regulatory filings
- ✅ You want to analyze management commentary (MD&A)
- ✅ You need historical data beyond 5 years
- ✅ You're building audit/compliance features

### Stick with yfinance if:
- ✅ You just need key metrics and summaries
- ✅ You want fast, easy access to data
- ✅ You're building investment screeners or dashboards
- ✅ You need recent/real-time data
- ✅ You don't need official document citations

---

## Implementation Effort:

### Adding SEC EDGAR Download:
- **Time**: 2-3 hours
- **Complexity**: Medium (need to handle PDF downloads, parse filing lists)
- **Benefits**: Official documents, complete data
- **Storage**: Need to manage downloaded PDFs (10-50 MB each)

### Adding SEC Data Parsing (XBRL):
- **Time**: 8-12 hours
- **Complexity**: High (XBRL format is complex)
- **Benefits**: Structured financial data from official source
- **Alternative**: Use paid service that provides pre-parsed data

---

## Next Steps:

Let me know if you want me to:

1. **Keep current setup** (yfinance only) - Simple, fast, free
2. **Add SEC filing downloads** - Get PDF/HTML documents
3. **Add SEC data parsing** - Extract structured data from filings
4. **Use third-party SEC API** - Pre-parsed official data (paid)

The current implementation with **yfinance is perfectly fine for most portfolio analysis use cases**. You only need SEC EDGAR if you specifically need official regulatory documents or complete holdings data.
