# Event Horizon AI - System Architecture

## Option 2: Backend Proxy Architecture (Recommended ✅)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          User's Browser                                 │
│                     http://localhost:3021                               │
│                        (React Frontend)                                 │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ HTTPS
                                 │ fetch(REACT_APP_BE_API_URL + '/ai/...')
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          VPS Server                                     │
│                   178.18.255.19 or domain                               │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │        Backend API (Node.js/Express + PM2)                        │ │
│  │        https://evth-api.hirodev.space/api                         │ │
│  │                                                                   │ │
│  │  Routes:                                                          │ │
│  │  - /api/ai/health            → Health check                       │ │
│  │  - /api/ai/portfolio/analyze → Full analysis                      │ │
│  │  - /api/ai/news              → News only                          │ │
│  │  - /api/ai/reports           → Reports only                       │ │
│  │  - /api/... (other endpoints)                                     │ │
│  └───────────────────────────┬───────────────────────────────────────┘ │
│                              │                                         │
│                              │ HTTP (localhost only)                   │
│                              │ axios.post('http://localhost:5000/...')  │
│                              │                                         │
│                              ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │        AI Service (Python/FastAPI)                              │  │
│  │        http://127.0.0.1:5000                                    │  │
│  │        (NOT exposed to internet - localhost only)               │  │
│  │                                                                 │  │
│  │  Endpoints:                                                     │  │
│  │  - GET  /health                                                 │  │
│  │  - POST /api/portfolio/analyze                                  │  │
│  │  - POST /api/news                                               │  │
│  │  - POST /api/reports                                            │  │
│  │                                                                 │  │
│  │  AI Agents:                                                     │  │
│  │  ├─ NewsAgent              (NewsAPI.org integration)            │  │
│  │  ├─ ReportAnalysisAgent    (Yahoo Finance integration)          │  │
│  │  ├─ SentimentAgent         (Future)                             │  │
│  │  ├─ TechnicalAnalysisAgent (Future)                             │  │
│  │  └─ RiskAssessmentAgent    (Future)                             │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Request Flow

### Example: Portfolio Analysis

1. **User Action** (Frontend - localhost:3021)
   ```javascript
   analyzePortfolio(['AAPL', 'GOOGL', 'TSLA'])
   ```

2. **Frontend → Backend** (HTTPS)
   ```javascript
   POST https://evth-api.hirodev.space/api/ai/portfolio/analyze
   Body: { stocks: ['AAPL', 'GOOGL', 'TSLA'] }
   ```

3. **Backend → AI Service** (HTTP localhost)
   ```javascript
   POST http://localhost:5000/api/portfolio/analyze
   Body: { stocks: ['AAPL', 'GOOGL', 'TSLA'] }
   ```

4. **AI Service Processes**
   - Initializes NewsAgent
   - Initializes ReportAnalysisAgent
   - Executes agents in parallel
   - Fetches news from NewsAPI.org
   - Fetches financial data from Yahoo Finance
   - Combines results

5. **AI Service → Backend** (Response)
   ```json
   {
     "portfolio": ["AAPL", "GOOGL", "TSLA"],
     "analysis_timestamp": "2026-01-17T...",
     "news_data": { ... },
     "report_data": { ... },
     "summary": { ... }
   }
   ```

6. **Backend → Frontend** (Response)
   - Same JSON response forwarded

7. **Frontend Displays Results**
   - Shows news articles
   - Shows financial metrics
   - Shows analysis summary

---

## Components Breakdown

### 1. Frontend (React)

**Location:** Separate repository
**Port:** 3021 (development)
**Environment:**
- `REACT_APP_BE_API_URL=https://evth-api.hirodev.space/api`

**Responsibilities:**
- User interface
- Portfolio input
- API calls to Backend
- Results visualization

---

### 2. Backend API (Node.js/Express)

**Location:** Separate repository
**Port:** 80/443 (behind Nginx)
**Domain:** evth-api.hirodev.space
**Process Manager:** PM2

**Responsibilities:**
- REST API endpoints
- Authentication (JWT/sessions)
- Request validation
- Proxy to AI service
- Rate limiting
- Logging
- Error handling

**Routes:**
```
/api/ai/health              → GET  → AI health check
/api/ai/portfolio/analyze   → POST → Full portfolio analysis
/api/ai/news                → POST → News only
/api/ai/reports             → POST → Financial reports only
... other app routes ...
```

---

### 3. AI Service (Python/FastAPI)

**Location:** This repository (`Event-Horizon-AI`)
**Port:** 5000 (localhost only)
**Process Manager:** systemd
**Path:** `/var/www/event-horizon-ai`

**Responsibilities:**
- Execute AI agents
- Fetch financial news
- Fetch financial reports
- Process and combine data
- Return structured JSON

**API Endpoints:**
```python
GET  /                       # Service info
GET  /health                 # Health check
POST /api/portfolio/analyze  # Full analysis (news + reports)
POST /api/news               # News only
POST /api/reports            # Reports only
GET  /docs                   # Swagger documentation
```

**Agents:**
- `NewsAgent` - Fetches news from NewsAPI.org
- `ReportAnalysisAgent` - Fetches financial data from Yahoo Finance
- (Future agents can be added easily)

