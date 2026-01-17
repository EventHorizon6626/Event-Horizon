# Undergraduate Level - Datasets & Data Sources

Free and accessible financial datasets for learning, practice, and analysis.

---

## 📊 Stock Market Data (Free)

### 1. **Yahoo Finance API** ⭐ BEST FOR BEGINNERS
- **Access**: Python (yfinance library), direct download
- **Data**: Historical prices, dividends, splits, fundamentals
- **Coverage**: Global stocks, ETFs, indices, currencies, crypto
- **Time Range**: Up to decades of historical data
- **Cost**: FREE
- **Usage**:
  ```python
  import yfinance as yf
  data = yf.download('AAPL', start='2020-01-01', end='2023-12-31')
  ```
- **Link**: https://finance.yahoo.com
- **Why Use**: Easiest to get started, no API key required

### 2. **Alpha Vantage**
- **Access**: REST API (free tier)
- **Data**: Real-time and historical prices, technical indicators, fundamentals
- **Limit**: 25 requests/day (free tier)
- **Cost**: FREE (limited) or $50-$200/month (premium)
- **Usage**: Get free API key, use with Python/R
- **Link**: https://www.alphavantage.co
- **Why Use**: Good for learning API integration

### 3. **Twelve Data**
- **Access**: REST API
- **Data**: Stocks, forex, crypto, indices
- **Limit**: 800 requests/day (free)
- **Cost**: FREE (limited) or $9-$79/month
- **Link**: https://twelvedata.com
- **Why Use**: More generous free tier than Alpha Vantage

---

## 🏢 Company Fundamentals (Free)

### 4. **SEC EDGAR**
- **Access**: Direct download, APIs available
- **Data**: 10-K, 10-Q, 8-K filings, insider trading, ownership
- **Coverage**: All U.S. public companies
- **Cost**: FREE
- **Tools**:
  - **sec-edgar-downloader** (Python library)
  - **FinancialModelingPrep API** (parses EDGAR)
- **Link**: https://www.sec.gov/edgar/searchedgar/companysearch.html
- **Why Use**: Primary source, official data

### 5. **Financial Modeling Prep API**
- **Access**: REST API
- **Data**: Financial statements, ratios, earnings calendar, stock screener
- **Limit**: 250 requests/day (free)
- **Cost**: FREE or $15-$60/month
- **Link**: https://financialmodelingprep.com/developer/docs/
- **Why Use**: Pre-parsed financial data (easier than raw EDGAR)

### 6. **Macrotrends**
- **Access**: Web scraping or manual download
- **Data**: Long-term financial metrics, ratios
- **Coverage**: Major U.S. stocks
- **Cost**: FREE
- **Link**: https://www.macrotrends.net
- **Why Use**: Historical fundamentals (10+ years)

---

## 📈 Market Indices & ETFs

### 7. **FRED (Federal Reserve Economic Data)**
- **Access**: Website, API, Excel plugin
- **Data**: Economic indicators, interest rates, inflation, GDP
- **Cost**: FREE
- **Link**: https://fred.stlouisfed.org
- **Download**: CSV, JSON, XML
- **Why Use**: Most comprehensive free macro data

### 8. **Kenneth French Data Library**
- **Access**: Direct CSV download
- **Data**: Fama-French factors, portfolio returns, industry returns
- **Coverage**: 1926-present
- **Cost**: FREE
- **Link**: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- **Why Use**: Standard in academic research, excellent for portfolio studies

### 9. **MSCI Index Data**
- **Access**: Website (limited free data)
- **Data**: Country/sector indices, ESG scores
- **Cost**: FREE (limited) or subscription
- **Link**: https://www.msci.com/end-of-day-data-search
- **Why Use**: International market exposure

---

## 🗞️ News & Sentiment Data

### 10. **NewsAPI**
- **Access**: REST API
- **Data**: News articles from 80,000+ sources
- **Limit**: 100 requests/day (free)
- **Cost**: FREE (developer) or $449-$999/month
- **Link**: https://newsapi.org
- **Why Use**: Build sentiment analysis models

### 11. **Reddit API (via PRAW)**
- **Access**: Python Reddit API Wrapper (PRAW)
- **Data**: r/WallStreetBets, r/investing, r/stocks posts and comments
- **Cost**: FREE
- **Usage**:
  ```python
  import praw
  reddit = praw.Reddit(client_id='...', client_secret='...', user_agent='...')
  subreddit = reddit.subreddit('wallstreetbets')
  ```
- **Why Use**: Social sentiment analysis, retail investor mood

### 12. **Twitter API (X API)**
- **Access**: API v2 (free tier available)
- **Data**: Tweets, user data, trends
- **Limit**: 1500 tweets/month (free)
- **Cost**: FREE (basic) or $100-$5000/month
- **Link**: https://developer.twitter.com/en/docs/twitter-api
- **Why Use**: Real-time sentiment, breaking news

---

## 💱 Cryptocurrency Data

### 13. **CoinGecko API**
- **Access**: REST API
- **Data**: Crypto prices, volume, market cap, historical data
- **Limit**: 10-50 calls/min (free)
- **Cost**: FREE
- **Link**: https://www.coingecko.com/en/api
- **Why Use**: Most comprehensive free crypto data

### 14. **CoinMarketCap API**
- **Access**: REST API
- **Data**: Similar to CoinGecko
- **Limit**: 333 credits/day (free)
- **Cost**: FREE (limited) or $29-$899/month
- **Link**: https://coinmarketcap.com/api/
- **Why Use**: Alternative to CoinGecko

---

## 🌍 International & Forex Data

