# Quick Deploy - Option 2 Architecture

Deploy AI service with Backend proxy (Recommended setup)

---

## Quick Overview

```
Frontend → Backend API → AI Service (localhost only)
         (evth-api.hirodev.space)  (localhost:5000)
```

---

## Step 1: Deploy AI Service on VPS

### SSH to VPS

```bash
ssh root@178.18.255.19
```

### Clone & Deploy (First Time)

```bash
# Create directory
sudo mkdir -p /var/www/event-horizon-ai
sudo chown $USER:$USER /var/www/event-horizon-ai
cd /var/www/event-horizon-ai

# Clone repo
git clone YOUR_GITHUB_REPO_URL .

# Run deploy script
chmod +x deploy.sh
./deploy.sh
```

### Configure Environment

```bash
nano .env
```

Set these values:

```bash
NEWS_API_KEY=your_actual_newsapi_key_here
API_HOST=127.0.0.1    # localhost only - not exposed to internet
API_PORT=5000
LOG_LEVEL=INFO
```

### Restart Service

```bash
sudo systemctl restart event-horizon-ai
```

### Verify AI Service Running

```bash
# Should work (from VPS)
curl http://localhost:5000/health

# Should NOT work (from outside) - this is correct!
curl http://178.18.255.19:5000/health  # Connection refused
```

---

## Step 2: Add Proxy Routes to Backend

### In your Node.js backend repo:

```bash
cd /path/to/backend
npm install axios
```

### Create `routes/ai-proxy.js`

Copy the complete proxy code from `BACKEND_INTEGRATION.md` section "Create AI Proxy Module"

### Update `app.js` or `index.js`

```javascript
const aiProxyRoutes = require('./routes/ai-proxy');
app.use('/api/ai', aiProxyRoutes);
```

### Deploy to VPS & Restart

```bash
git add .
git commit -m "Add AI service proxy routes"
git push origin main

# On VPS
ssh root@178.18.255.19
cd /path/to/your/backend
git pull origin main
npm install
pm2 restart all
```

---

## Step 3: Update Frontend

### Remove AI_API_URL from `.env`

```bash
# Only keep this:
REACT_APP_BE_API_URL=https://evth-api.hirodev.space/api

# Remove this line:
# REACT_APP_AI_API_URL=http://178.18.255.19:5000
```

### Update API calls to use Backend proxy

```javascript
// Call backend proxy instead of AI service directly
fetch(`${REACT_APP_BE_API_URL}/ai/portfolio/analyze`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ stocks: ['AAPL', 'GOOGL'] })
})
```

---

## Step 4: Test End-to-End

### Test Backend → AI proxy

```bash
curl https://evth-api.hirodev.space/api/ai/health
```

Should return:
```json
{
  "backend": "healthy",
  "ai_service": {
    "status": "healthy",
    "service": "event-horizon-ai"
  }
}
```

### Test Portfolio Analysis

```bash
curl -X POST https://evth-api.hirodev.space/api/ai/portfolio/analyze \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "GOOGL"]}'
```

### Test from Frontend

Open your frontend (localhost:3021) and test portfolio analysis.

---

## Future Updates

### Update AI Service

```bash
# Local
git add .
git commit -m "Update AI service"
git push origin main

# VPS
ssh root@178.18.255.19
cd /var/www/event-horizon-ai
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart event-horizon-ai
```

### Update Backend Proxy

```bash
# Local
git add .
git commit -m "Update backend routes"
git push origin main

# VPS
ssh root@178.18.255.19
cd /path/to/backend
git pull origin main
npm install
pm2 restart all
```

---

## Security Checklist

- [x] AI service binds to `127.0.0.1` (not `0.0.0.0`)
- [x] Port 5000 NOT accessible from internet
- [x] Backend proxies all AI requests
- [x] Frontend only knows about Backend API
- [x] Firewall blocks external port 5000

---

## Monitoring

```bash
# AI Service
sudo systemctl status event-horizon-ai
sudo journalctl -u event-horizon-ai -f

# Backend
pm2 logs
pm2 monit
```

---

## Quick Commands Reference

```bash
# Restart AI service
sudo systemctl restart event-horizon-ai

# Restart Backend
pm2 restart all

# Check AI logs
sudo journalctl -u event-horizon-ai -n 50

# Test AI (from VPS)
curl http://localhost:5000/health

# Test Backend proxy (from anywhere)
curl https://evth-api.hirodev.space/api/ai/health
```

---

**That's it! Your architecture is deployed and secure.**

See `BACKEND_INTEGRATION.md` for detailed documentation.
