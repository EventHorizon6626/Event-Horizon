# News Retrieval Agent - Design Document

**Agent Type**: News Analysis Agent (Phase 1)
**Status**: Initial Implementation
**Date**: January 15, 2026

---

## Overview

The News Retrieval Agent is the first specialized agent in the Event Horizon multi-agent system. Its primary responsibility is to monitor and retrieve real-time news articles for each stock in a user's portfolio.

---

## Objectives

### Phase 1 (Current): Basic News Retrieval
- ✅ Accept a portfolio list of stock symbols
- ✅ Retrieve recent news for each stock
- ✅ Structure news data for storage/analysis
- ✅ Handle API rate limits and errors gracefully

### Phase 2 (Future):
- 🔲 Sentiment analysis on news articles
- 🔲 Identify market-moving events
- 🔲 Score news impact (high/medium/low)
- 🔲 Real-time monitoring with webhooks

---

## Architecture

### Design Pattern Used
- **Tool Use Pattern**: Agent uses external news APIs as tools
- **Error Handling**: Graceful fallback and retry logic
- **Simple Iteration**: Process each stock sequentially (parallelization later)

### Data Flow

```
Portfolio Input
  ["AAPL", "TSLA", "GOOGL", "MSFT"]
         ↓
For Each Stock Symbol:
  1. Query News API
  2. Filter & Clean Results
  3. Structure Data
  4. Store/Return
         ↓
Aggregated News Output
  {
    "AAPL": [articles...],
    "TSLA": [articles...],
    "GOOGL": [articles...],
    "MSFT": [articles...]
  }
```

---

## Data Models

### Input: Portfolio

```python
class Portfolio:
    portfolio_id: str
    user_id: str
    stocks: List[str]  # ["AAPL", "TSLA", "GOOGL"]
    created_at: datetime
    last_updated: datetime
```

### Output: News Article

```python
class NewsArticle:
    article_id: str
    symbol: str           # Stock symbol (e.g., "AAPL")
    title: str
    description: str
    url: str
    source: str          # News source (e.g., "Bloomberg")
    published_at: datetime
    sentiment: Optional[str]  # Phase 2: "positive", "negative", "neutral"
    impact_score: Optional[float]  # Phase 2: 0.0 to 1.0
    retrieved_at: datetime
```

### Output: Agent Result

```python
class NewsAgentResult:
    portfolio_id: str
    execution_id: str
    status: str  # "success", "partial_success", "failed"
    news_by_stock: Dict[str, List[NewsArticle]]
    errors: List[Dict[str, Any]]  # Any errors encountered
    total_articles: int
    executed_at: datetime
    execution_time_seconds: float
```

---

## News API Options

### Option 1: NewsAPI.org (Recommended for MVP)
**Pros**:
- ✅ Easy to use
- ✅ Good free tier (100 requests/day)
- ✅ Stock/company search capability
- ✅ Well-documented Python client

**Cons**:
- ❌ Free tier has 1-month historical limit
- ❌ Rate limits can be restrictive

**Pricing**:
- Free: 100 requests/day, 1-month history
- Developer: $449/month, unlimited requests, 2-year history

**API Example**:
```python
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='YOUR_API_KEY')

articles = newsapi.get_everything(
    q='Apple OR AAPL',
    language='en',
    sort_by='publishedAt',
    page_size=20
)
```

### Option 2: Alpha Vantage News API
**Pros**:
- ✅ Financial focus
- ✅ Free tier available
- ✅ Includes sentiment scores
- ✅ Stock-specific queries

**Cons**:
- ❌ 25 requests/day on free tier
- ❌ More complex API

**Pricing**:
- Free: 25 requests/day
- $49.99/month: 1200 requests/day

**API Example**:
```python
import requests

url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=YOUR_API_KEY'
response = requests.get(url)
data = response.json()
```

### Option 3: Finnhub (Best for Financial News)
**Pros**:
- ✅ Financial market focus
- ✅ Real-time news
- ✅ Good free tier (60 requests/minute)
- ✅ WebSocket support for real-time

**Cons**:
- ❌ Limited historical data on free tier

**Pricing**:
- Free: 60 API calls/minute
- $59/month: Enhanced limits

**API Example**:
```python
import finnhub

finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")

news = finnhub_client.company_news('AAPL', _from="2024-01-01", to="2024-12-31")
```

### Option 4: Polygon.io
**Pros**:
- ✅ Comprehensive financial data
- ✅ News included in stock data
- ✅ Developer-friendly

**Cons**:
- ❌ No free tier for news
- ❌ Starts at $99/month

### **Recommendation**: Start with **NewsAPI.org** for MVP, migrate to **Finnhub** or **Alpha Vantage** for production

---

## Implementation Plan