### 15. **Quandl (Nasdaq Data Link)**
- **Access**: API, Python library
- **Data**: Stocks, commodities, forex, bitcoin
- **Limit**: 50 calls/day (free)
- **Cost**: FREE or $49/month+
- **Link**: https://data.nasdaq.com/
- **Why Use**: Clean, curated datasets

### 16. **OANDA Exchange Rates**
- **Access**: API
- **Data**: Historical forex rates (200+ currencies)
- **Cost**: FREE for non-commercial use
- **Link**: https://www.oanda.com/fx-for-business/historical-rates
- **Why Use**: Accurate historical FX data

---

## 📚 Academic & Research Datasets

### 17. **CRSP (via WRDS for students)**
- **Access**: Wharton Research Data Services (WRDS)
- **Data**: Historical U.S. stock returns, corporate actions
- **Cost**: FREE if your university has WRDS access
- **Link**: https://wrds-www.wharton.upenn.edu/
- **Why Use**: Gold standard for academic research

### 18. **Compustat (via WRDS)**
- **Access**: WRDS (university subscription)
- **Data**: Company fundamentals, financials
- **Cost**: FREE with university access
- **Why Use**: Clean, standardized financial data

### 19. **Bloomberg Terminal (University Access)**
- **Access**: On-campus terminals
- **Data**: Everything (prices, fundamentals, news, analytics)
- **Cost**: FREE for students (university subscription)
- **Link**: Ask your university library
- **Why Use**: Industry standard, most comprehensive

---

## 🛠️ Pre-Built Datasets for Learning

### 20. **Kaggle Financial Datasets**
- **Popular Datasets**:
  - S&P 500 Stock Data
  - Bitcoin Historical Data
  - Stock Market Dataset (all US stocks)
  - Financial Sentiment Analysis
- **Cost**: FREE
- **Link**: https://www.kaggle.com/datasets?search=stock
- **Why Use**: Clean, ready-to-use for projects

### 21. **UCI Machine Learning Repository - Finance**
- **Datasets**:
  - Credit Approval
  - Default of Credit Card Clients
  - German Credit Data
- **Cost**: FREE
- **Link**: https://archive.ics.uci.edu/ml/index.php
- **Why Use**: Benchmark datasets for ML projects

### 22. **Quandl Wiki Continuous Futures**
- **Data**: Futures prices (commodities, indices)
- **Cost**: FREE
- **Link**: https://data.nasdaq.com/data/CHRIS-wiki-continuous-futures
- **Why Use**: Learn about derivatives

---

## 🎓 Recommended Datasets for Projects

### Project 1: Build a Portfolio Tracker
**Data Needed**:
- Yahoo Finance (yfinance) - stock prices
- FRED - risk-free rate (treasury yields)
**Difficulty**: Easy
**Time**: 1-2 weeks

### Project 2: Fundamental Stock Screener
**Data Needed**:
- Financial Modeling Prep API - fundamentals
- Yahoo Finance - prices
**Difficulty**: Medium
**Time**: 2-3 weeks

### Project 3: Sentiment Analysis Trading Bot
**Data Needed**:
- NewsAPI - news articles
- Reddit API - social sentiment
- Yahoo Finance - prices
**Difficulty**: Medium-Hard
**Time**: 4-6 weeks

### Project 4: Backtest Fama-French Factors
**Data Needed**:
- Kenneth French Data Library - factor returns
- Yahoo Finance - stock prices
**Difficulty**: Medium
**Time**: 2-3 weeks

### Project 5: Options Pricing Model
**Data Needed**:
- Yahoo Finance - stock prices, options data
- FRED - risk-free rate
**Difficulty**: Hard
**Time**: 4-6 weeks

---

## 💻 Data Access Tools

### Python Libraries:
```python
# Stock data
import yfinance as yf
import pandas_datareader as pdr

# APIs
import requests
import fredapi
import praw  # Reddit

# Data manipulation
import pandas as pd
import numpy as np
```

### R Libraries:
```r
# Stock data
library(quantmod)
library(tidyquant)

# Data access
library(Quandl)
library(fredr)  # FRED API
```

---

## 📥 Data Collection Best Practices

1. **Respect Rate Limits**: Don't spam APIs, you'll get banned
2. **Cache Data**: Download once, save locally
3. **Check Data Quality**: Always validate for missing values, outliers
4. **Timezone Awareness**: Market data has timezone issues
5. **Adjust for Splits/Dividends**: Use adjusted close prices
6. **Attribution**: Cite your data sources
7. **Legal Use**: Respect terms of service

---

## 🔒 Data Ethics & Legality

**Allowed**:
✅ Using free APIs within rate limits
✅ Scraping public SEC filings
✅ Academic research with proper attribution
✅ Personal projects and learning

**Not Allowed**:
❌ Selling redistributed data
❌ Violating API terms of service
❌ High-frequency scraping without permission
❌ Commercial use of free-tier data (check TOS)

---

## 📊 Sample Code: Getting Started

```python
import yfinance as yf
import pandas as pd
from fredapi import Fred

# 1. Get stock data
aapl = yf.Ticker('AAPL')
hist = aapl.history(period='1y')
print(hist.head())

# 2. Get fundamentals
info = aapl.info
print(f"P/E Ratio: {info['trailingPE']}")
print(f"Market Cap: ${info['marketCap']:,.0f}")

# 3. Get economic data (FRED API key required)
fred = Fred(api_key='YOUR_API_KEY')
gdp = fred.get_series('GDP')
print(gdp.tail())

# 4. Simple portfolio
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
data = yf.download(tickers, start='2020-01-01')['Adj Close']
returns = data.pct_change()
print(f"Average Daily Returns:\n{returns.mean()}")
```

---

**Next Steps**: After building 2-3 projects with these datasets, explore [Graduate Level Datasets](../02-graduate-master/datasets.md) for high-frequency and alternative data.
