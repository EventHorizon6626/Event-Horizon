# News Retrieval Agent - Design Document

**Agent Type**: Data Retrieval Agent (Stage 1)
**Status**: Implemented
**Last Updated**: 2026-02-10

---

## Overview

The News Agent retrieves real-time news articles for each stock in a portfolio. It is one of 5 specialized agents in Stage 1 of the Data Processing Pipeline.

**Location**: `event_horizon/data_pipeline/stage_1/agents/news_agent.py`
**Service**: `event_horizon/data_pipeline/stage_1/services/news_search_client.py`

---

## Data Sources

### Primary: Tavily Search API

The News Agent uses **Tavily** as its primary news source via the `tavily_news_search()` function in `news_search_client.py`.

**Features**:
- Financial news search with relevance ranking
- Recent articles with summaries
- No scraping required -- structured API responses

**Environment Variable**: `TAVILY_API_KEY`

### Fallback: Exa Search API

If Tavily is unavailable or returns no results, the agent falls back to **Exa** via `exa_news_search()`.

**Environment Variable**: `EXASEARCH_API_KEY`

### Supplementary: Web Search

The FastAPI app also provides a standalone `POST /agents/web-search` endpoint (via `event_horizon/thinking-multi-agent/app/services/web_search.py`) that uses the same Tavily/Exa stack for general web search queries.

### Legacy: NewsAPI.org

The `news_api_client.py` file still exists for backward compatibility but is **not used** by the current News Agent. The agent was migrated from NewsAPI.org to Tavily/Exa for better financial news coverage.

---

## Architecture

### Data Flow

```
Portfolio Input
  ["AAPL", "TSLA", "GOOGL"]
         |
For Each Stock Symbol:
  1. Search Tavily for stock news
  2. If Tavily fails, fallback to Exa
  3. Structure results as NewsData
         |
Aggregated News Output (Dict[str, NewsData])
```

### Integration in Pipeline

```
Stage 1 Orchestrator (parallel)
  |-- CandlestickAgent  -> Yahoo Finance
  |-- EarningsAgent      -> Yahoo Finance
  |-- NewsAgent          -> Tavily / Exa       <-- this agent
  |-- TechnicalAgent     -> yfinance
  +-- FundamentalsAgent  -> yfinance
```

---

## Data Models

### Output: NewsData

```python
@dataclass
class NewsData:
    symbol: str
    articles: List[Dict]       # [{title, source, url, published_at, ...}]
    total_articles: int
    data_source: str           # "tavily", "exa", or "newsapi"
    error: Optional[str]
```

### API Endpoint Output

Via `POST /agents/news`:

```json
{
  "agent_id": "news",
  "agent_name": "news",
  "status": "success",
  "analysis": {
    "AAPL": {
      "symbol": "AAPL",
      "articles": [
        {
          "title": "Apple reports strong quarterly earnings...",
          "source": "Bloomberg",
          "url": "https://...",
          "published_at": "2026-02-09T15:30:00Z"
        }
      ],
      "total_articles": 10,
      "data_source": "tavily"
    }
  }
}
```

---

## Configuration

### Agent Config

```python
{
    "max_articles_per_stock": 10,  # Max articles to retrieve per symbol
    "days_back": 7                 # How far back to search
}
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TAVILY_API_KEY` | Yes (for news) | Tavily search API key |
| `EXASEARCH_API_KEY` | No (fallback) | Exa search API key |

---

## Usage

### Via FastAPI

```bash
curl -X POST http://localhost:8030/agents/news \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "TSLA"], "days": 7}'
```

### Via Python

```python
from event_horizon.data_pipeline.stage_1.agents.news_agent import NewsAgent

agent = NewsAgent(config={"max_articles_per_stock": 10, "days_back": 7})
result = agent.execute({"portfolio": ["AAPL", "TSLA"]})

news_data = result["result"]
for symbol, data in news_data.items():
    print(f"{symbol}: {data.total_articles} articles from {data.data_source}")
```

---

## Error Handling

- If Tavily fails, automatically falls back to Exa
- If both fail, returns `NewsData` with error field set
- Stage 1 orchestrator continues with partial results

---

## Next Steps

### Future Enhancements
- Sentiment analysis on retrieved articles
- Impact scoring (high/medium/low)
- Real-time monitoring with webhooks
- Caching to reduce API calls

---

**Document Version**: 2.0
**Last Updated**: 2026-02-10
