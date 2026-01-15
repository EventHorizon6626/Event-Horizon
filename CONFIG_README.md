# Event Horizon - Configuration System

## Quick Answer to Your Questions

### 1. How to easily activate/deactivate agents for deployment?

**Answer**: Edit `config.yaml` and set `enabled: true/false`

```yaml
agents:
  news_agent:
    enabled: false  # ← Deactivated (your current request)

  report_agent:
    enabled: true   # ← Activated (your current request)
```

Then run:
```bash
python main.py
```

**No code changes needed!**

---

### 2. Can Report Agent download open source earnings reports published by companies/funds?

**Short Answer**: No, currently it doesn't download the actual PDF/HTML reports.

**What it does now**:
- ✅ Fetches **parsed earnings data** from Yahoo Finance (via yfinance)
- ✅ Gets revenue, EPS, and financial metrics
- ✅ Retrieves fund information and holdings
- ❌ Does NOT download actual PDF reports filed with SEC
- ❌ Does NOT download official 10-K, 10-Q, prospectus documents

**Long Answer**: See `docs/data-sources-explained.md` for complete explanation.

**To add official report downloads**: I can add SEC EDGAR integration (see below).

---

## What You Have Now

### New Files:

1. **`config.yaml`** - Master configuration file
   - Enable/disable agents
   - Configure agent parameters
   - Set data sources
   - API key management

2. **`utils/config_loader.py`** - Configuration loader
   - Reads YAML configuration
   - Manages agent status
   - Handles environment variables

3. **`main.py`** - Configuration-driven main script
   - Automatically runs enabled agents
   - No manual menu selection
   - Uses config.yaml for all settings

4. **Documentation**:
   - `docs/configuration-guide.md` - Complete guide
   - `docs/data-sources-explained.md` - Data source comparison
   - `CONFIG_README.md` - This file (quick reference)

---

## How to Use (Simple)

### Step 1: Install PyYAML

```bash
pip install pyyaml
```

Or:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Agents

Edit `config.yaml`:

```yaml
agents:
  news_agent:
    enabled: false  # You wanted this off

  report_agent:
    enabled: true   # You wanted this on
```

### Step 3: Run

```bash
python main.py
```

**Output**:
```
======================================================================
 AGENT CONFIGURATION STATUS
======================================================================
news_agent          : ❌ DISABLED
report_agent        : ✅ ENABLED

Enabled Agents: report_agent
======================================================================

🤖 EXECUTING REPORT AGENT
...
📊 report_results.json
```

---

## Data Source Clarification

### What yfinance Provides (Current):

| Data Type | Example | Source |
|-----------|---------|--------|
| Earnings Data | Revenue: $119.5B, EPS: $2.18 | Yahoo Finance (parsed) |
| Financial Metrics | P/E: 28.5, Market Cap: $3T | Yahoo Finance (calculated) |
| Fund Info | Expense ratio: 0.09%, Assets: $450B | Yahoo Finance |
| Top Holdings | AAPL 7.1%, MSFT 6.8%, etc. | Yahoo Finance (top 10-15) |

**Format**: JSON/Python objects (already parsed)
**Cost**: Free
**API Key**: Not required
**Speed**: Fast

### What SEC EDGAR Would Provide (If Added):

| Document Type | Example | Source |
|---------------|---------|--------|
| 10-K (Annual) | Complete annual report PDF | SEC.gov (official) |
| 10-Q (Quarterly) | Quarterly report PDF | SEC.gov (official) |
| Prospectus | ETF prospectus PDF | SEC.gov (official) |
| N-CSR | Complete holdings list (all positions) | SEC.gov (official) |

**Format**: PDF/HTML/XBRL (raw documents)
**Cost**: Free
**API Key**: Not required
**Speed**: Slower (large files)

---

## Comparison Table

|  | yfinance (Current) | SEC EDGAR (Can Add) |
|--|-------------------|---------------------|
| **What you get** | Parsed numbers | Official PDF documents |
| **Example** | `{"revenue": 119500000000}` | 50-page PDF report |
| **Processing** | Ready to use | Need to read/parse |
| **Completeness** | Summary metrics | Complete disclosures |
| **Legal status** | Unofficial | Official regulatory filing |
| **Use case** | Quick analysis | Official records |
| **ETF holdings** | Top 10-15 | All holdings (complete list) |

---

## Do You Need SEC EDGAR?

### Stick with yfinance (current) if:
- ✅ You need earnings metrics and summaries
- ✅ You want fast data access
- ✅ You're building investment dashboards
- ✅ Top 10-15 ETF holdings are sufficient

### Add SEC EDGAR if:
- ✅ You need official source documents
- ✅ You want complete ETF holdings (all 500 positions)
- ✅ You need to cite regulatory filings
- ✅ You want to read full management commentary
- ✅ You need documents for audit/compliance

---

## How to Add SEC EDGAR (If Needed)

