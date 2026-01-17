# Event Horizon AI

AI-powered portfolio analysis service with multi-agent architecture.

---

## Quick Deploy

```bash
# Configure
cp .env.example .env
nano .env  # Set NEWS_API_KEY

# Deploy with Docker
docker-compose up -d --build

# Test
curl http://localhost:5000/health
```

**See:** [QUICK_DEPLOY.md](Event-Horizon%20AI%20md/QUICK_DEPLOY.md) for detailed instructions.

---

## Architecture

```
Frontend → Backend API → AI Service (localhost:5000)
                         ├─ NewsAgent
                         ├─ ReportAgent
                         └─ Future agents
```

**Option 2 Architecture:** Backend proxies requests to AI service (localhost-only, secure)

**See:** [ARCHITECTURE.md](Event-Horizon%20AI%20md/ARCHITECTURE.md) for full architecture details.

---

## Documentation

### Deployment
- **[QUICK_DEPLOY.md](Event-Horizon%20AI%20md/QUICK_DEPLOY.md)** - Fast deployment guide
- **[DOCKER_DEPLOY.md](Event-Horizon%20AI%20md/DOCKER_DEPLOY.md)** - Complete Docker deployment guide
- **[BACKEND_INTEGRATION.md](Event-Horizon%20AI%20md/BACKEND_INTEGRATION.md)** - Node.js backend proxy setup

### Getting Started
- **[QUICKSTART.md](Event-Horizon%20AI%20md/QUICKSTART.md)** - General quickstart guide
- **[CONFIG_README.md](Event-Horizon%20AI%20md/CONFIG_README.md)** - Configuration guide

### Architecture & Design
- **[ARCHITECTURE.md](Event-Horizon%20AI%20md/ARCHITECTURE.md)** - System architecture
- **[docs/multi-agent-architecture.md](docs/multi-agent-architecture.md)** - Multi-agent design patterns
- **[docs/news-agent-design.md](docs/news-agent-design.md)** - NewsAgent design
- **[docs/report-agent-design.md](docs/report-agent-design.md)** - ReportAgent design

---

## Features

### Current Agents
- **NewsAgent** - Fetches financial news from NewsAPI.org
- **ReportAgent** - Fetches financial reports and metrics from Yahoo Finance

### API Endpoints
- `GET /health` - Health check
- `POST /api/portfolio/analyze` - Full portfolio analysis (news + reports)
- `POST /api/news` - Get news articles only
- `POST /api/reports` - Get financial reports only
- `GET /docs` - API documentation (Swagger)

---

## Tech Stack

- **Backend:** Python 3.11 + FastAPI
- **Agents:** Custom multi-agent architecture
- **Data Sources:** NewsAPI.org, Yahoo Finance (yfinance)
- **Deployment:** Docker
- **Process Management:** Docker Compose

---

## Project Structure

```
Event-Horizon-AI/
├── agents/                        # AI agents
│   ├── news_agent.py
│   ├── report_agent.py
│   └── base_agent.py
├── services/                      # External services
│   ├── news_api_client.py
│   └── yahoo_finance_client.py
├── api_server.py                  # FastAPI server
├── docker-compose.yml             # Docker deployment
├── Event-Horizon AI md/           # Documentation
├── docs/                          # Agent design docs
└── README.md                      # This file
```

---

## Environment Variables

Required in `.env`:

```bash
NEWS_API_KEY=your_newsapi_key_here    # Get from newsapi.org
LOG_LEVEL=INFO
API_HOST=0.0.0.0                      # Inside Docker
API_PORT=5000
```

---

## Usage Examples

### Full Portfolio Analysis

```bash
curl -X POST http://localhost:5000/api/portfolio/analyze \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "GOOGL", "TSLA"]}'
```

### News Only

```bash
curl -X POST http://localhost:5000/api/news \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "TSLA"]}'
```

### Reports Only

```bash
curl -X POST http://localhost:5000/api/reports \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "TSLA"]}'
```

---

## Docker Commands

```bash
# Start
docker-compose up -d

# Logs
docker logs -f event-horizon-ai

# Restart
docker-compose restart

# Stop
docker-compose down

# Update after code changes
git pull && docker-compose up -d --build
```

---

## Development

### Local Setup (without Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Run server
python api_server.py
```

---

## Roadmap

### Planned Agents
- [ ] Sentiment Analysis Agent (FinBERT)
- [ ] Technical Analysis Agent (Chart patterns)
- [ ] Risk Assessment Agent (Portfolio risk)
- [ ] Social Media Agent (Twitter/Reddit)

### Infrastructure
- [ ] Redis caching
- [ ] PostgreSQL persistence
- [ ] Celery background tasks
- [ ] WebSocket real-time updates

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-agent`)
3. Commit changes (`git commit -m 'Add new agent'`)
4. Push to branch (`git push origin feature/new-agent`)
5. Open Pull Request

---

## License

Proprietary - Event Horizon Project

---

## Support

For issues or questions, check the documentation:
- [Deployment Issues](Event-Horizon%20AI%20md/DOCKER_DEPLOY.md#troubleshooting)
- [Architecture Questions](Event-Horizon%20AI%20md/ARCHITECTURE.md)
- [Configuration Help](Event-Horizon%20AI%20md/CONFIG_README.md)

---

**Ready to deploy?** → [QUICK_DEPLOY.md](Event-Horizon%20AI%20md/QUICK_DEPLOY.md)
