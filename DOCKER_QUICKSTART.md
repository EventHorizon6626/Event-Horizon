# Docker Quick Start

Run Event Horizon in Docker locally in under 5 minutes.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- Docker Compose (included with Docker Desktop)

---

## Quick Start

### Option 1: Docker Run (Simplest)

```bash
# Build image
docker build -t event-horizon:latest .

# Run once
docker run --rm \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v $(pwd)/results:/app/results \
  event-horizon:latest
```

Results saved to `./results/`

### Option 2: Docker Compose (Recommended)

**Development:**
```bash
docker-compose -f docker-compose.dev.yml up
```

**Production:**
```bash
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.prod.yml down
```

---

## Configuration

### API Keys

Create `.env` file:
```bash
NEWS_API_KEY=your_key_here
```

Or pass as environment variable:
```bash
docker run -e NEWS_API_KEY=your_key event-horizon:latest
```

### Enable/Disable Agents

Edit `config.yaml`:
```yaml
agents:
  news_agent:
    enabled: false
  report_agent:
    enabled: true
```

---

## Common Commands

### Build

```bash
docker build -t event-horizon:latest .

# Build without cache
docker build --no-cache -t event-horizon:latest .
```

### Run

```bash
# Run once and remove container
docker run --rm event-horizon:latest

# Run with mounted volumes
docker run --rm \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/results:/app/results \
  event-horizon:latest

# Run interactively
docker run -it --rm event-horizon:latest /bin/bash
```

### Logs

```bash
# Docker Compose
docker-compose logs -f

# Docker run
docker logs -f <container-id>
```

---

## Docker Compose Files

| File | Purpose | Usage |
|------|---------|-------|
| `docker-compose.yml` | Default configuration | `docker-compose up` |
| `docker-compose.dev.yml` | Development (hot reload) | `docker-compose -f docker-compose.dev.yml up` |
| `docker-compose.prod.yml` | Production (optimized) | `docker-compose -f docker-compose.prod.yml up -d` |
| `docker-compose.standalone.yml` | Backend API only | `docker-compose -f docker-compose.standalone.yml up -d` |

---

## Volumes

Mount these for persistence:

```yaml
volumes:
  - ./config.yaml:/app/config.yaml:ro    # Configuration
  - ./.env:/app/.env:ro                  # Environment variables
  - ./results:/app/results               # Output files
  - ./logs:/app/logs                     # Log files
  - ./data:/app/data                     # Data storage
```

---

## Troubleshooting

### Build fails

```bash
# Clear cache and rebuild
docker build --no-cache -t event-horizon:latest .

# Check Dockerfile syntax
docker build -t event-horizon:latest . --progress=plain
```

### Container exits immediately

```bash
# Check logs
docker logs <container-id>

# Run interactively to debug
docker run -it event-horizon:latest /bin/bash
```

### Config not found

```bash
# Verify file exists
ls config.yaml

# Check mount path
docker run --rm -v $(pwd)/config.yaml:/app/config.yaml:ro event-horizon:latest ls -la /app/
```

### Results not saved

```bash
# Ensure results directory exists
mkdir -p results

# Mount correctly
docker run --rm -v $(pwd)/results:/app/results event-horizon:latest
```

---

## Production Deployment

For production deployment to cloud platforms (AWS, GCP, Azure, Kubernetes, etc.), see **[DEPLOYMENT.md](DEPLOYMENT.md)**

---

## Scheduled Execution

### Using cron (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Run daily at 9 AM
0 9 * * * cd /path/to/Event-Horizon-AI && docker-compose -f docker-compose.prod.yml up >> logs/cron.log 2>&1
```

### Using systemd timer (Linux)

Create `/etc/systemd/system/event-horizon.service`:
```ini
[Unit]
Description=Event Horizon Agent System

[Service]
Type=oneshot
WorkingDirectory=/path/to/Event-Horizon-AI
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/event-horizon.timer`:
```ini
[Unit]
Description=Event Horizon Daily Timer

[Timer]
OnCalendar=daily
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl enable event-horizon.timer
sudo systemctl start event-horizon.timer
```

---

## Health Checks

The containers include health checks:

```bash
# Check health status
docker ps

# Manual health check
docker exec <container-id> python -c "import sys; sys.exit(0)"
```

---

## Resource Limits

Configure in docker-compose files:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

---

## Next Steps

- **Local development**: Use `docker-compose.dev.yml`
- **Production deployment**: See `DEPLOYMENT.md` for cloud platforms
- **Configuration**: See `CONFIG_README.md` for agent configuration
- **API server**: Use `docker-compose.standalone.yml` for backend API

---

## Quick Reference

```bash
# Build
docker build -t event-horizon:latest .

# Run (development)
docker-compose -f docker-compose.dev.yml up

# Run (production)
docker-compose -f docker-compose.prod.yml up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down

# Clean up
docker system prune -a
```
