# Backend Integration Guide - Node.js Proxy to AI Service

This guide shows how to integrate the AI service with your existing Node.js backend.

---

## Architecture (Option 2 - Recommended)

```
┌─────────────────────┐
│  Frontend (Local)   │
│  localhost:3021     │
└──────────┬──────────┘
           │
           │ HTTPS
           ▼
┌───────────────────────────────┐
│   Backend API (VPS)           │
│   evth-api.hirodev.space      │
│   (Node.js/Express + PM2)     │
└───────────┬───────────────────┘
            │
            │ HTTP (localhost only)
            ▼
┌───────────────────────────────┐
│   AI Service (Same VPS)       │
│   localhost:5000              │
│   (Python/FastAPI)            │
│                               │
│   ├─ NewsAgent                │
│   ├─ ReportAgent              │
│   └─ Future agents            │
└───────────────────────────────┘
```

**Key Points:**
- Frontend only knows about Backend API (evth-api.hirodev.space)
- Backend proxies requests to AI service on localhost:5000
- AI service NOT exposed to internet (more secure)
- Single entry point for all API calls

---

## Step 1: Update AI Service Configuration

The AI service should bind to `localhost` only (not `0.0.0.0`) for security.

### Update `.env` on VPS:

```bash
# /var/www/event-horizon-ai/.env
NEWS_API_KEY=your_actual_key_here
LOG_LEVEL=INFO

# Bind to localhost only (not exposed to internet)
API_HOST=127.0.0.1
API_PORT=5000
```

### Restart AI service:

```bash
sudo systemctl restart event-horizon-ai
```

### Test locally on VPS:

```bash
# Should work (from VPS)
curl http://localhost:5000/health

# Should NOT work (from outside)
curl http://178.18.255.19:5000/health  # Connection refused
```

---

## Step 2: Add Proxy Routes to Node.js Backend

In your Node.js backend repository, add these routes.

### Install Dependencies

```bash
cd /path/to/your/nodejs/backend
npm install axios
```

### Create AI Proxy Module

Create `routes/ai-proxy.js`:

```javascript
const express = require('express');
const axios = require('axios');
const router = express.Router();

// AI Service configuration
const AI_SERVICE_URL = 'http://localhost:5000';
const AI_TIMEOUT = 60000; // 60 seconds for AI processing

// Create axios instance with default config
const aiClient = axios.create({
  baseURL: AI_SERVICE_URL,
  timeout: AI_TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * Health check for AI service
 * GET /api/ai/health
 */
router.get('/health', async (req, res) => {
  try {
    const response = await aiClient.get('/health');
    res.json({
      backend: 'healthy',
      ai_service: response.data
    });
  } catch (error) {
    console.error('AI health check failed:', error.message);
    res.status(503).json({
      backend: 'healthy',
      ai_service: 'unavailable',
      error: error.message
    });
  }
});

/**
 * Full Portfolio Analysis (News + Reports)
 * POST /api/ai/portfolio/analyze
 *
 * Body: {
 *   stocks: ["AAPL", "GOOGL", "TSLA"]
 * }
 */
router.post('/portfolio/analyze', async (req, res) => {
  try {
    const { stocks } = req.body;

    // Validate input
    if (!stocks || !Array.isArray(stocks) || stocks.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Invalid request. Provide an array of stock symbols.'
      });
    }

    console.log(`[AI Proxy] Analyzing portfolio: ${stocks.join(', ')}`);

    // Forward request to AI service
    const response = await aiClient.post('/api/portfolio/analyze', {
      stocks: stocks
    });

    res.json(response.data);

  } catch (error) {
    console.error('[AI Proxy] Portfolio analysis failed:', error.message);

    if (error.response) {
      // AI service returned an error
      res.status(error.response.status).json(error.response.data);
    } else if (error.code === 'ECONNREFUSED') {
      // AI service is down
      res.status(503).json({
        success: false,
        error: 'AI service is temporarily unavailable'
      });
    } else {
      // Other errors
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    }
  }
});

/**
 * Get News Only
 * POST /api/ai/news
 *
 * Body: {
 *   stocks: ["AAPL", "GOOGL"]
 * }
 */
router.post('/news', async (req, res) => {
  try {
    const { stocks } = req.body;

    if (!stocks || !Array.isArray(stocks) || stocks.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Invalid request. Provide an array of stock symbols.'
      });
    }

    console.log(`[AI Proxy] Fetching news for: ${stocks.join(', ')}`);

    const response = await aiClient.post('/api/news', { stocks });
    res.json(response.data);

  } catch (error) {
    console.error('[AI Proxy] News fetch failed:', error.message);

    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({
        success: false,
        error: 'Failed to fetch news'
      });
    }
  }
});

/**
 * Get Financial Reports Only
 * POST /api/ai/reports
 *
 * Body: {
 *   stocks: ["AAPL", "GOOGL"]
 * }
 */
router.post('/reports', async (req, res) => {
  try {
    const { stocks } = req.body;

    if (!stocks || !Array.isArray(stocks) || stocks.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Invalid request. Provide an array of stock symbols.'
      });
    }

    console.log(`[AI Proxy] Fetching reports for: ${stocks.join(', ')}`);

    const response = await aiClient.post('/api/reports', { stocks });
    res.json(response.data);

  } catch (error) {
    console.error('[AI Proxy] Reports fetch failed:', error.message);

    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({
        success: false,
        error: 'Failed to fetch reports'
      });
    }
  }
});

module.exports = router;
```

