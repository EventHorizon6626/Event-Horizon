# Docker Deployment Guide - Option 2 Architecture

Deploy AI service using Docker with localhost-only binding.

---

## Quick Deploy

### 1. Configure Environment

```bash
cd ~/EventHorizon/Event-Horizon-AI

# Create .env file
cp .env.example .env
nano .env
```

Set your NewsAPI key:
```bash
NEWS_API_KEY=your_actual_newsapi_key_here
LOG_LEVEL=INFO
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
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-17T...",
  "service": "event-horizon-ai"
}
```

### 4. Test Security (Should Fail)

```bash
# From outside VPS - should NOT work
curl http://178.18.255.19:5000/health
# Connection refused - This is correct! ✅
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

# Check all containers
docker ps -a

# Check resource usage
docker stats event-horizon-ai
```

### Rebuild After Code Changes

```bash
# Pull latest code
cd ~/EventHorizon/Event-Horizon-AI
git pull origin main

# Rebuild and restart
docker-compose up -d --build
```

---

## Update Workflow

When you push code changes:

**Local machine:**
```bash
git add .
git commit -m "Update AI service"
git push origin main
```

**VPS:**
```bash
cd ~/EventHorizon/Event-Horizon-AI
git pull origin main
docker-compose up -d --build
```

---

## Architecture

```
Backend API (your Node.js app)
    ↓ HTTP
http://localhost:5000 ← Docker container (event-horizon-ai)
```

The Docker container:
- Binds to `127.0.0.1:5000` on host
- Only accessible from localhost
- NOT exposed to internet ✅

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs event-horizon-ai

# Check if port is in use
sudo lsof -i :5000

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
docker exec event-horizon-ai curl http://localhost:5000/health

# Check logs
docker logs --tail 50 event-horizon-ai
```

---

## Production Setup

### Auto-restart on Boot

Docker containers with `restart: unless-stopped` will automatically start on server reboot.

### Monitor with Portainer (Optional)

```bash
# Install Portainer
docker run -d -p 9443:9443 --name portainer \
  --restart=unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest

# Access at https://your-vps-ip:9443
```

---

## Cleanup

### Remove Everything

```bash
# Stop and remove containers
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker rmi event-horizon-ai

# Clean system
docker system prune -a
```

---

## Comparison: Docker vs Systemd

| Feature | Docker | Systemd |
|---------|--------|---------|
| Setup | Easier | More manual |
| Isolation | Full isolation | Shared system |
| Dependencies | Self-contained | Needs venv |
| Updates | Rebuild image | pip install |
| Logs | `docker logs` | `journalctl` |
| Portability | Highly portable | System-specific |
| Resource limits | Built-in | Manual config |

**Recommendation:** Use Docker for cleaner deployment ✅

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
curl http://localhost:5000/health
```

---

**Docker deployment is now live on localhost:5000** ✅
