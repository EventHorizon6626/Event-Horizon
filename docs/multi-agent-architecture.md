# Event Horizon - Multi-Agent Scalable Architecture

Guide for scaling Event Horizon to support many AI agents with orchestration.

---

## Table of Contents

1. [Current Architecture](#current-architecture)
2. [Future Architecture (Multi-Agent)](#future-architecture-multi-agent)
3. [Adding New Agents](#adding-new-agents)
4. [Agent Orchestration](#agent-orchestration)
5. [Communication Patterns](#communication-patterns)
6. [Deployment Strategies](#deployment-strategies)
7. [Monitoring & Observability](#monitoring--observability)

---

## Current Architecture

### Single Container, Multiple Agents

```
┌──────────────────────────────────────┐
│         Docker Container             │
│                                      │
│  ┌────────────────────────────────┐ │
│  │          main.py               │ │
│  │                                │ │
│  │  ┌──────────────────────────┐ │ │
│  │  │   config.yaml loader     │ │ │
│  │  └──────────────────────────┘ │ │
│  │                                │ │
│  │  if news_agent enabled:       │ │
│  │    ┌─────────────────┐        │ │
│  │    │  News Agent     │        │ │
│  │    │  - execute()    │        │ │
│  │    └─────────────────┘        │ │
│  │                                │ │
│  │  if report_agent enabled:     │ │
│  │    ┌─────────────────┐        │ │
│  │    │  Report Agent   │        │ │
│  │    │  - execute()    │        │ │
│  │    └─────────────────┘        │ │
│  │                                │ │
│  │  Save results to JSON         │ │
│  └────────────────────────────────┘ │
│                                      │
└──────────────────────────────────────┘
```

**Characteristics**:
- ✅ Simple, easy to deploy
- ✅ Low overhead
- ✅ Good for 2-5 agents
- ❌ Not scalable to 10+ agents
- ❌ All agents run sequentially
- ❌ No parallel processing
- ❌ Single point of failure

---

## Future Architecture (Multi-Agent)

### Microservices Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                           │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              API Gateway / Orchestrator                   │ │
│  │  - Receives portfolio requests                            │ │
│  │  - Dispatches work to agents                              │ │
│  │  - Aggregates results                                     │ │
│  │  - Handles errors and retries                             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                            │                                    │
│          ┌─────────────────┴──────────────────┐                │
│          ▼                 ▼                   ▼                │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐        │
│  │  News Agent   │ │ Report Agent  │ │ Sentiment     │        │
│  │  (Pod)        │ │  (Pod)        │ │  Agent (Pod)  │        │
│  │               │ │               │ │               │        │
│  │  - REST API   │ │  - REST API   │ │  - REST API   │        │
│  │  - Health chk │ │  - Health chk │ │  - Health chk │        │
│  └───────────────┘ └───────────────┘ └───────────────┘        │
│                                                                 │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐        │
│  │ Technical     │ │ Balance Sheet │ │  Risk         │        │
│  │ Analysis      │ │  Agent        │ │  Analysis     │        │
│  │  (Pod)        │ │  (Pod)        │ │  Agent (Pod)  │        │
│  └───────────────┘ └───────────────┘ └───────────────┘        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Message Queue (Redis/RabbitMQ)               │ │
│  │  - Task distribution                                      │ │
│  │  - Result collection                                      │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │               Database (PostgreSQL)                       │ │
│  │  - Portfolio data                                         │ │
│  │  - Historical results                                     │ │
│  │  - Execution logs                                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │               Cache Layer (Redis)                         │ │
│  │  - API response caching                                   │ │
│  │  - Rate limit tracking                                    │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Characteristics**:
- ✅ Highly scalable (10+ agents)
- ✅ Parallel execution
- ✅ Independent agent deployment
- ✅ Fault tolerance (if one agent fails, others continue)
- ✅ Easy to add new agents
- ❌ More complex to set up
- ❌ Higher infrastructure cost

---

## Adding New Agents

### Step 1: Create Agent Class

**`agents/sentiment_agent.py`**:

```python
"""Sentiment Analysis Agent"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from transformers import pipeline  # or your sentiment library


class SentimentAgent(BaseAgent):
    """Agent for analyzing sentiment of news articles"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("sentiment_agent", config)

        # Initialize sentiment model
        self.model_name = self.get_config("model_name", "finbert-tone")
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=f"ProsusAI/{self.model_name}"
        )

    def _execute_internal(self, input_data: Any) -> Dict[str, Any]:
        """
        Analyze sentiment of news articles

        Args:
            input_data: Dict with "articles" key

        Returns:
            Dict with sentiment scores per article
        """
        articles = input_data.get("articles", [])

        sentiments = []
        for article in articles:
            text = article.get("title", "") + " " + article.get("description", "")

            # Analyze sentiment
            result = self.sentiment_analyzer(text)[0]

            sentiments.append({
                "article_id": article.get("url"),
                "sentiment": result["label"],  # positive/negative/neutral
                "confidence": result["score"],
                "symbol": article.get("symbol")
            })

        return {
            "total_articles": len(articles),
            "sentiments": sentiments,
            "average_sentiment": self._calculate_average(sentiments)
        }

    def _calculate_average(self, sentiments):
        """Calculate average sentiment score"""
        # Implementation here
        pass
```

### Step 2: Register Agent in Config

**`config.yaml`**:

```yaml
agents:
  news_agent:
    enabled: true
    config:
      max_articles_per_stock: 5
      days_back: 7

  report_agent:
    enabled: true
    config:
      include_financials: true

  # NEW: Sentiment Agent
  sentiment_agent:
    enabled: true
    config:
      model_name: "finbert-tone"
      batch_size: 32
```

### Step 3: Update main.py

**`main.py`** (add sentiment agent):

```python
from agents.sentiment_agent import SentimentAgent

# In run_with_config():
if config.is_agent_enabled('sentiment_agent'):
    try:
        print_section("EXECUTING SENTIMENT AGENT", "=")
        agent_config = config.get_agent_config('sentiment_agent')
        sentiment_agent = SentimentAgent(config=agent_config)

        # Get articles from news agent result
        articles = news_result['result']['news_by_stock']

        print("🔄 Running Sentiment Agent...")
        sentiment_result = sentiment_agent.execute({"articles": articles})
        results['sentiment'] = sentiment_result

        # Display and save
        display_sentiment_results(sentiment_result)
        sentiment_file = save_results(sentiment_result, "sentiment_results.json")
        print(f"\n💾 Saved: {sentiment_file}")
    except Exception as e:
        print(f"❌ Sentiment Agent failed: {str(e)}")
```

### Step 4: Add Agent Dockerfile (Optional - Microservices)

**`agents/sentiment_agent/Dockerfile`**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements-sentiment.txt .
RUN pip install --no-cache-dir -r requirements-sentiment.txt

# Copy agent code
COPY agents/base_agent.py agents/
COPY agents/sentiment_agent.py agents/
COPY services/ services/

# Create API wrapper
COPY api_wrapper.py .

# Expose port
EXPOSE 8000

# Run as API
CMD ["uvicorn", "api_wrapper:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Agent Orchestration

### Pattern 1: Sequential (Current)

```python
# main.py
results = {}

# Run agents one by one
if enabled('news_agent'):
    results['news'] = news_agent.execute(portfolio)

if enabled('report_agent'):
    results['reports'] = report_agent.execute(portfolio)

if enabled('sentiment_agent'):
    # Uses news results
    results['sentiment'] = sentiment_agent.execute(results['news'])
```

**Pros**: Simple, easy to debug
**Cons**: Slow (each agent waits for previous)

---

### Pattern 2: Parallel (Independent Agents)

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def run_agents_parallel(portfolio):
    """Run independent agents in parallel"""

    with ThreadPoolExecutor(max_workers=5) as executor:
        # Launch all agents simultaneously
        futures = []

        if enabled('news_agent'):
            futures.append(executor.submit(news_agent.execute, portfolio))

        if enabled('report_agent'):
            futures.append(executor.submit(report_agent.execute, portfolio))

        # Wait for all to complete
        results = [f.result() for f in futures]

    return results
```

**Pros**: Fast (agents run simultaneously)
**Cons**: More complex, requires thread-safe agents

---

### Pattern 3: DAG (Directed Acyclic Graph)

For agents with dependencies:

```python
from typing import Dict, List, Callable

class AgentOrchestrator:
    """Orchestrate agents with dependencies"""

    def __init__(self):
        self.agents = {}
        self.dependencies = {}

    def register_agent(self, name: str, agent: BaseAgent, depends_on: List[str] = None):
        """Register agent and its dependencies"""
        self.agents[name] = agent
        self.dependencies[name] = depends_on or []

    def execute(self, portfolio: Dict) -> Dict:
        """Execute agents in dependency order"""

        results = {}
        executed = set()

        def can_execute(agent_name: str) -> bool:
            """Check if dependencies are satisfied"""
            deps = self.dependencies[agent_name]
            return all(dep in executed for dep in deps)

        while len(executed) < len(self.agents):
            # Find agents ready to execute
            ready = [name for name in self.agents if name not in executed and can_execute(name)]

            if not ready:
                raise RuntimeError("Circular dependency detected")

            # Execute ready agents in parallel
            for agent_name in ready:
                agent = self.agents[agent_name]

                # Prepare input (include results from dependencies)
                input_data = {"portfolio": portfolio}
                for dep in self.dependencies[agent_name]:
                    input_data[dep] = results[dep]

                # Execute
                results[agent_name] = agent.execute(input_data)
                executed.add(agent_name)

        return results

# Usage:
orchestrator = AgentOrchestrator()

# Register agents with dependencies
orchestrator.register_agent("news_agent", news_agent, depends_on=[])
orchestrator.register_agent("report_agent", report_agent, depends_on=[])
orchestrator.register_agent("sentiment_agent", sentiment_agent, depends_on=["news_agent"])
orchestrator.register_agent("summary_agent", summary_agent, depends_on=["news_agent", "report_agent", "sentiment_agent"])

# Execute all
results = orchestrator.execute(portfolio)
```

**Dependency Graph**:
```
news_agent ────────┐
                   ├──→ sentiment_agent ───┐
report_agent ──────┘                       ├──→ summary_agent
                                           │
technical_agent ───────────────────────────┘
```

**Pros**: Handles complex dependencies, maximizes parallelism
**Cons**: Most complex to implement

---

## Communication Patterns

### Pattern 1: Shared Database

```
Agent 1 → Write to DB → Agent 2 reads from DB
```

**Implementation**:
```python
# Agent 1 saves results
db.save_results(portfolio_id, results)

# Agent 2 retrieves
previous_results = db.get_results(portfolio_id)
```

---

### Pattern 2: Message Queue (Redis/RabbitMQ)

```
Agent 1 → Publish message → Queue → Agent 2 subscribes
```

**Implementation**:
```python
import redis

r = redis.Redis()

# Agent 1 publishes
r.publish('news_complete', json.dumps(news_results))

# Agent 2 subscribes
pubsub = r.pubsub()
pubsub.subscribe('news_complete')
for message in pubsub.listen():
    if message['type'] == 'message':
        news_results = json.loads(message['data'])
        # Process
```

---

### Pattern 3: API Calls

```
Orchestrator → HTTP POST → Agent API → Response
```

**Agent API** (`api_wrapper.py`):
```python
from fastapi import FastAPI
from agents.news_agent import NewsAgent

app = FastAPI()
agent = NewsAgent()

@app.post("/execute")
async def execute_agent(portfolio: dict):
    result = agent.execute(portfolio)
    return result

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

**Orchestrator calls**:
```python
import httpx

async with httpx.AsyncClient() as client:
    # Call news agent
    response = await client.post(
        "http://news-agent-service:8000/execute",
        json={"portfolio": portfolio}
    )
    news_results = response.json()
```

---

## Deployment Strategies

### Strategy 1: Single Container (Current)

**When to use**: 2-5 agents, simple deployment

```yaml
# docker-compose.yml
services:
  event-horizon:
    image: event-horizon:latest
    # All agents in one container
```

---

### Strategy 2: Sidecar Pattern

**When to use**: 5-10 agents, shared resources

```yaml
services:
  main-app:
    image: event-horizon-orchestrator:latest

  news-agent:
    image: news-agent:latest

  report-agent:
    image: report-agent:latest

  sentiment-agent:
    image: sentiment-agent:latest
```

---

### Strategy 3: Kubernetes Microservices

**When to use**: 10+ agents, high scale

```yaml
# k8s/news-agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: news-agent
spec:
  replicas: 3  # Scale independently
  template:
    spec:
      containers:
      - name: news-agent
        image: news-agent:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: news-agent-service
spec:
  selector:
    app: news-agent
  ports:
  - port: 8000
```

---

## Monitoring & Observability

### Metrics to Track

```python
from prometheus_client import Counter, Histogram, Gauge

# Agent execution metrics
agent_executions = Counter('agent_executions_total', 'Total agent executions', ['agent_name', 'status'])
agent_duration = Histogram('agent_duration_seconds', 'Agent execution duration', ['agent_name'])
agent_errors = Counter('agent_errors_total', 'Total agent errors', ['agent_name', 'error_type'])

# Usage in BaseAgent
class BaseAgent(ABC):
    def execute(self, input_data: Any) -> Dict[str, Any]:
        start_time = time.time()

        try:
            result = self._execute_internal(input_data)
            agent_executions.labels(agent_name=self.agent_name, status='success').inc()
            return result
        except Exception as e:
            agent_errors.labels(agent_name=self.agent_name, error_type=type(e).__name__).inc()
            raise
        finally:
            duration = time.time() - start_time
            agent_duration.labels(agent_name=self.agent_name).observe(duration)
```

### Logging

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "agent_execution_started",
    agent_name=self.agent_name,
    portfolio_id=portfolio_id,
    execution_id=execution_id
)
```

### Tracing

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("agent_execution") as span:
    span.set_attribute("agent.name", self.agent_name)
    span.set_attribute("portfolio.id", portfolio_id)

    result = self._execute_internal(input_data)
```

---

## Roadmap: Scaling to 20+ Agents

### Phase 1: Current (2-5 agents)
- ✅ Single container deployment
- ✅ Sequential execution
- ✅ Config-based enabling

### Phase 2: Parallel (5-10 agents)
- 🔄 Add async execution
- 🔄 Implement parallel agent runs
- 🔄 Add result aggregation

### Phase 3: Microservices (10-20 agents)
- 📋 Convert agents to REST APIs
- 📋 Deploy on Kubernetes
- 📋 Add message queue (Redis)
- 📋 Implement orchestrator service

### Phase 4: Enterprise (20+ agents)
- 📋 Add database persistence
- 📋 Implement caching layer
- 📋 Add comprehensive monitoring
- 📋 Auto-scaling based on load
- 📋 Multi-region deployment

---

## Quick Migration Guide

### From Monolith to Microservices

1. **Add FastAPI wrapper to each agent**
2. **Create separate Dockerfiles**
3. **Deploy to Kubernetes**
4. **Add orchestrator service**
5. **Migrate gradually** (start with one agent as microservice)

See full guide: `docs/migration-to-microservices.md` (coming soon)

---

## Summary

**Current**: Simple, works for 2-5 agents
**Future**: Scalable, supports 20+ agents with orchestration

**Next Steps**:
1. Keep current architecture until you have 5+ agents
2. When scaling, start with parallel execution
3. Move to microservices when you have 10+ agents
4. Use Kubernetes for production scale

Ready to scale? Start by adding your next agent using the guide above!