### Add Routes to Main App

In your main `app.js` or `index.js`:

```javascript
const express = require('express');
const app = express();

// ... your existing middleware ...

// Import AI proxy routes
const aiProxyRoutes = require('./routes/ai-proxy');

// Mount AI routes
app.use('/api/ai', aiProxyRoutes);

// ... rest of your routes ...

app.listen(PORT, () => {
  console.log(`Backend API listening on port ${PORT}`);
});
```

### Restart Backend

```bash
# If using PM2
pm2 restart your-backend-app

# Or
pm2 restart all
```

---

## Step 3: Update Frontend Configuration

### Frontend `.env` (Remove AI_API_URL)

```bash
# Backend API (running on VPS via PM2)
REACT_APP_BE_API_URL=https://evth-api.hirodev.space/api

# Remove this line - no longer needed!
# REACT_APP_AI_API_URL=http://178.18.255.19:5000

NODE_ENV=development
REACT_APP_PROJECT_NAME=EventHorizon
REACT_APP_SMALL_NAME=eventhorizon
REACT_APP_CONTACT_EMAIL=support@eventhorizon.io
GENERATE_SOURCEMAP=false
PORT=3021

TSC_COMPILE_ON_ERROR=true
DISABLE_ESLINT_PLUGIN=true
SKIP_PREFLIGHT_CHECK=true
```

### Frontend API Calls

Update your React code to only call the Backend API:

```javascript
// services/api.js or wherever you make API calls

const API_BASE = process.env.REACT_APP_BE_API_URL;

/**
 * Analyze portfolio using AI agents
 */
export const analyzePortfolio = async (stocks) => {
  const response = await fetch(`${API_BASE}/ai/portfolio/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ stocks })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
};

/**
 * Get news only
 */
export const getNews = async (stocks) => {
  const response = await fetch(`${API_BASE}/ai/news`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ stocks })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
};

/**
 * Get financial reports only
 */
export const getReports = async (stocks) => {
  const response = await fetch(`${API_BASE}/ai/reports`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ stocks })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
};

/**
 * Check AI service health
 */
export const checkAIHealth = async () => {
  const response = await fetch(`${API_BASE}/ai/health`);
  return await response.json();
};
```

### Usage in React Components

```javascript
import { analyzePortfolio, getNews, getReports } from './services/api';

