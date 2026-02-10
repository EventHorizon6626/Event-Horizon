# Backend Integration Guide - Node.js Proxy to AI Service

This guide shows how to integrate the AI service with your existing Node.js backend.

---

## Architecture (Option 2 - Recommended)

```
+---------------------+
|  Frontend (Local)   |
|  localhost:3021     |
+----------+----------+
           |
           | HTTPS
           v
+-------------------------------+
|   Backend API (VPS)           |
|   evth-api.hirodev.space      |
|   (Node.js/Express + PM2)     |
+-----------+-------------------+
            |
            | HTTP (localhost only)
            v
+-------------------------------+
|   AI Service (Same VPS)       |
|   localhost:8030              |
|   (Python/FastAPI v3.0.0)     |
|                               |
|   Data Pipeline:              |
|   -- Stage 1 (5 data agents) |
|   -- Stage 2 (normalizer)    |
|   -- Stage 3 (LLM extractor) |
|                               |
|   Analyzer System:            |
|   -- Bull-Bear Analyzer       |
|                               |
|   Services:                   |
|   -- Thinking engine          |
|   -- Web search (Tavily/Exa) |
|   -- Agent CRUD               |
+-------------------------------+
```

**Key Points:**
- Frontend only knows about Backend API (evth-api.hirodev.space)
- Backend proxies requests to AI service on localhost:8030
- AI service NOT exposed to internet (more secure)
- Single entry point for all API calls

---

## Step 1: Update AI Service Configuration

The AI service binds to `localhost` only (not `0.0.0.0`) for security.

### Update `.env` on VPS:

```bash
# /var/www/event-horizon-ai/event_horizon/thinking-multi-agent/.env
LLM_BASE_URL=http://localhost:8000
LLM_MODEL=mistralai/Ministral-3-14B-Reasoning-2512
LLM_API_KEY=
TAVILY_API_KEY=your_tavily_key
AGENTS_FILE=/data/agents.json
LOG_LEVEL=info
```

### Test locally on VPS:

```bash
# Should work (from VPS)
curl http://localhost:8030/health

# Should NOT work (from outside)
curl http://178.18.255.19:8030/health  # Connection refused
```

---

## Step 2: Add Proxy Routes to Node.js Backend

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
const AI_SERVICE_URL = 'http://localhost:8030';
const AI_TIMEOUT = 120000; // 2 minutes for pipeline processing

const aiClient = axios.create({
  baseURL: AI_SERVICE_URL,
  timeout: AI_TIMEOUT,
  headers: { 'Content-Type': 'application/json' }
});

// Health check
router.get('/health', async (req, res) => {
  try {
    const response = await aiClient.get('/health');
    res.json({ backend: 'healthy', ai_service: response.data });
  } catch (error) {
    res.status(503).json({ backend: 'healthy', ai_service: 'unavailable', error: error.message });
  }
});

// Portfolio analysis (Stage 1 pipeline)
router.post('/portfolio/analyze', async (req, res) => {
  try {
    const response = await aiClient.post('/api/v1/analyze-portfolio', req.body);
    res.json(response.data);
  } catch (error) {
    handleProxyError(res, error, 'Portfolio analysis');
  }
});

// Generic proxy for named agent endpoints
const agentEndpoints = [
  'candlestick', 'earnings', 'news', 'technical', 'fundamentals',
  'web-search', 'bull-bear-analyzer', 'custom', 'think'
];

agentEndpoints.forEach(endpoint => {
  router.post(`/agents/${endpoint}`, async (req, res) => {
    try {
      const timeout = endpoint === 'think' ? 180000 : AI_TIMEOUT; // 3 min for thinking
      const response = await aiClient.post(`/agents/${endpoint}`, req.body, { timeout });
      res.json(response.data);
    } catch (error) {
      handleProxyError(res, error, `Agent ${endpoint}`);
    }
  });
});

// Agent CRUD
router.post('/agents', async (req, res) => {
  try { res.json((await aiClient.post('/agents', req.body)).data); }
  catch (error) { handleProxyError(res, error, 'Create agent'); }
});

router.get('/agents', async (req, res) => {
  try { res.json((await aiClient.get('/agents')).data); }
  catch (error) { handleProxyError(res, error, 'List agents'); }
});

router.get('/agents/:id', async (req, res) => {
  try { res.json((await aiClient.get(`/agents/${req.params.id}`)).data); }
  catch (error) { handleProxyError(res, error, 'Get agent'); }
});

router.delete('/agents/:id', async (req, res) => {
  try { res.json((await aiClient.delete(`/agents/${req.params.id}`)).data); }
  catch (error) { handleProxyError(res, error, 'Delete agent'); }
});

