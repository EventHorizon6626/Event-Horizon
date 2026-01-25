## Services Layer

The services layer contains client interfaces for external data sources.
Each service is responsible for API communication and data fetching.

### Structure

```
services/
├── news/                 # News data providers
│   └── news_api_client.py
├── financial/            # Financial data providers
│   └── financial_data_client.py
├── charts/              # Chart/OHLCV data providers
│   ├── chart_data_client.py (Yahoo Finance)
│   └── massive_chart_client.py (Massive.com)
└── __init__.py
```

### Services vs Agents

**Services**: External API clients
- Handle HTTP requests and responses
- Manage API authentication
- Rate limiting and error handling
- Return raw API data

**Agents**: Business logic and orchestration
- Use services to fetch data
- Transform and validate data
- Implement retry logic
- Return structured output

### Adding a New Service

1. Create service in appropriate subdirectory
2. Implement client interface
3. Add authentication and error handling
4. Create corresponding agent in `layer_1/agents/`
