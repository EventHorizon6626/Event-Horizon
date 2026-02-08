# Development Setup Guide

This guide explains how to run Event Horizon AI in **local development** vs **server deployment**.

---

## 🏠 Local Development (Recommended for Testing)

Run the API server directly on your machine without Docker.

### Setup

1. **Configure environment**
   ```bash
   # Your .env file is already configured for local dev
   # Make sure GOOGLE_API_KEY is set correctly
   cat .env
   ```

2. **Run the local dev server**
   ```bash
   ./run_local.sh
   ```

   Or manually:
   ```bash
   # Activate venv
   source venv/bin/activate

   # Install dependencies
   pip install -r event_horizon/thinking-multi-agent/app/requirements.txt

   # Run server
   SKIP_VLLM=true PYTHONPATH="$(pwd)" uvicorn main:app --host 0.0.0.0 --port 8030 --app-dir event_horizon/thinking-multi-agent/app
   ```

3. **Test the API**
   ```bash
   # Health check
   curl http://localhost:8030/health

   # Swagger docs
   open http://localhost:8030/docs
   ```

### Advantages
- ✅ Faster iteration (no Docker rebuild)
- ✅ Easy debugging with IDE
- ✅ Hot reload with uvicorn
- ✅ Direct access to logs

---

## 🚀 Server Deployment (Docker)

Run the API in a Docker container for production-like environment.

### Setup

1. **Configure production environment**
   ```bash
   # Edit .env.production with your API keys
   vim .env.production
   ```

2. **Build and run with Docker**
   ```bash
   docker compose up -d --build
   ```

3. **Check logs**
   ```bash
   docker logs -f event-horizon
   ```

4. **Test the API**
   ```bash
   curl http://localhost:8030/health
   ```

### Advantages
- ✅ Isolated environment
- ✅ Production-like setup
- ✅ Easy deployment to servers
- ✅ Auto-restart on failure

---

## 📁 Environment Files

| File | Purpose | Used By |
|------|---------|---------|
| `.env` | Local development configuration | Local dev (run_local.sh) and Docker Compose |
| `.env.example` | Template with all options | Documentation |

---

## 🔧 Switching Between Modes

### Local → Docker
```bash
# Stop local server (CTRL+C if running)
# Start Docker
docker compose up -d --build
```

### Docker → Local
```bash
# Stop Docker
docker compose down
# Start local server
./run_local.sh
```

---

## ⚠️ Important Notes

1. **API Keys**: Configure in `.env` (used by both local dev and Docker)

2. **Model Configuration**: Set `LLM_MODEL` in `.env` (default: `mistralai/Ministral-3-14B-Reasoning-2512`)

3. **Ports**:
   - Local dev: `0.0.0.0:8030`
   - Docker: `0.0.0.0:8030`

4. **Hot Reload**:
   - Local: Enabled by default (uvicorn reload)
   - Docker: Requires rebuild to apply code changes

---

## 🐛 Troubleshooting

### "Failed to connect to localhost:8030"
- Check if server is running: `ps aux | grep uvicorn` (local) or `docker ps` (Docker)
- Check logs: `docker logs event-horizon` (Docker)

### "404 NOT_FOUND - models/gemini-xxx is not found"
- Update model name in `.env` or `.env.production` to: `gemini-2.0-flash`
- Available models: `gemini-2.0-flash`, `gemini-2.5-flash`, `gemini-2.5-pro`

### "GOOGLE_API_KEY not configured"
- Make sure API key is set in `.env` (local) or `.env.production` (Docker)
- Restart server/container after changing env files

---

## 🎯 Quick Reference

```bash
# LOCAL DEVELOPMENT
./run_local.sh                    # Start local dev server
source venv/bin/activate          # Activate virtual environment
deactivate                        # Deactivate virtual environment

# DOCKER DEPLOYMENT
docker compose up -d              # Start containers
docker compose down               # Stop containers
docker compose up -d --build      # Rebuild and start
docker logs -f event-horizon      # View logs
docker ps                         # List containers

# TESTING
curl http://localhost:8030/health                           # Health check
curl http://localhost:8030/agents                           # List agents
open http://localhost:8030/docs                             # Swagger UI
```
