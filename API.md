# Event Horizon AI - API Documentation

## Base URL
```
http://localhost:8030
```

## Authentication
Currently no authentication required. Add JWT/API keys in production.

---

## Endpoints

### 1. Health Check

**GET** `/health`

Returns service health status.

**Response**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-25T17:30:00",
  "version": "1.0.0"
}
```

---

### 2. Analyze Portfolio

**POST** `/api/v1/analyze-portfolio`

Analyzes a stock portfolio using Stage 1 multi-agent pipeline.

**Request Body**
```json
{
  "portfolio": ["AAPL", "TSLA", "SPY", "NVDA"],
  "portfolio_id": "optional_custom_id",
  "enabled_agents": ["candlestick", "earnings", "news", "technical", "fundamentals"],
  "agent_configs": {
    "candlestick": {
      "period": "1mo",
      "interval": "1d"
    },
    "technical": {
      "indicators": ["SMA", "RSI", "MACD"],
      "look_back_days": 30
    }
  }
}
```

**Parameters**
- `portfolio` (required): Array of stock symbols
- `portfolio_id` (optional): Custom portfolio identifier
- `enabled_agents` (optional): List of agents to run. Default: all 5 agents
- `agent_configs` (optional): Custom configuration per agent

**Response**
```json
{
  "status": "success",
  "stage1_output": {
    "portfolio_id": "portfolio_20260125_173000",
    "symbols": ["AAPL", "TSLA", "SPY", "NVDA"],
    "timestamp": "2026-01-25T17:30:00",

    "chart_data": {
      "AAPL": {
        "symbol": "AAPL",
        "candles": [
          {
            "date": "2026-01-24",
            "open": 230.50,
            "high": 232.00,
            "low": 229.00,
            "close": 231.50,
            "volume": 45000000
          }
        ],
        "period": "1mo",
        "interval": "1d"
      }
    },

    "earnings_data": {
      "AAPL": {
        "name": "Apple Inc.",
        "security_type": "stock",
        "earnings_reports": { ... },
        "financial_statements": { ... }
      }
    },

    "news_data": {
      "AAPL": {
        "articles": [
          {
            "title": "Apple announces new product",
            "description": "...",
            "source": "Reuters",
            "published_at": "2026-01-24T10:00:00"
          }
        ],
        "total_articles": 10
      }
    },

    "technical_data": {
      "AAPL": {
        "indicators": {
          "SMA": "SMA(50): 228.30, SMA(200): 220.15",
          "RSI": "RSI(14): 62.5",
          "MACD": "MACD: 2.3, Signal: 1.8, Histogram: 0.5"
        }
      }
    },

    "fundamentals_data": {
      "AAPL": {
        "fundamentals_text": "P/E: 28.5, ROE: 147%, Debt/Equity: 1.8, ...",
        "data_source": "yfinance"
      }
    },

    "execution_time_seconds": 12.45,
    "agents_executed": ["candlestick", "earnings", "news", "technical", "fundamentals"],
    "errors": []
  },
  "execution_time_seconds": 12.45,
  "agents_executed": [...],
  "errors": []
}
```

**Status Codes**
- `200`: Success
- `500`: Server error (check error message in response)

---

### 3. Get Supported Agents

**GET** `/api/v1/supported-agents`

Returns list of available data agents and their configurations.

**Response**
```json
{
  "agents": [
    {
      "name": "candlestick",
      "description": "OHLCV price data",
      "config_options": ["period", "interval"]
    },
    {
      "name": "earnings",
      "description": "Financial reports & earnings",
      "config_options": ["include_financials", "earnings_periods"]
    },
    {
      "name": "news",
      "description": "News articles & headlines",
      "config_options": ["max_articles_per_stock", "days_back"]
    },
    {
      "name": "technical",
      "description": "Technical indicators (SMA, RSI, MACD)",
      "config_options": ["indicators", "look_back_days"]
    },
    {
      "name": "fundamentals",
      "description": "Fundamental metrics (P/E, ROE, etc.)",
      "config_options": ["include_ratios", "include_financials"]
    }
  ]
}
```

---

## Agent Configuration Options

### Candlestick Agent
```json
{
  "period": "1mo",     // 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
  "interval": "1d"     // 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
}
```

### Earnings Agent
```json
{
  "include_financials": true,
  "earnings_periods": 4,      // Number of quarterly reports
  "top_holdings": 10          // For ETFs
}
```

### News Agent
```json
{
  "max_articles_per_stock": 10,
  "days_back": 7
}
```

### Technical Agent
```json
{
  "indicators": ["SMA", "RSI", "MACD"],
  "look_back_days": 30
}
```

### Fundamentals Agent
```json
{
  "include_ratios": true,
  "include_financials": true
}
```

---

## Example Usage

### cURL
```bash
curl -X POST http://localhost:8030/api/v1/analyze-portfolio \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": ["AAPL", "TSLA", "NVDA"],
    "portfolio_id": "tech_stocks_2026"
  }'
```

### JavaScript (Node.js)
```javascript
const axios = require('axios');

async function analyzePortfolio() {
  const response = await axios.post('http://localhost:8030/api/v1/analyze-portfolio', {
    portfolio: ['AAPL', 'TSLA', 'NVDA'],
    portfolio_id: 'tech_stocks_2026'
  });

  console.log(response.data);
}
```

### Python
```python
import requests

response = requests.post('http://localhost:8030/api/v1/analyze-portfolio', json={
    'portfolio': ['AAPL', 'TSLA', 'NVDA'],
    'portfolio_id': 'tech_stocks_2026'
})

data = response.json()
print(data)
```

---

## CORS

CORS is enabled for all origins (`*`) by default.

**Production**: Update CORS in `event_horizon/thinking-multi-agent/app/main.py` to restrict origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Your FE domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Rate Limiting

Currently no rate limiting. Consider adding in production:
- slowapi
- redis-based rate limiting
- API keys with quotas

---

## Error Handling

All errors return:
```json
{
  "detail": "Error message here"
}
```

Common errors:
- Invalid symbols
- API key missing (for news agent)
- Network errors (Yahoo Finance down)
- Timeout errors (long-running analysis)
