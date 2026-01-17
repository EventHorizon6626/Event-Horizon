# Quick Deploy - Docker (Localhost Only)

Fast deployment guide for AI service using Docker.

---

## One-Command Deploy

```bash
cd ~/EventHorizon/Event-Horizon-AI
cp .env.example .env
nano .env  # Add your NEWS_API_KEY
docker-compose up -d --build
```

---

## Step-by-Step

### 1. Configure

```bash
cd ~/EventHorizon/Event-Horizon-AI
cp .env.example .env
nano .env
```

Set:
```bash
NEWS_API_KEY=your_actual_key_here
LOG_LEVEL=INFO
```

### 2. Deploy

```bash
docker-compose up -d --build
```

### 3. Verify

```bash
# Check status
docker ps | grep event-horizon

# Test API
curl http://localhost:5000/health
```

Expected:
```json
{"status": "healthy", "service": "event-horizon-ai"}
```

---

## Update After Code Changes

```bash
cd ~/EventHorizon/Event-Horizon-AI
git pull origin main
docker-compose up -d --build
```

---

## Useful Commands

```bash
# Logs
docker logs -f event-horizon-ai

# Restart
docker-compose restart

# Stop
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Architecture

```
Backend API → http://localhost:5000 → AI Service (Docker)
```

AI service is localhost-only, NOT exposed to internet ✅

---

For detailed docs, see:
- **DOCKER_DEPLOY.md** - Full Docker deployment guide
- **BACKEND_INTEGRATION.md** - Node.js backend proxy setup
- **ARCHITECTURE.md** - System architecture