---

## Data Flow Example

### Input:
```json
{
  "stocks": ["AAPL", "GOOGL", "TSLA"]
}
```

### Processing:

1. **NewsAgent** executes:
   - Queries NewsAPI.org for each stock
   - Fetches recent news articles
   - Filters and structures data

2. **ReportAnalysisAgent** executes:
   - Queries Yahoo Finance for each stock
   - Fetches earnings reports
   - Fetches financial metrics
   - Structures data

3. **Combine results** into unified response

### Output:
```json
{
  "portfolio": ["AAPL", "GOOGL", "TSLA"],
  "analysis_timestamp": "2026-01-17T10:30:00Z",
  "news_data": {
    "success": true,
    "data": {
      "articles": [
        {
          "symbol": "AAPL",
          "title": "Apple announces...",
          "source": "TechCrunch",
          "url": "https://...",
          "published_at": "2026-01-17T08:00:00Z"
        }
      ]
    }
  },
  "report_data": {
    "success": true,
    "data": {
      "reports": {
        "AAPL": {
          "symbol": "AAPL",
          "name": "Apple Inc.",
          "metrics": {
            "market_cap": 3000000000000,
            "pe_ratio": 28.5,
            "earnings_date": "2026-01-25"
          },
          "financials": { ... }
        }
      }
    }
  },
  "summary": {
    "total_stocks": 3,
    "news_articles_count": 25,
    "reports_fetched": 3,
    "analysis_status": "completed"
  }
}
```

---

## Security Features

### 1. AI Service Isolation
- ✅ Binds to `127.0.0.1` only (not `0.0.0.0`)
- ✅ NOT accessible from internet
- ✅ Only Backend on same VPS can access it

### 2. Backend as Gateway
- ✅ Single entry point for frontend
- ✅ Can add authentication layer
- ✅ Can add rate limiting
- ✅ Input validation before forwarding

### 3. Firewall
- ✅ Port 5000 blocked from external access
- ✅ Only 80/443 exposed for Backend API

---

## Scalability

### Current Setup (Single VPS)
```
Frontend → Backend + AI Service (same VPS)
```
Good for: MVP, small-medium traffic

### Future Scaling Options

#### Option A: Separate AI Service VPS
```
Frontend → Backend (VPS 1) → AI Service (VPS 2)
```
- Deploy AI service on separate VPS
- Backend proxies to `http://ai-service-ip:5000`

#### Option B: Load Balancer + Multiple AI Services
```
Frontend → Backend → Load Balancer → AI Service 1
                                   → AI Service 2
                                   → AI Service 3
```
- Deploy multiple AI service instances
- Use Nginx or HAProxy to balance load

#### Option C: Microservices
```
Frontend → API Gateway → News Service (specialized)
                      → Report Service (specialized)
                      → Sentiment Service (specialized)
```
- Split agents into separate services
- Each service independently scalable

---

## Deployment Architecture

### Development
```
Frontend (local:3021) → Backend (VPS) → AI Service (VPS)
```

### Production (Future)
```
Frontend (CDN/Static Host) → Backend (VPS/Cloud) → AI Service (VPS/Cloud)
```

---

## Technologies Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | React | User interface |
| Backend API | Node.js/Express | REST API, proxy |
| AI Service | Python/FastAPI | AI agents execution |
| Process Mgmt (BE) | PM2 | Backend process manager |
| Process Mgmt (AI) | systemd | AI service manager |
| News Data | NewsAPI.org | Financial news source |
| Financial Data | Yahoo Finance | Stock/ETF data source |
| Deployment | Git + Manual | Code deployment |

---

## Environment Configuration

### Frontend `.env`
```bash
REACT_APP_BE_API_URL=https://evth-api.hirodev.space/api
NODE_ENV=development
PORT=3021
```

### Backend `.env`
```bash
# Your backend env vars
# ...
```

### AI Service `.env`
```bash
NEWS_API_KEY=your_actual_key_here
API_HOST=127.0.0.1
API_PORT=5000
LOG_LEVEL=INFO
```

---

## Monitoring & Logs

### AI Service
```bash
# Status
sudo systemctl status event-horizon-ai

# Logs
sudo journalctl -u event-horizon-ai -f

# Recent logs
sudo journalctl -u event-horizon-ai -n 100
```

### Backend
```bash
# PM2 status
pm2 status

# Logs
pm2 logs

# Monitor
pm2 monit
```

---

## Future Enhancements

### Planned Agents
- [ ] Sentiment Analysis Agent (FinBERT)
- [ ] Technical Analysis Agent (Chart patterns)
- [ ] Risk Assessment Agent (Portfolio risk metrics)
- [ ] Social Media Agent (Twitter/Reddit sentiment)

### Infrastructure
- [ ] Redis caching layer
- [ ] PostgreSQL for data persistence
- [ ] Celery for background tasks
- [ ] WebSocket for real-time updates

### Features
- [ ] User authentication
- [ ] Portfolio tracking
- [ ] Historical analysis
- [ ] Alerts and notifications

---

**Current Status:** Option 2 Architecture ✅
**Security:** AI Service isolated, localhost-only ✅
**Scalability:** Ready for future scaling ✅