### Phase 1: Basic News Retrieval (MVP)

#### Step 1: Setup Project Structure
```
Event-Horizon/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class
│   ├── news_agent.py          # News retrieval agent
│   └── config.py              # Agent configurations
├── models/
│   ├── __init__.py
│   ├── portfolio.py           # Portfolio data model
│   └── news.py                # News article models
├── services/
│   ├── __init__.py
│   └── news_api_client.py     # News API wrapper
├── utils/
│   ├── __init__.py
│   ├── logger.py              # Logging utilities
│   └── cache.py               # Simple caching
├── tests/
│   ├── test_news_agent.py
│   └── test_news_api_client.py
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── main.py                    # Entry point for testing
```

#### Step 2: Define Dependencies

**requirements.txt**:
```txt
# Core Dependencies
python-dotenv==1.0.0
requests==2.31.0
pydantic==2.5.3

# News APIs
newsapi-python==0.2.7          # NewsAPI.org client
finnhub-python==2.4.19         # Finnhub client (optional)

# Utilities
tenacity==8.2.3                # Retry logic
python-dateutil==2.8.2         # Date handling
cachetools==5.3.2              # Simple caching

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
```

#### Step 3: Implement Base Agent Class

**Purpose**: Common functionality for all agents

**Key Features**:
- Logging
- Error handling
- Execution tracking
- Status reporting

#### Step 4: Implement News API Client

**Purpose**: Abstract away API details, handle rate limits, retries

**Key Features**:
- API authentication
- Request retry with exponential backoff
- Response parsing and validation
- Error handling and logging
- Simple in-memory cache

#### Step 5: Implement News Agent

**Purpose**: Core agent logic for news retrieval

**Key Features**:
- Accept portfolio input
- Iterate through stocks
- Call News API client
- Aggregate results
- Return structured output

#### Step 6: Create Simple Test/Demo Script

**Purpose**: Test the agent with sample portfolio

---

## Implementation Code

### 1. Base Agent Class

```python
# agents/base_agent.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict
import logging
import uuid

class BaseAgent(ABC):
    """Base class for all Event Horizon agents"""

    def __init__(self, agent_name: str, config: Dict[str, Any] = None):
        self.agent_name = agent_name
        self.config = config or {}
        self.logger = logging.getLogger(f"agents.{agent_name}")

    def execute(self, input_data: Any) -> Dict[str, Any]:
        """Execute agent with input data"""
        execution_id = str(uuid.uuid4())
        start_time = datetime.now()

        self.logger.info(f"Starting execution {execution_id}")

        try:
            result = self._execute_internal(input_data)
            status = "success"
            error = None
        except Exception as e:
            self.logger.error(f"Execution {execution_id} failed: {str(e)}", exc_info=True)
            result = None
            status = "failed"
            error = str(e)

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        return {
            "execution_id": execution_id,
            "agent_name": self.agent_name,
            "status": status,
            "result": result,
            "error": error,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "execution_time_seconds": execution_time
        }

    @abstractmethod
    def _execute_internal(self, input_data: Any) -> Any:
        """Internal execution logic - implement in subclass"""
        pass
```

### 2. News API Client

```python
# services/news_api_client.py
import os
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

class NewsAPIClient:
    """Client for fetching news from NewsAPI.org"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
        self.logger = logging.getLogger("services.news_api_client")

        if not self.api_key:
            raise ValueError("NEWS_API_KEY not found in environment")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def get_stock_news(
        self,
        symbol: str,
        days_back: int = 7,
        max_articles: int = 20,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Fetch news for a specific stock symbol

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            days_back: Number of days to look back
            max_articles: Maximum number of articles to return
            language: Language code (default: "en")

        Returns:
            List of news articles
        """
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)

        # Build query - search for both symbol and common company names
        # You might want to add a mapping of symbols to company names
        query = f"{symbol} OR {self._get_company_name(symbol)}"

        params = {
            "q": query,
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d"),
            "language": language,
            "sortBy": "publishedAt",
            "pageSize": max_articles,
            "apiKey": self.api_key
        }

        try:
            response = requests.get(f"{self.base_url}/everything", params=params)
            response.raise_for_status()

            data = response.json()

            if data.get("status") != "ok":
                self.logger.error(f"NewsAPI error for {symbol}: {data.get('message')}")
                return []

            articles = data.get("articles", [])
            self.logger.info(f"Retrieved {len(articles)} articles for {symbol}")

            return self._format_articles(symbol, articles)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch news for {symbol}: {str(e)}")
            return []

    def _format_articles(self, symbol: str, articles: List[Dict]) -> List[Dict[str, Any]]:
        """Format API response into standardized structure"""
        formatted = []

        for article in articles:
            formatted.append({
                "symbol": symbol,
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "published_at": article.get("publishedAt", ""),
                "image_url": article.get("urlToImage"),
                "content": article.get("content", ""),
                "retrieved_at": datetime.now().isoformat()
            })

        return formatted

    def _get_company_name(self, symbol: str) -> str:
        """Map stock symbol to company name for better search results"""
        # Simple mapping - expand this as needed
        symbol_map = {
            "AAPL": "Apple",
            "TSLA": "Tesla",
            "GOOGL": "Google Alphabet",
            "MSFT": "Microsoft",
            "AMZN": "Amazon",
            "META": "Meta Facebook",
            "NVDA": "Nvidia",
            "NFLX": "Netflix"
        }
        return symbol_map.get(symbol, symbol)
```