### Option 1: I Can Build It (2-3 hours)

I can add:
```python
class SECEdgarClient:
    def download_10k(self, ticker: str) -> str:
        """Download latest annual report PDF"""

    def download_10q(self, ticker: str) -> str:
        """Download latest quarterly report PDF"""

    def get_etf_holdings_complete(self, ticker: str) -> List[Dict]:
        """Get complete holdings from N-CSR filing"""
```

**Pros**: Free, official source
**Cons**: Raw documents (PDFs), need storage

### Option 2: Use Third-Party Service

Services like **sec-api.io** provide pre-parsed SEC data:
- API access to filings
- Structured JSON format
- No parsing needed

**Pros**: Already parsed, easy to use
**Cons**: $49-99/month

---

## Deployment Guide

### For Your Current Request

**config.yaml**:
```yaml
agents:
  news_agent:
    enabled: false  # ← OFF

  report_agent:
    enabled: true   # ← ON
    config:
      include_financials: true
      earnings_periods: 4
      top_holdings: 10
```

**Commands**:
```bash
# Install dependencies (first time)
pip install -r requirements.txt

# Run system
python main.py

# Output
# ✅ report_results.json (earnings and fund data)
# ❌ No news_results.json (news agent disabled)
```

### For Production

1. Copy config template:
```bash
cp config.yaml config.prod.yaml
```

2. Edit for production:
```yaml
agents:
  news_agent:
    enabled: false

  report_agent:
    enabled: true
    config:
      earnings_periods: 8  # More history

logging:
  level: "INFO"

output:
  json_directory: "/app/data/results"
```

3. Deploy:
```bash
python main.py
```

---

## File Structure

```
Event-Horizon/
├── config.yaml                    # ← Configure agents here
├── main.py                        # ← Run this (config-driven)
│
├── utils/
│   └── config_loader.py           # Configuration loader
│
├── docs/
│   ├── configuration-guide.md     # Complete config guide
│   ├── data-sources-explained.md  # What data you get
│   └── CONFIG_README.md           # This file
│
└── agents/
    ├── news_agent.py              # News Agent
    └── report_agent.py            # Report Agent
```

---

## Two Modes

### Interactive Mode (without config.yaml):
```bash
python main.py
# User sees menu, selects option manually
# Good for testing and exploration
```

### Automated Mode (with config.yaml):
```bash
# Configure once
vim config.yaml

# Run anytime (no interaction needed)
python main.py

# Perfect for automation, Docker, cron jobs
```

---

## FAQ

### Q: Does main.py require config.yaml?

**A**: No! `main.py` works in two modes:
- **With config.yaml**: Automated, config-driven (best for deployment)
- **Without config.yaml**: Interactive menu mode (best for testing)

The script automatically detects which mode to use.

### Q: Can I have multiple config files?

**A**: Yes!
```bash
python main.py --config config.dev.yaml   # Development
python main.py --config config.prod.yaml  # Production
```

(Note: Command-line config selection requires minor update to main.py)

### Q: What happens if I enable both agents?

**A**: Both run sequentially:
```
1. News Agent executes → news_results.json
2. Report Agent executes → report_results.json
```

### Q: Do I need NEWS_API_KEY if news agent is disabled?

**A**: No! If news agent is disabled, the API key is not required.

### Q: Can the Report Agent work without any API keys?

**A**: Yes! Report Agent uses yfinance which requires no API key.

---

## Summary

### What You Asked For:

1. ✅ **Easy agent activation/deactivation**: Use `config.yaml`
2. ✅ **Deactivate News Agent**: Set `enabled: false`
3. ✅ **Activate Report Agent only**: Set `enabled: true`
4. ❓ **Download official reports**: Not yet implemented (currently gets parsed data)

### What You Got:

1. **`config.yaml`** - Simple configuration file
2. **`main.py`** - Configuration-driven execution
3. **`ConfigLoader`** - Configuration management utility
4. **Documentation** - Complete guides and explanations

### Next Steps:

**Option A**: Use current setup (recommended for most cases)
- Run `python main.py`
- Get parsed earnings data
- Fast and easy

**Option B**: Add SEC EDGAR for official documents
- Let me know and I'll implement it
- Takes 2-3 hours
- You'll get actual PDF reports

---

## Current Status

**Your config.yaml is set to**:
- ❌ News Agent: DISABLED
- ✅ Report Agent: ENABLED

**Data source**:
- yfinance (Yahoo Finance parsed data)

**What you'll get**:
- Earnings metrics (revenue, EPS)
- Financial statements (income, balance, cash flow)
- Fund information (expense ratio, holdings)
- Key metrics (P/E, market cap, etc.)

**What you won't get**:
- Official SEC PDF documents
- Complete ETF holdings (just top 10-15)
- Raw regulatory filings

**To change**: Edit `config.yaml` and run `python main.py`
