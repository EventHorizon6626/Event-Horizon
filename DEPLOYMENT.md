# Event Horizon AI - Deployment Guide

## Server Architecture

```
/home/vytrieu/EventHorizon/
├── FE/                  # React Frontend (nginx)
├── BE/                  # Node.js Backend (PM2)
└── Event-Horizon-AI/    # Python AI API (Docker)
```

## Deployment Methods

1. **Docker** (Recommended) - Isolated, reproducible, easy updates

---

# Method 1: Docker Deployment (Recommended)

## Quick Start

```bash
cd /home/vytrieu/EventHorizon
git clone https://github.com/EventHorizon6626/Event-Horizon-AI.git
cd Event-Horizon-AI
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys:
# - NEWS_API_KEY (get from https://newsapi.org/)
nano .env
```

### 3. Build and Start
```bash
docker compose up -d --build
```

### 4. Verify Service
```bash
docker ps
curl http://localhost:8030/health
```

## Continuous Deployment

The unified `deploy.sh` script supports both deployment methods:

```bash
# Usage: ./deploy.sh [docker|systemd] [--once]
chmod +x deploy.sh
```

### Option 1: One-time Deployment
```bash
# Docker deployment (single run)
./deploy.sh docker --once

# Systemd deployment (single run)
./deploy.sh systemd --once
```

### Option 2: Continuous Deployment Loop
```bash
# Docker - Run in background with nohup
nohup ./deploy.sh docker &

# Systemd - Run in background
nohup ./deploy.sh systemd &

# Or use screen/tmux
screen -S deploy-ai
./deploy.sh docker  # or systemd
# Ctrl+A, D to detach
```

### Option 3: Systemd Service (Recommended)
Create `/etc/systemd/system/evth-ai-deploy.service`:
```ini
[Unit]
Description=Event Horizon AI Deployment
After=network.target

[Service]
Type=simple
User=vytrieu
WorkingDirectory=/home/vytrieu/EventHorizon/Event-Horizon-AI
ExecStart=/home/vytrieu/EventHorizon/Event-Horizon-AI/deploy.sh docker
Restart=always
```

Enable and start:
```bash
sudo systemctl enable evth-ai-deploy
sudo systemctl start evth-ai-deploy
```

## API Endpoints

Once deployed, the API will be available at `http://localhost:8030`:

### Health Check
```bash
GET /health
```

### Analyze Portfolio
```bash
POST /api/v1/analyze-portfolio
Content-Type: application/json

{
  "portfolio": ["AAPL", "TSLA", "SPY", "NVDA"],
  "portfolio_id": "demo_2026"
}
```

### Get Supported Agents
```bash
GET /api/v1/supported-agents
```

## Integration with BE (Node.js)

In your Node.js backend (`/home/vytrieu/EventHorizon/BE`):

```javascript
// Example: Call AI API from Node.js BE
const axios = require('axios');

async function analyzePortfolio(symbols) {
  try {
    const response = await axios.post('http://localhost:8030/api/v1/analyze-portfolio', {
      portfolio: symbols,
      portfolio_id: `portfolio_${Date.now()}`
    });

    return response.data;
  } catch (error) {
    console.error('AI API error:', error.message);
    throw error;
  }
}

// Usage in your BE routes:
app.post('/api/portfolio/analyze', async (req, res) => {
  const { symbols } = req.body;
  const analysis = await analyzePortfolio(symbols);
  res.json(analysis);
});
```

## Monitoring

### Check Service Status
```bash
docker ps
docker logs -f event-horizon
```

### Test API
```bash
# Health check
curl http://localhost:8030/health

# Swagger docs
open http://localhost:8030/docs

# Full analysis
curl -X POST http://localhost:8030/api/v1/analyze-portfolio \
  -H "Content-Type: application/json" \
  -d '{"portfolio": ["AAPL", "TSLA"]}'
```

## Nginx Reverse Proxy (Optional)

If you want to expose the AI API externally:

```nginx
# /etc/nginx/sites-available/evth-ai
server {
    listen 80;
    server_name ai.yourdomain.com;

    location / {
        proxy_pass http://localhost:8030;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs event-horizon

# Test manually
./run_local.sh
```

### Port already in use
```bash
# Check what's using port 8030
sudo lsof -i :8030

# Restart container
docker compose restart
```
