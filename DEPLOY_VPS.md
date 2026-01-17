# Deploy Event Horizon AI to VPS - Manual Guide

Deploy the AI service (FastAPI + Agents) to your VPS at **178.18.255.19:5000**

---

## Architecture

```
┌─────────────────────┐
│  Frontend (Local)   │
│  localhost:3021     │
└──────────┬──────────┘
           │
           ├─────────────────────────────────┐
           │                                 │
           ▼                                 ▼
┌──────────────────────┐      ┌───────────────────────────┐
│   Backend API (VPS)  │      │    AI Service (VPS)       │
│ evth-api.hirodev.space│     │   178.18.255.19:5000     │
│   (Node.js/PM2)      │      │   (Python/FastAPI)        │
└──────────────────────┘      └───────────────────────────┘
                               │
                               ├─ NewsAgent
                               ├─ ReportAgent
                               └─ Future agents
```

---

## Prerequisites on VPS

1. Ubuntu/Debian server
2. Python 3.8+
3. Git installed
4. Port 5000 open in firewall

---

## Deployment Steps

### 1. First Time Setup on VPS

SSH into your VPS:

```bash
ssh root@178.18.255.19
# or
ssh your_user@178.18.255.19
```

Create application directory:

```bash
sudo mkdir -p /var/www/event-horizon-ai
sudo chown $USER:$USER /var/www/event-horizon-ai
cd /var/www/event-horizon-ai
```

Clone your repository:

```bash
git clone https://github.com/YOUR_USERNAME/Event-Horizon-AI.git .
# Or use the git URL of your repository
```

---

### 2. Deploy Using Script (Recommended)

Make deploy script executable:

```bash
chmod +x deploy.sh
```

Run deployment:

```bash
./deploy.sh
```

The script will:
- Install Python dependencies
- Set up virtual environment
- Create systemd service
- Start the AI service on port 5000

---

### 3. Manual Deployment (Alternative)

If you prefer manual deployment:

#### Step A: Install Dependencies

```bash
cd /var/www/event-horizon-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step B: Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

Set your NewsAPI key in `.env`:
```bash
NEWS_API_KEY=your_actual_newsapi_key_here
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=5000
```

#### Step C: Test Locally First

```bash
# Activate venv if not already
source venv/bin/activate

# Run server
python api_server.py
```

Test in another terminal:
```bash
curl http://localhost:5000/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-17T...",
  "service": "event-horizon-ai"
}
```

Press `Ctrl+C` to stop.

#### Step D: Create Systemd Service

Create service file:

```bash
sudo nano /etc/systemd/system/event-horizon-ai.service
```

Add this content:

```ini
[Unit]
Description=Event Horizon AI Service
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/var/www/event-horizon-ai
Environment="PATH=/var/www/event-horizon-ai/venv/bin"
ExecStart=/var/www/event-horizon-ai/venv/bin/python api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Replace `YOUR_USERNAME` with your actual user.

#### Step E: Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable event-horizon-ai

# Start service
sudo systemctl start event-horizon-ai

# Check status
sudo systemctl status event-horizon-ai
```

---

### 4. Configure Firewall

Open port 5000:

```bash
# UFW (Ubuntu)
sudo ufw allow 5000/tcp
sudo ufw status

# Or iptables
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

---

### 5. Test from Your Local Machine

From your local computer, test the API:

```bash
curl http://178.18.255.19:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-17T...",
  "service": "event-horizon-ai"
}
```

Test portfolio analysis:

```bash
curl -X POST http://178.18.255.19:5000/api/portfolio/analyze \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "GOOGL"]}'
```

---

### 6. Update Frontend Configuration

Your frontend `.env` is already configured:

```bash
REACT_APP_AI_API_URL=http://178.18.255.19:5000
```

This should work once the AI service is deployed!

---

## Updating After Code Changes

When you push new code to GitHub:

### On Your Local Machine:

```bash
git add .
git commit -m "Update AI service"
git push origin main
```

### On VPS:

```bash
ssh your_user@178.18.255.19

cd /var/www/event-horizon-ai

# Pull latest code
git pull origin main

# Activate venv and update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart event-horizon-ai

# Check status
sudo systemctl status event-horizon-ai
```

**Or use the deploy script:**

```bash
./deploy.sh
```

---

## Service Management Commands

```bash
# Start service
sudo systemctl start event-horizon-ai

# Stop service
sudo systemctl stop event-horizon-ai

# Restart service
sudo systemctl restart event-horizon-ai

# Check status
sudo systemctl status event-horizon-ai

# View logs (real-time)
sudo journalctl -u event-horizon-ai -f

# View recent logs
sudo journalctl -u event-horizon-ai -n 100
```

---

## API Endpoints

Once deployed, these endpoints will be available:

- `GET http://178.18.255.19:5000/` - Service info
- `GET http://178.18.255.19:5000/health` - Health check
- `POST http://178.18.255.19:5000/api/portfolio/analyze` - Full analysis
- `POST http://178.18.255.19:5000/api/news` - News only
- `POST http://178.18.255.19:5000/api/reports` - Reports only
- `GET http://178.18.255.19:5000/docs` - API documentation (Swagger)

---

## Testing from Frontend

Your frontend will call the AI API like this:

```javascript
// In your React app
const analyzePortfolio = async (stocks) => {
  const response = await fetch(
    `${process.env.REACT_APP_AI_API_URL}/api/portfolio/analyze`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stocks })
    }
  );

  return await response.json();
};

// Usage
const result = await analyzePortfolio(['AAPL', 'GOOGL', 'TSLA']);
console.log(result);
```

---

## Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u event-horizon-ai -n 50

# Check if port is in use
sudo lsof -i :5000

# Check Python version
python3 --version  # Should be 3.8+
```

### Port 5000 blocked

```bash
# Test locally first
curl http://localhost:5000/health

# If local works but external doesn't, check firewall
sudo ufw status
sudo ufw allow 5000/tcp
```

### Dependencies issues

```bash
cd /var/www/event-horizon-ai
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### CORS errors from frontend

Check CORS configuration in `api_server.py:36-48`. Your frontend URL should be allowed.

---

## Production Recommendations (Optional)

### 1. Use Nginx as Reverse Proxy

```nginx
server {
    listen 80;
    server_name ai.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Use HTTPS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d ai.yourdomain.com
```

### 3. Use PM2 (Alternative to systemd)

```bash
npm install -g pm2

# Start
pm2 start api_server.py --name event-horizon-ai --interpreter python3

# Save
pm2 save
pm2 startup
```

### 4. Monitor with PM2

```bash
pm2 status
pm2 logs event-horizon-ai
pm2 monit
```

---

## Quick Reference

```bash
# Deployment workflow
git push origin main                    # Push from local
ssh user@178.18.255.19                  # SSH to VPS
cd /var/www/event-horizon-ai            # Go to app dir
git pull origin main                    # Pull latest
source venv/bin/activate                # Activate venv
pip install -r requirements.txt         # Update deps
sudo systemctl restart event-horizon-ai # Restart
sudo journalctl -u event-horizon-ai -f  # Check logs
```

---

## Success Checklist

- [ ] VPS accessible via SSH
- [ ] Python 3.8+ installed
- [ ] Repository cloned to `/var/www/event-horizon-ai`
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured with NewsAPI key
- [ ] Systemd service created and enabled
- [ ] Service running and healthy
- [ ] Port 5000 accessible from outside
- [ ] Health endpoint returns 200 OK
- [ ] Frontend can connect to AI API

---

**Ready to deploy? Start with Step 1!**
