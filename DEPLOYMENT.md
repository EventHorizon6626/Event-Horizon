# Event Horizon AI - Deployment Guide

## Server Architecture

```
/home/vytrieu/EventHorizon/
├── FE/                  # React Frontend (nginx)
├── BE/                  # Node.js Backend (PM2)
└── Event-Horizon-AI/    # Python AI API (systemd)
```

## Initial Setup on Server

### 1. Clone Repository
```bash
cd /home/vytrieu/EventHorizon
git clone https://github.com/EventHorizon6626/Event-Horizon-AI.git
cd Event-Horizon-AI
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys:
# - NEWS_API_KEY (get from https://newsapi.org/)
nano .env
```

### 4. Install Systemd Service
```bash
sudo cp evth-ai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable evth-ai
sudo systemctl start evth-ai
```

### 5. Verify Service
```bash
sudo systemctl status evth-ai
curl http://localhost:8001/health
```

## Continuous Deployment

### Option 1: Manual Deployment Script
```bash
# Make script executable
chmod +x deploy_ai.sh

# Run in background with nohup
nohup ./deploy_ai.sh &

# Or use screen/tmux
screen -S deploy-ai
./deploy_ai.sh
# Ctrl+A, D to detach
```

### Option 2: Systemd Timer (Recommended)
Create `/etc/systemd/system/evth-ai-deploy.service`:
```ini
[Unit]
Description=Event Horizon AI Deployment
After=network.target

[Service]
Type=simple
User=vytrieu
WorkingDirectory=/home/vytrieu/EventHorizon
ExecStart=/home/vytrieu/EventHorizon/Event-Horizon-AI/deploy_ai.sh
Restart=always
```

Enable and start:
```bash
sudo systemctl enable evth-ai-deploy
sudo systemctl start evth-ai-deploy
```

## API Endpoints

Once deployed, the API will be available at `http://localhost:8001`:

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
    const response = await axios.post('http://localhost:8001/api/v1/analyze-portfolio', {
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
sudo systemctl status evth-ai
```

### View Logs
```bash
# Service logs
sudo journalctl -u evth-ai -f

# Deployment logs
tail -f /home/vytrieu/EventHorizon/.deploy_logs/deploy_ai_loop.log
```

### Test API
```bash
# Health check
curl http://localhost:8001/health

# Full analysis
curl -X POST http://localhost:8001/api/v1/analyze-portfolio \
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
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u evth-ai -n 50

# Test manually
cd /home/vytrieu/EventHorizon/Event-Horizon-AI
source venv/bin/activate
python api_server.py
```

### Python dependencies issue
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Port already in use
```bash
# Check what's using port 8001
sudo lsof -i :8001

# Change port in evth-ai.service if needed
sudo nano /etc/systemd/system/evth-ai.service
sudo systemctl daemon-reload
sudo systemctl restart evth-ai
```
