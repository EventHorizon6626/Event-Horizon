# Docker Deployment Guide - Option 2 Architecture

Deploy AI service using Docker with localhost-only binding.

---

## Quick Deploy

### 1. Configure Environment

```bash
cd event_horizon/thinking-multi-agent

# Create .env file
cp .env.example .env
nano .env
```

Set your configuration:
```bash
LLM_BASE_URL=http://host.docker.internal:8000
LLM_MODEL=mistralai/Ministral-3-14B-Reasoning-2512
TAVILY_API_KEY=your_tavily_key
AGENTS_FILE=/data/agents.json
LOG_LEVEL=info
```

### 2. Build and Start

```bash
# Stop any running systemd service first (if applicable)
sudo systemctl stop event-horizon-ai 2>/dev/null || true

# Build and start with Docker
docker-compose up -d --build
```

### 3. Verify

```bash
# Check container status
docker ps | grep event-horizon

# Check logs
docker logs event-horizon-ai

# Test API (from VPS)
curl http://localhost:8030/health
```

Expected response:
```json
{
  "status": "healthy",
  "model": "mistralai/Ministral-3-14B-Reasoning-2512",
  "agents_count": 5,
  "llm_backend_status": "connected",
  "timestamp": "2026-02-10T..."
}
```

### 4. Test Security (Should Fail)

```bash
# From outside VPS - should NOT work
curl http://178.18.255.19:8030/health
# Connection refused - This is correct!
```

---

## Docker Commands

### Start/Stop/Restart

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Logs

```bash
# Follow logs
docker logs -f event-horizon-ai

# Last 100 lines
docker logs --tail 100 event-horizon-ai

# With timestamps
docker logs -f --timestamps event-horizon-ai
```

### Status

```bash
# Check running containers
docker ps

# Check resource usage
docker stats event-horizon-ai
```

### Rebuild After Code Changes

```bash
cd ~/EventHorizon/Event-Horizon
git pull origin main

# Rebuild and restart
docker-compose up -d --build
```

---

## Architecture

```
Backend API (your Node.js app)
    | HTTP
http://localhost:8030  <--  Docker container (event-horizon-ai)
```

The Docker container:
- Binds to `127.0.0.1:8030` on host
- Only accessible from localhost
- NOT exposed to internet

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs event-horizon-ai

# Check if port is in use
sudo lsof -i :8030

# Remove old container
docker-compose down
docker rm -f event-horizon-ai
```

### Port already in use

```bash
# Stop systemd service if running
sudo systemctl stop event-horizon-ai 2>/dev/null || true
sudo systemctl disable event-horizon-ai 2>/dev/null || true

# Then start Docker
docker-compose up -d
```

### Build fails

```bash
# Clean rebuild
docker-compose down
docker system prune -f
docker-compose up -d --build --force-recreate
```

### Can't connect to API

```bash
# Check container is running
docker ps | grep event-horizon

# Check health
docker exec event-horizon-ai curl http://localhost:8030/health

# Check logs
docker logs --tail 50 event-horizon-ai
```

---

## Quick Reference

```bash
# Start
docker-compose up -d

# Logs
docker logs -f event-horizon-ai

# Restart
docker-compose restart

# Stop
docker-compose down

# Update
git pull && docker-compose up -d --build

# Test
curl http://localhost:8030/health
```

---

**Docker deployment is now live on localhost:8030**
