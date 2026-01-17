# Event Horizon - Quick Start Guide

Get your multi-agent system running in 5 minutes.

---

## Prerequisites

- Python 3.8+
- pip
- (Optional) NewsAPI.org account for News Agent

---

## Quick Setup

### 1. Install Dependencies

```bash
cd Event-Horizon-AI

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install packages
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional)

```bash
# Copy example environment file
cp .env.example .env

# Edit and add your API key
nano .env
```

`.env` file:
```bash
NEWS_API_KEY=your_api_key_here
LOG_LEVEL=INFO
```

**Note**: NewsAPI key only needed for News Agent. Report Agent works without any keys.

Get free API key: [newsapi.org/register](https://newsapi.org/register)

### 3. Run

```bash
python main.py
```

Choose agents when prompted:
```
Select agents to execute:
  1. News Agent only
  2. Report Agent only
  3. Both agents (recommended)

Enter choice (1-3) [default: 3]:
```

### 4. Check Results

Results saved to:
- `news_results.json` - News articles
- `report_results.json` - Earnings/fund reports
- `event_horizon_[timestamp].log` - Execution logs

---

## Output Examples

### News Agent Output

```json
{
  "portfolio_id": "test_001",
  "news_by_stock": {
    "AAPL": [
      {
        "title": "Apple announces new product...",
        "source": "TechCrunch",
        "url": "https://...",
        "published_at": "2024-01-15T10:30:00Z",
        "description": "..."
      }
    ]
  },
  "total_articles": 35
}
```

### Report Agent Output

**For Stocks:**
```json
{
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
        "earnings_date": "2024-01-25"
      },
      "metrics": {
        "market_cap": 3000000000000,
        "pe_ratio": 28.5
      },
      "financials": {...}
    }
  }
}
```

**For ETFs:**
```json
{
  "SPY": {
    "symbol": "SPY",
    "security_type": "etf",
    "name": "SPDR S&P 500 ETF Trust",
    "reports": {
      "fund_info": {
        "category": "Large Blend",
        "total_assets": 450000000000,
        "expense_ratio": 0.0945
      },
      "holdings": [...],
      "performance": {...}
    }
  }
}
```

---

## Custom Portfolios

Edit `main.py` to test different securities:

```python
test_portfolio = {
    "portfolio_id": "my_portfolio",
    "user_id": "user_demo",
    "portfolio": ["NVDA", "AMD", "VGT", "QQQ"]
}
```

**Supported:**
- **Stocks**: AAPL, TSLA, GOOGL, MSFT, AMZN, META, NVDA, AMD, etc.
- **ETFs**: SPY, QQQ, VOO, VTI, IWM, DIA, VGT, XLF, etc.

---

## Configuration

### News Agent Config

```python
news_config = {
    "max_articles_per_stock": 10,  # 1-100
    "days_back": 7,                # 1-30
    "language": "en"
}
```

### Report Agent Config

```python
report_config = {
    "include_financials": True,
    "earnings_periods": 4,         # Number of quarters
    "top_holdings": 10             # Top N for ETFs
}
```

---

## Troubleshooting

### News Agent

**"NEWS_API_KEY not found"**
- Ensure `.env` exists in project root
- Verify no typos in API key
- Restart terminal after creating `.env`
- Skip News Agent and use Report Agent only

**"Rate limit reached"**
- Free tier: 100 requests/day
- Reduce `max_articles_per_stock`
- Wait 24 hours or upgrade plan

**No articles returned**
- Add company to `SYMBOL_TO_COMPANY` in `services/news_api_client.py`
- Verify stock symbol is correct

### Report Agent

**"Symbol not found"**
- Verify symbol on finance.yahoo.com
- Delisted or small cap stocks may lack data

**Empty earnings data**
- Some stocks don't report publicly
- New listings may lack historical data

**Connection issues**
- Check internet connection
- Yahoo Finance may be temporarily down

### General

**Import errors**
- Activate virtual environment
- Run `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.8+)

---

## Docker Usage

For Docker deployment:

```bash
# Build
docker build -t event-horizon:latest .

# Run
docker run --rm \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v $(pwd)/results:/app/results \
  event-horizon:latest
```

See **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** for details.

---

## Next Steps

### Add More Agents
- Sentiment Analysis Agent
- Technical Analysis Agent
- Risk Assessment Agent

### Integration
- **Web API**: FastAPI/Flask REST endpoints
- **Dashboard**: Streamlit visualization
- **Scheduling**: Celery for automation
- **Database**: PostgreSQL for storage

### Enhancements
- Parallel processing with aiohttp
- Database persistence with SQLAlchemy
- FinBERT sentiment analysis
- Multi-agent orchestration

---

## Documentation

- `docs/news-agent-design.md` - News Agent architecture
- `docs/report-agent-design.md` - Report Agent architecture
- `docs/multi-agent-architecture.md` - Multi-agent patterns
- `CONFIG_README.md` - Configuration system
- `DEPLOYMENT.md` - Production deployment
- `DOCKER_QUICKSTART.md` - Docker local setup

---

## Success Checklist

- ✅ Python 3.8+ installed
- ✅ Dependencies installed
- ✅ `python main.py` runs successfully
- ✅ Report Agent retrieves data
- ✅ JSON results created
- ⬜ (Optional) NewsAPI key configured
- ⬜ (Optional) Custom portfolio tested

---

## Tips

1. **Start small**: Test with 2-3 securities first
2. **Mix types**: Combine stocks and ETFs
3. **Check logs**: Detailed execution info in log files
4. **No API key needed**: Report Agent is fully functional without keys
5. **Rate limits**: News Agent free tier = 100 requests/day
6. **Save results**: JSON files useful for analysis

---

## Quick Reference

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Run
python main.py

# Docker
docker build -t event-horizon:latest .
docker-compose -f docker-compose.dev.yml up

# Check results
ls results/
cat results/report_results.json
```

---

**Ready to build?** This foundation supports adding more specialized agents and creating a complete multi-agent investment analysis platform.
