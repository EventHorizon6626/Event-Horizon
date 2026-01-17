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

📖 **See:** [Quick Start Guide](docs/guides/quick-start.md) for detailed instructions.

---

## Architecture

```
Frontend → Backend API → AI Service (localhost:5000)
                         ├─ NewsAgent
                         ├─ ReportAgent
                         └─ Future agents
```

**Option 2 Architecture:** Backend proxies requests to AI service (localhost-only, secure)

📖 **See:** [System Architecture](docs/architecture/system-architecture.md) for full details.

---

## Documentation

### 🚀 Getting Started
- **[Quick Start](docs/guides/quick-start.md)** - Fast deployment guide
- **[Docker Deployment](docs/guides/docker-deploy.md)** - Complete Docker guide
- **[Configuration](docs/guides/configuration.md)** - Environment setup

### 🏗️ Architecture
- **[System Architecture](docs/architecture/system-architecture.md)** - Complete system design
- **[Backend Integration](docs/architecture/backend-integration.md)** - Node.js proxy setup
- **[Multi-Agent Design](docs/architecture/multi-agent-design.md)** - Agent patterns

### 🤖 Agents
- **[News Agent](docs/agents/news-agent.md)** - NewsAgent design & implementation
- **[Report Agent](docs/agents/report-agent.md)** - ReportAgent design & implementation

### 📚 Guides
- **[Usage Guide](docs/guides/usage.md)** - How to use the API
- **[Data Sources](docs/guides/data-sources.md)** - Understanding data sources
- **[Advanced Configuration](docs/guides/configuration-advanced.md)** - Advanced settings

### 📖 References
- **[Architecture Overview](docs/references/architecture-overview.md)** - High-level overview
- **[Design Patterns](docs/references/20-agentic-design-patterns.md)** - Agentic patterns

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
├── docs/                          # Documentation
│   ├── guides/                    # User guides
│   ├── architecture/              # Architecture docs
│   ├── agents/                    # Agent-specific docs
│   └── references/                # Reference materials
├── api_server.py                  # FastAPI server
├── docker-compose.yml             # Docker deployment
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
- [Deployment Issues](docs/guides/docker-deploy.md#troubleshooting)
- [Architecture Questions](docs/architecture/system-architecture.md)
- [Configuration Help](docs/guides/configuration.md)

---

**Ready to deploy?** → [Quick Start Guide](docs/guides/quick-start.md)