### 3. News Agent Implementation

```python
# agents/news_agent.py
from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from services.news_api_client import NewsAPIClient
import logging

class NewsAgent(BaseAgent):
    """Agent for retrieving financial news about portfolio stocks"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("news_agent", config)
        self.news_client = NewsAPIClient()
        self.max_articles_per_stock = config.get("max_articles_per_stock", 20)
        self.days_back = config.get("days_back", 7)

    def _execute_internal(self, input_data: Any) -> Dict[str, Any]:
        """
        Execute news retrieval for portfolio stocks

        Args:
            input_data: Dict with "portfolio" key containing list of stock symbols

        Returns:
            Dict with news organized by stock symbol
        """
        # Extract portfolio
        if isinstance(input_data, dict):
            stocks = input_data.get("portfolio", [])
            portfolio_id = input_data.get("portfolio_id", "unknown")
        elif isinstance(input_data, list):
            stocks = input_data
            portfolio_id = "unknown"
        else:
            raise ValueError("Input must be dict with 'portfolio' key or list of symbols")

        if not stocks:
            raise ValueError("Portfolio is empty")

        self.logger.info(f"Processing {len(stocks)} stocks: {stocks}")

        # Retrieve news for each stock
        news_by_stock = {}
        errors = []
        total_articles = 0

        for symbol in stocks:
            self.logger.info(f"Fetching news for {symbol}")

            try:
                articles = self.news_client.get_stock_news(
                    symbol=symbol,
                    days_back=self.days_back,
                    max_articles=self.max_articles_per_stock
                )

                news_by_stock[symbol] = articles
                total_articles += len(articles)

                self.logger.info(f"Retrieved {len(articles)} articles for {symbol}")

            except Exception as e:
                error_msg = f"Failed to fetch news for {symbol}: {str(e)}"
                self.logger.error(error_msg)
                errors.append({
                    "symbol": symbol,
                    "error": str(e)
                })
                news_by_stock[symbol] = []

        # Determine overall status
        if len(errors) == len(stocks):
            status = "failed"
        elif errors:
            status = "partial_success"
        else:
            status = "success"

        return {
            "portfolio_id": portfolio_id,
            "status": status,
            "news_by_stock": news_by_stock,
            "total_articles": total_articles,
            "errors": errors,
            "stocks_processed": len(stocks),
            "stocks_with_errors": len(errors)
        }
```

### 4. Simple Test Script

```python
# main.py
import os
import json
import logging
from dotenv import load_dotenv
from agents.news_agent import NewsAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Load environment variables
    load_dotenv()

    # Create test portfolio
    test_portfolio = {
        "portfolio_id": "test_001",
        "user_id": "user_123",
        "portfolio": ["AAPL", "TSLA", "GOOGL", "MSFT"]
    }

    print("=" * 60)
    print("Event Horizon - News Agent Test")
    print("=" * 60)
    print(f"Portfolio: {test_portfolio['portfolio']}")
    print("-" * 60)

    # Create and configure agent
    agent_config = {
        "max_articles_per_stock": 10,  # Limit for testing
        "days_back": 7
    }

    agent = NewsAgent(config=agent_config)

    # Execute agent
    print("Executing News Agent...")
    result = agent.execute(test_portfolio)

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(f"Execution Time: {result['execution_time_seconds']:.2f} seconds")
    print(f"Execution ID: {result['execution_id']}")

    if result['result']:
        agent_result = result['result']
        print(f"\nTotal Articles Retrieved: {agent_result['total_articles']}")
        print(f"Stocks Processed: {agent_result['stocks_processed']}")

        if agent_result.get('errors'):
            print(f"Errors: {agent_result['stocks_with_errors']}")

        print("\n" + "-" * 60)
        print("Articles by Stock:")
        print("-" * 60)

        for symbol, articles in agent_result['news_by_stock'].items():
            print(f"\n{symbol}: {len(articles)} articles")

            # Show first 2 articles for each stock
            for i, article in enumerate(articles[:2], 1):
                print(f"  {i}. {article['title']}")
                print(f"     Source: {article['source']} | {article['published_at']}")
                print(f"     URL: {article['url'][:60]}...")

        # Save full results to JSON file
        output_file = "news_results.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n\nFull results saved to: {output_file}")

    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()
```