function PortfolioAnalyzer() {
  const [stocks, setStocks] = useState(['AAPL', 'GOOGL', 'TSLA']);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const result = await analyzePortfolio(stocks);
      setAnalysis(result);
      console.log('Analysis complete:', result);
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Failed to analyze portfolio');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze Portfolio'}
      </button>
      {analysis && <div>{/* Display results */}</div>}
    </div>
  );
}
```

---

## Step 4: Testing the Integration

### Test 1: Health Check

```bash
# Test Backend → AI proxy
curl https://evth-api.hirodev.space/api/ai/health
```

Expected:
```json
{
  "backend": "healthy",
  "ai_service": {
    "status": "healthy",
    "timestamp": "2026-01-17T...",
    "service": "event-horizon-ai"
  }
}
```

### Test 2: Portfolio Analysis

```bash
curl -X POST https://evth-api.hirodev.space/api/ai/portfolio/analyze \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "GOOGL"]}'
```

Expected:
```json
{
  "portfolio": ["AAPL", "GOOGL"],
  "analysis_timestamp": "2026-01-17T...",
  "news_data": {...},
  "report_data": {...},
  "summary": {...}
}
```

### Test 3: From Frontend

In your React app (localhost:3021):

```javascript
// Open browser console
const result = await fetch('https://evth-api.hirodev.space/api/ai/portfolio/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ stocks: ['AAPL', 'TSLA'] })
}).then(r => r.json());

console.log(result);
```

---

## Security Benefits

✅ **AI service not exposed to internet** - Only accessible via localhost
✅ **Single API endpoint** - Frontend only knows about Backend
✅ **Backend can add auth** - Protect AI routes with JWT/sessions
✅ **Rate limiting** - Backend can limit AI calls per user
✅ **Request validation** - Backend validates before forwarding
✅ **Error handling** - Backend provides consistent error responses
✅ **Logging** - Backend logs all AI service calls

---

## Firewall Configuration

Since AI service is localhost-only, **close port 5000** on firewall:

```bash
# Block port 5000 from external access
sudo ufw deny 5000/tcp

# Only allow your Backend API port (if using standalone)
# Usually 80/443 if behind Nginx
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

---

## Deployment Checklist

- [ ] AI service deployed and running on localhost:5000
- [ ] AI service `.env` has `API_HOST=127.0.0.1`
- [ ] Node.js backend has proxy routes (`/api/ai/*`)
- [ ] Backend `axios` dependency installed
- [ ] Backend restarted with new routes
- [ ] Port 5000 blocked from external access (firewall)
- [ ] Frontend `.env` has only `REACT_APP_BE_API_URL`
- [ ] Frontend updated to call backend proxy routes
- [ ] Health check works: `curl https://evth-api.hirodev.space/api/ai/health`
- [ ] Portfolio analysis works from frontend

---

## Monitoring

### Check AI Service Status (on VPS)

```bash
sudo systemctl status event-horizon-ai
sudo journalctl -u event-horizon-ai -f
```

### Check Backend Logs (PM2)

```bash
pm2 logs your-backend-app
pm2 monit
```

### Test Connection

```bash
# On VPS, test AI service directly
curl http://localhost:5000/health

# From outside, test Backend proxy
curl https://evth-api.hirodev.space/api/ai/health
```

---

## API Route Summary

### Frontend calls Backend:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ai/health` | GET | Health check |
| `/api/ai/portfolio/analyze` | POST | Full analysis |
| `/api/ai/news` | POST | News only |
| `/api/ai/reports` | POST | Reports only |

### Backend proxies to AI Service:

| Backend Route | → | AI Service Route |
|---------------|---|------------------|
| `/api/ai/health` | → | `http://localhost:5000/health` |
| `/api/ai/portfolio/analyze` | → | `http://localhost:5000/api/portfolio/analyze` |
| `/api/ai/news` | → | `http://localhost:5000/api/news` |
| `/api/ai/reports` | → | `http://localhost:5000/api/reports` |

---

## Troubleshooting

### Backend can't connect to AI service

```bash
# On VPS, check if AI service is running
sudo systemctl status event-horizon-ai
curl http://localhost:5000/health

# Check if binding to localhost
sudo lsof -i :5000
```

### CORS errors

The AI service already has CORS configured. Make sure your backend domain is allowed in `api_server.py:36-48`.

### Timeout errors

AI processing can take 30-60 seconds. Increase timeout:

```javascript
// In ai-proxy.js
const AI_TIMEOUT = 120000; // 2 minutes
```

---

**Done! Your architecture is now secure and scalable.**
