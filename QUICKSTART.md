# Event Horizon - Quick Start Guide

Get your multi-agent system running in 5 minutes!

This guide covers both agents:
- **News Agent**: Retrieves financial news for portfolio stocks
- **Report Agent**: Fetches earnings reports (stocks) and fund reports (ETFs)

---

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A free NewsAPI.org account (optional - only for News Agent)
- Internet connection (for Report Agent to fetch financial data)

---

## 🚀 Quick Setup (5 Steps)

### Step 1: Get Your Free API Key

1. Go to [https://newsapi.org/register](https://newsapi.org/register)
2. Sign up for a free account
3. Copy your API key from the dashboard
4. Keep it handy for Step 3

**Free tier limits**: 100 requests/day, perfect for testing!

---

### Step 2: Install Dependencies

```bash
cd Event-Horizon

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

---

### Step 3: Configure API Key

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
# Replace "your_newsapi_key_here" with your actual key
nano .env  # or use your preferred editor
```

Your `.env` file should look like:
```
NEWS_API_KEY=abc123xyz789youractualkey
MAX_ARTICLES_PER_STOCK=20
DAYS_BACK=7
LOG_LEVEL=INFO
```

---

### Step 4: Run the Test

```bash
python main.py
```

You'll be prompted to choose which agents to run:
```
==============================================================
 EVENT HORIZON - MULTI-AGENT SYSTEM TEST
==============================================================

Test Portfolio:
  ID: test_001
  Securities: AAPL, TSLA, SPY, QQQ
  Mix: Stocks (AAPL, TSLA) + ETFs (SPY, QQQ)

==============================================================
Select agents to execute:
  1. News Agent only
  2. Report Agent only
  3. Both agents (recommended)
==============================================================

Enter choice (1-3) [default: 3]:
```

**Recommended**: Press Enter to run both agents (option 3).

**Note**: The Report Agent works without any API keys! It uses yfinance to fetch data from Yahoo Finance. The News Agent requires a NewsAPI.org key.

---

### Step 5: Check the Results

After execution completes:

1. **Console Output**: See formatted summary in terminal
2. **JSON Files**:
   - `news_results.json` - News articles for each security
   - `report_results.json` - Earnings/fund reports for each security
3. **Log File**: Detailed execution logs in `event_horizon_[timestamp].log`

---

## 📊 Understanding the Output

### News Agent Console Output:

- **Execution Summary**: Status, timing, article counts
- **Articles by Symbol**: Top 3 articles per stock with:
  - Title
  - Source
  - Publication date
  - URL
  - Description
- **Errors**: Any issues encountered

### Report Agent Console Output:

- **Execution Summary**: Status, timing, report counts
- **Securities by Type**: Count of stocks, ETFs, mutual funds
- **Reports by Symbol**:
  - **Stocks**: Earnings data, upcoming earnings dates, key metrics, financials
  - **ETFs**: Fund info, holdings, performance, distributions
- **Errors**: Any issues encountered

### News Agent JSON File Contains:

```json
{
  "execution_id": "uuid",
  "status": "success",
  "result": {
    "portfolio_id": "test_001",
    "news_by_stock": {
      "AAPL": [
        {
          "title": "Apple announces...",
          "source": "TechCrunch",
          "url": "https://...",
          "published_at": "2024-01-15T10:30:00Z",
          "description": "...",
          ...
        }
      ],
      ...
    },
    "total_articles": 35,
    ...
  }
}
```

### Report Agent JSON File Contains:

```json
{
  "execution_id": "uuid",
  "status": "success",
  "result": {
    "portfolio_id": "test_001",
    "reports_by_symbol": {
      "AAPL": {
        "symbol": "AAPL",
        "security_type": "stock",
        "name": "Apple Inc.",
        "reports": {
          "earnings": {
            "quarterly": [...],
            "annual": [...]
          },
          "calendar": {
            "earnings_date": "2024-01-25",
            "earnings_estimate": 2.10
          },
          "metrics": {
            "market_cap": 3000000000000,
            "pe_ratio": 28.5,
            "dividend_yield": 0.0045
          },
          "financials": {...}
        }
      },
      "SPY": {
        "symbol": "SPY",
        "security_type": "etf",
        "name": "SPDR S&P 500 ETF Trust",
        "reports": {
          "fund_info": {
            "category": "Large Blend",
            "total_assets": 450000000000,
            "expense_ratio": 0.0945,
            "yield": 0.0145
          },
          "performance": {...},
          "distributions": [...]
        }
      }
    },
    "securities_by_type": {
      "stock": 2,
      "etf": 2
    },
    "total_reports": 4
  }
}
```

---

## 🎯 Try Different Portfolios

Edit `main.py` to test different securities:

```python
test_portfolio = {
    "portfolio_id": "my_tech_portfolio",
    "user_id": "user_demo",
    "portfolio": ["NVDA", "AMD", "INTC", "VGT", "QQQ"]  # Mix of stocks and ETFs
}
```

**Supported symbols**:
- **Stocks**: AAPL, TSLA, GOOGL, MSFT, AMZN, META, NVDA, AMD, INTC, CRM, ORCL, IBM, DIS, BA, GE, JPM, BAC, WMT, and more!
- **ETFs**: SPY, QQQ, VOO, VTI, IWM, DIA, VGT, XLF, XLE, and thousands more!

---

## ⚙️ Configuration Options

Adjust in `main.py`:

### News Agent Config:
```python
news_config = {
    "max_articles_per_stock": 10,  # Articles per stock (1-100)
    "days_back": 7,                # How far back to search (1-30)
    "language": "en"               # News language
}
```

### Report Agent Config:
```python
report_config = {
    "include_financials": True,    # Include full financial statements
    "earnings_periods": 4,         # Number of quarters to retrieve
    "top_holdings": 10            # Top N holdings for ETFs
}
```

---

## 🐛 Troubleshooting

### News Agent Issues

#### "NEWS_API_KEY not found"
- Make sure `.env` file exists in project root
- Check API key is correct (no quotes needed)
- Restart terminal after creating `.env`
- **Note**: You can still run Report Agent without this key!

#### "Invalid API key" (401 error)
- Verify your API key on NewsAPI.org dashboard
- Check for typos or extra spaces

#### "Rate limit reached"
- Free tier: 100 requests/day
- Wait 24 hours or upgrade plan
- Reduce `max_articles_per_stock` to conserve requests

#### No articles returned for stock
- Company name might not match search
- Try adding company to `SYMBOL_TO_COMPANY` dict in `services/news_api_client.py`
- Check if stock symbol is correct

### Report Agent Issues

#### "Symbol not found or no data available"
- Verify stock/ETF symbol is correct
- Some delisted or very small cap stocks may not have data
- Check symbol on finance.yahoo.com

#### Empty earnings data
- Some stocks don't report earnings publicly
- Newly listed companies may not have historical data
- Foreign stocks may have limited data

#### yfinance connection issues
- Check internet connection
- Yahoo Finance may be temporarily unavailable
- Try again in a few minutes

### General Issues

#### Import errors
- Ensure you're in virtual environment
- Run `pip install -r requirements.txt` again
- Check Python version: `python --version` (need 3.8+)

#### "ModuleNotFoundError: No module named 'yfinance'"
- Activate your virtual environment
- Run `pip install yfinance`

---

## 📚 Next Steps

### Phase 2 Enhancements:

1. **Add Sentiment Analysis**
   - Install: `pip install transformers torch`
   - Integrate FinBERT for financial sentiment

2. **Add Database Storage**
   - Install: `pip install sqlalchemy`
   - Store articles for historical tracking

3. **Add Parallel Processing**
   - Install: `pip install aiohttp`
   - Fetch news for all stocks simultaneously

4. **Create More Agents**
   - Financial Summary Agent
   - Technical Analysis Agent
   - Balance Sheet Agent

### Integration Options:

- **Web API**: Use FastAPI to create REST endpoints
- **Dashboard**: Build with Streamlit for visualization
- **Scheduling**: Use Celery for automated updates
- **Database**: PostgreSQL for production storage

---

## 📖 Documentation

- **Agent Design Docs**:
  - `docs/news-agent-design.md` - News Agent architecture
  - `docs/report-agent-design.md` - Report Agent architecture
- **Architecture Resources**:
  - `Event-Horizon AI/20-agentic-design-patterns.md` - Agentic design patterns
  - `Event-Horizon AI/multiagent-refs.md` - Multi-agent systems guide
- **Implementation**:
  - `agents/base_agent.py` - Base agent class
  - `services/news_api_client.py` - News API client
  - `services/financial_data_client.py` - Financial data client

---

## 💡 Tips

1. **Start Small**: Test with 2-3 securities first
2. **Mix Security Types**: Try combinations of stocks and ETFs
3. **Check Logs**: Detailed info in log files
4. **Rate Limits (News Agent)**: Free tier = 100 requests/day, plan accordingly
5. **No Rate Limits (Report Agent)**: yfinance is free and unlimited!
6. **Company Names**: Add more to `SYMBOL_TO_COMPANY` for better news results
7. **Save Results**: JSON files useful for analysis and debugging
8. **Parallel Processing**: Both agents can run independently

---

## 🎉 Success Checklist

- [✓] Python 3.8+ installed
- [✓] Dependencies installed (`pip install -r requirements.txt`)
- [✓] `python main.py` runs successfully
- [✓] Report Agent retrieves earnings and fund data
- [✓] JSON results files created
- [✓] Both agents work with test portfolio
- [ ] (Optional) NewsAPI.org account created
- [ ] (Optional) API key added to `.env` for News Agent

---

## 🆘 Need Help?

Check the comprehensive design document:
```bash
cat docs/news-agent-design.md
```

Or review the implementation:
```bash
# View agent code
cat agents/news_agent.py

# View API client
cat services/news_api_client.py
```

---

**Happy Coding! 🚀**

You've successfully set up your Event Horizon multi-agent system with:
- ✅ **News Agent** - Financial news retrieval
- ✅ **Report Agent** - Earnings and fund reports
- ✅ **Base Agent Architecture** - Ready for more agents

This is the foundation for building a complete multi-agent investment analysis platform.

**Next Steps**:
- Build more specialized agents (sentiment analysis, technical analysis, etc.)
- Create multi-agent orchestration layer
- Add caching and parallel processing
- Integrate with portfolio management system