### 5. Environment Setup

**.env.example**:
```bash
# NewsAPI.org credentials
NEWS_API_KEY=your_newsapi_key_here

# Agent Configuration
MAX_ARTICLES_PER_STOCK=20
DAYS_BACK=7

# Logging
LOG_LEVEL=INFO
```

---

## Getting Started

### Step 1: Get API Key
1. Go to [NewsAPI.org](https://newsapi.org/)
2. Sign up for free account
3. Get your API key from dashboard
4. Copy to `.env` file

### Step 2: Install Dependencies
```bash
cd Event-Horizon
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
cp .env.example .env
# Edit .env and add your NEWS_API_KEY
```

### Step 4: Run Test
```bash
python main.py
```

### Expected Output
```
==============================================================
Event Horizon - News Agent Test
==============================================================
Portfolio: ['AAPL', 'TSLA', 'GOOGL', 'MSFT']
--------------------------------------------------------------
Executing News Agent...

==============================================================
RESULTS
==============================================================
Status: success
Execution Time: 4.23 seconds
Execution ID: 8a7f3c4e-1b2d-4f5a-9e8c-7d6f5e4a3b2c

Total Articles Retrieved: 40
Stocks Processed: 4

--------------------------------------------------------------
Articles by Stock:
--------------------------------------------------------------

AAPL: 10 articles
  1. Apple announces new iPhone features...
     Source: TechCrunch | 2024-01-14T10:30:00Z
     URL: https://techcrunch.com/...
  2. Apple stock reaches new high...
     Source: Bloomberg | 2024-01-13T15:45:00Z
     URL: https://bloomberg.com/...

[... more results ...]

Full results saved to: news_results.json
```

---

## Next Steps

### Immediate (Phase 1 Complete)
- ✅ Basic news retrieval working
- ✅ Error handling implemented
- ✅ Structured output format
- ✅ Test script functional

### Phase 2 Enhancements
1. **Add Sentiment Analysis**
   - Integrate sentiment analysis model
   - Score each article: positive/negative/neutral
   - Add confidence scores

2. **Implement Caching**
   - Cache results for X minutes
   - Avoid redundant API calls
   - Redis or simple file cache

3. **Add Parallel Processing**
   - Use asyncio or threading
   - Fetch news for all stocks simultaneously
   - Faster execution time

4. **Database Integration**
   - Store articles in database
   - Track historical news
   - Enable search and filtering

5. **Real-time Monitoring**
   - WebSocket integration for real-time news
   - Push notifications for important events
   - Scheduled background jobs

6. **Impact Scoring**
   - Classify news by impact (high/medium/low)
   - Identify market-moving events
   - Priority ranking

---

## Testing Strategy

### Unit Tests
```python
# tests/test_news_agent.py
def test_news_agent_with_valid_portfolio():
    """Test agent with valid stock symbols"""
    pass

def test_news_agent_with_empty_portfolio():
    """Test agent handles empty portfolio"""
    pass

def test_news_agent_with_invalid_symbol():
    """Test agent handles invalid stock symbol"""
    pass

def test_news_agent_api_failure():
    """Test agent handles API failure gracefully"""
    pass
```

### Integration Tests
- Test with real API (using test API key)
- Verify rate limiting
- Check error recovery

### Performance Tests
- Measure execution time for various portfolio sizes
- Test concurrent requests
- Monitor memory usage

---

## Success Criteria

✅ **MVP Complete When**:
- [ ] Agent retrieves news for all stocks in portfolio
- [ ] Results returned in structured format
- [ ] Errors handled gracefully
- [ ] Execution time < 10 seconds for 5 stocks
- [ ] Test script runs successfully
- [ ] Basic logging implemented

---

## Resources

### APIs
- [NewsAPI.org Documentation](https://newsapi.org/docs)
- [Finnhub API Docs](https://finnhub.io/docs/api)
- [Alpha Vantage News API](https://www.alphavantage.co/documentation/#news-sentiment)

### Libraries
- [Tenacity (Retry Logic)](https://tenacity.readthedocs.io/)
- [Pydantic (Data Validation)](https://docs.pydantic.dev/)
- [Python Logging](https://docs.python.org/3/library/logging.html)

### Design Patterns Reference
- See `20-agentic-design-patterns.md` - Pattern #2: Tool Use

---

**Document Version**: 1.0
**Last Updated**: January 15, 2026
**Status**: Ready for Implementation