router.post('/agents/:id/analyze', async (req, res) => {
  try { res.json((await aiClient.post(`/agents/${req.params.id}/analyze`, req.body)).data); }
  catch (error) { handleProxyError(res, error, 'Dispatch agent'); }
});

// General analysis
router.post('/analyze', async (req, res) => {
  try { res.json((await aiClient.post('/analyze', req.body)).data); }
  catch (error) { handleProxyError(res, error, 'Analysis'); }
});

function handleProxyError(res, error, context) {
  console.error(`[AI Proxy] ${context} failed:`, error.message);
  if (error.response) {
    res.status(error.response.status).json(error.response.data);
  } else if (error.code === 'ECONNREFUSED') {
    res.status(503).json({ success: false, error: 'AI service is temporarily unavailable' });
  } else {
    res.status(500).json({ success: false, error: 'Internal server error' });
  }
}

module.exports = router;
```

### Add Routes to Main App

```javascript
const aiProxyRoutes = require('./routes/ai-proxy');
app.use('/api/ai', aiProxyRoutes);
```

---

## Step 3: Testing the Integration

### Test 1: Health Check

```bash
curl https://evth-api.hirodev.space/api/ai/health
```

### Test 2: Portfolio Analysis

```bash
curl -X POST https://evth-api.hirodev.space/api/ai/portfolio/analyze \
  -H "Content-Type: application/json" \
  -d '{"portfolio": ["AAPL", "GOOGL"]}'
```

### Test 3: Thinking Agent

```bash
curl -X POST https://evth-api.hirodev.space/api/ai/agents/think \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL"], "system_prompt": "Analyze for value investing", "max_iterations": 3}'
```

---

## API Route Summary

### Frontend calls Backend:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ai/health` | GET | Health check |
| `/api/ai/portfolio/analyze` | POST | Full Stage 1 pipeline |
| `/api/ai/agents/candlestick` | POST | OHLCV price data |
| `/api/ai/agents/earnings` | POST | Earnings/financials |
| `/api/ai/agents/news` | POST | News articles |
| `/api/ai/agents/technical` | POST | Technical indicators |
| `/api/ai/agents/fundamentals` | POST | Fundamental metrics |
| `/api/ai/agents/web-search` | POST | Web search (Tavily/Exa) |
| `/api/ai/agents/bull-bear-analyzer` | POST | Bull-bear debate analysis |
| `/api/ai/agents/think` | POST | Thinking agent (ReAct) |
| `/api/ai/agents/custom` | POST | Custom agent execution |
| `/api/ai/agents` | POST | Create agent |
| `/api/ai/agents` | GET | List all agents |
| `/api/ai/agents/:id` | GET | Get agent details |
| `/api/ai/agents/:id` | DELETE | Delete agent |
| `/api/ai/agents/:id/analyze` | POST | Dispatch agent analysis |
| `/api/ai/analyze` | POST | General analysis |

### Backend proxies to AI Service:

| Backend Route | AI Service Route |
|---------------|------------------|
| `/api/ai/health` | `http://localhost:8030/health` |
| `/api/ai/portfolio/analyze` | `http://localhost:8030/api/v1/analyze-portfolio` |
| `/api/ai/agents/{name}` | `http://localhost:8030/agents/{name}` |
| `/api/ai/agents` | `http://localhost:8030/agents` |
| `/api/ai/agents/:id/analyze` | `http://localhost:8030/agents/{id}/analyze` |
| `/api/ai/analyze` | `http://localhost:8030/analyze` |

---

## Firewall Configuration

```bash
# Block AI service port from external access
sudo ufw deny 8030/tcp

# Allow Backend API port
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

---

## Deployment Checklist

- [ ] AI service deployed and running on localhost:8030
- [ ] LLM backend (vLLM) running and accessible from AI service
- [ ] Node.js backend has proxy routes (`/api/ai/*`)
- [ ] Backend `axios` dependency installed
- [ ] Port 8030 blocked from external access (firewall)
- [ ] Frontend `.env` has only `REACT_APP_BE_API_URL`
- [ ] Health check works: `curl https://evth-api.hirodev.space/api/ai/health`
- [ ] Portfolio analysis works from frontend

---

## Troubleshooting

### Backend can't connect to AI service

```bash
# On VPS, check if AI service is running
curl http://localhost:8030/health

# Check what's on port 8030
sudo lsof -i :8030
```

### Timeout errors

AI processing can take 30-120 seconds depending on the endpoint. The thinking agent can take up to 3 minutes. Adjust timeouts accordingly.

---

**Done! Your architecture is now secure and scalable.**
