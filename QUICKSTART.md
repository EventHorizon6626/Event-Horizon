# Event Horizon AI - Quick Deployment Guide

## 🚀 Deploy on Your Server (5 minutes)

### Step 1: Push to GitHub
```bash
# On your local machine
git push origin main
```

### Step 2: Deploy on Server

SSH into your server:
```bash
ssh vytrieu@vmi1816419.contaboserver.net
cd /home/vytrieu/EventHorizon
```

### Step 3: Clone Repository (First Time Only)
```bash
git clone https://github.com/EventHorizon6626/Event-Horizon-AI.git
cd Event-Horizon-AI
```

Or if already cloned:
```bash
cd Event-Horizon-AI
git pull origin main
```

### Step 4: Configure Environment
```bash
cp .env.example .env
nano .env
```

Add (NEWS_API_KEY is optional):
```
NEWS_API_KEY=your_key_here_or_leave_empty
```
Save and exit (Ctrl+X, Y, Enter)

### Step 5: Start Docker Container
```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### Step 6: Test API
```bash
# Health check
curl http://localhost:8030/health

# Full test
curl -X POST http://localhost:8030/api/v1/analyze-portfolio \
  -H "Content-Type: application/json" \
  -d '{"portfolio": ["AAPL", "TSLA"]}'
```

✅ **Done!** AI API is running on `http://localhost:8030`

---

## 🔄 Continuous Deployment (Auto-Update)

Like your FE and BE, run a deployment loop:

```bash
# Make executable
chmod +x deploy_docker.sh

# Run in screen (recommended)
screen -S deploy-ai
./deploy_docker.sh
# Press Ctrl+A, then D to detach

# Check it's running
screen -ls
```

Now AI will auto-update every 2 minutes when you push to GitHub!

---

## 📊 Server Architecture

```
/home/vytrieu/EventHorizon/
├── FE/                     # React app → nginx
├── BE/                     # Node.js → PM2
└── Event-Horizon-AI/       # Python AI → Docker:8030
```

**Communication Flow:**
```
FE → BE → AI (localhost:8030) → Stage 1 Analysis → Response
```

---

## 🔗 Connect BE to AI

In your Node.js backend (`/home/vytrieu/EventHorizon/BE`):

```javascript
// Add this to your routes
const axios = require('axios');

app.post('/api/portfolio/analyze', async (req, res) => {
  try {
    const { symbols } = req.body;

    // Call AI service
    const response = await axios.post('http://localhost:8030/api/v1/analyze-portfolio', {
      portfolio: symbols,
      portfolio_id: `portfolio_${Date.now()}`
    });

    res.json(response.data);
  } catch (error) {
    console.error('AI API Error:', error.message);
    res.status(500).json({ error: error.message });
  }
});
```

---

## 🛠️ Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Check status
docker ps | grep event-horizon

# Enter container
docker compose exec event-horizon bash

# Check container logs
docker compose logs -f
```

---

## 🐛 Troubleshooting

### Container won't start
```bash
docker-compose logs
```

### Port already in use
```bash
sudo lsof -i :8030
# Kill the process or change port in docker-compose.yml
```

### API not responding
```bash
# Check container health
docker ps
docker inspect event-horizon

# Restart
docker-compose restart
```

### Update not working
```bash
cd /home/vytrieu/EventHorizon/Event-Horizon-AI
git pull origin main
docker-compose build --no-cache
docker-compose up -d
```

---

## 📈 Monitoring

```bash
# Real-time logs
docker compose logs -f event-horizon

# Resource usage
docker stats event-horizon
```

---

## 🎯 What You Get

✅ **5 Data Agents** running in parallel:
- Candlestick (OHLCV price data)
- Earnings (Financial reports)
- News (Articles & headlines)
- Technical (SMA, RSI, MACD)
- Fundamentals (P/E, ROE, ratios)

✅ **REST API** on port 8030
✅ **Auto-deployment** every 2 minutes
✅ **Docker isolation** (no dependency conflicts)
✅ **Health checks** and auto-restart
✅ **Production-ready** logging and monitoring

---

## 🚦 Next Steps

1. ✅ Push code: `git push origin main`
2. ✅ Deploy on server (5 min)
3. ✅ Start continuous deployment
4. 🔧 Connect your BE to AI API
5. 🎨 Update FE to call BE portfolio endpoint
6. 🎉 Test full stack!
