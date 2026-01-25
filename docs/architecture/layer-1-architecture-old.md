# Layer 1 Architecture

## System Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                         USER / APPLICATION                              │
│                               main_layer1.py                            │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       LAYER 1 ORCHESTRATOR                              │
│                   layer_1/orchestrator/                                 │
│                                                                         │
│  • Parallel execution (ThreadPoolExecutor)                             │
│  • Agent lifecycle management                                          │
│  • Result aggregation                                                  │
│  • Error handling                                                      │
└────────────────────────────────────────────────────────────────────────┘
                │                 │                 │
                ▼                 ▼                 ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │ Candlestick  │  │   Earnings   │  │     News     │
        │    Agent     │  │    Agent     │  │    Agent     │
        └──────────────┘  └──────────────┘  └──────────────┘
                │                 │                 │
                ▼                 ▼                 ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │   Chart      │  │  Financial   │  │   News       │
        │   Service    │  │   Service    │  │  Service     │
        └──────────────┘  └──────────────┘  └──────────────┘
                │                 │                 │
                ▼                 ▼                 ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │Yahoo Finance │  │Yahoo Finance │  │  NewsAPI     │
        │ Massive.com  │  │              │  │              │
        └──────────────┘  └──────────────┘  └──────────────┘
```

## Component Layers

### 1. Application Layer

**File**: `main_layer1.py`

Responsibilities:
- User interface / entry point
- Configuration setup
- Result display
- Output persistence

### 2. Orchestration Layer

**File**: `layer_1/orchestrator/layer_1_orchestrator.py`

Responsibilities:
- Parallel agent execution
- Configuration distribution
- Result aggregation
- Error handling
- Status management

### 3. Agent Layer

**Files**:
- `layer_1/agents/candlestick_agent.py`
- `layer_1/agents/earnings_agent.py`
- `layer_1/agents/news_agent.py`

Responsibilities:
- Data retrieval logic
- Input validation
- Output formatting
- Error handling
- Retry logic

### 4. Service Layer

**Files**:
- `services/chart_data_client.py`
- `services/financial_data_client.py`
- `services/news_api_client.py`

Responsibilities:
- External API communication
- Authentication
- Rate limiting
- Response parsing
- HTTP error handling

### 5. External APIs

- Yahoo Finance (chart + financial data)
- Massive.com (alternative chart data)
- NewsAPI (news articles)

## Data Flow

### Sequential Flow (Step-by-step)

```
1. User Request
   portfolio = ["AAPL", "TSLA", "SPY"]

2. Orchestrator Init
   - Load configuration
   - Initialize agents
   - Set up thread pool

3. Parallel Execution
   Thread 1: CandlestickAgent.execute(portfolio)
   Thread 2: EarningsAgent.execute(portfolio)
   Thread 3: NewsAgent.execute(portfolio)

4. Agent Processing (each agent)
   - Parse input
   - For each symbol:
     - Call service client
     - Get data
     - Format output
   - Return result

5. Result Aggregation
   - Collect all agent results
   - Build Layer1Output
   - Calculate metadata
   - Determine overall status

6. Return to User
   - Layer1Output object
   - Execution metadata
   - Error information
```

### Parallel Execution Timeline

```
Time  →
0s    ├─ Start Orchestrator
      │
1s    ├─ Launch Agents (parallel)
      │  ├─ CandlestickAgent starts
      │  ├─ EarningsAgent starts
      │  └─ NewsAgent starts
      │
2s    │  ├─ NewsAgent fetching...
      │  ├─ CandlestickAgent fetching...
      │  └─ EarningsAgent fetching...
      │
3s    │  ├─ NewsAgent ✓ done (3s)
      │  ├─ CandlestickAgent fetching...
      │  └─ EarningsAgent fetching...
      │
5s    │  ├─ CandlestickAgent ✓ done (5s)
      │  └─ EarningsAgent fetching...
      │
7s    │  └─ EarningsAgent ✓ done (7s)
      │
8s    ├─ Aggregate results
      │
9s    └─ Return Layer1Output

Total: 9s (vs 15s sequential)
```

## Module Dependencies

```
main_layer1.py
    │
    └── layer_1.Layer1Orchestrator
            │
            ├── layer_1.agents.CandlestickAgent
            │       └── services.ChartDataClient
            │               └── [Yahoo Finance API]
            │
            ├── layer_1.agents.EarningsAgent
            │       └── services.FinancialDataClient
            │               └── [Yahoo Finance API]
            │
            └── layer_1.agents.NewsAgent
                    └── services.NewsAPIClient
                            └── [NewsAPI]
```

## Class Hierarchy

```
layer_1.agents.base_agent.BaseAgent (ABC)
    │
    ├── CandlestickAgent
    │   - Inherits: execute(), get_config()
    │   - Implements: _execute_internal()
    │   - Uses: ChartDataClient
    │
    ├── EarningsAgent
    │   - Inherits: execute(), get_config()
    │   - Implements: _execute_internal()
    │   - Uses: FinancialDataClient
    │
    └── NewsAgent
        - Inherits: execute(), get_config()
        - Implements: _execute_internal()
        - Uses: NewsAPIClient
```

## Data Schemas

```
Layer1Output
    ├── portfolio_id: str
    ├── symbols: List[str]
    │
    ├── chart_data: Dict[str, ChartData]
    │   └── ChartData
    │       ├── symbol: str
    │       ├── candles: List[Dict]
    │       ├── period: str
    │       ├── interval: str
    │       └── error: Optional[str]
    │
    ├── earnings_data: Dict[str, EarningsData]
    │   └── EarningsData
    │       ├── symbol: str
    │       ├── security_type: str
    │       ├── earnings_reports: Dict
    │       ├── financial_statements: Dict
    │       └── error: Optional[str]
    │
    ├── news_data: Dict[str, NewsData]
    │   └── NewsData
    │       ├── symbol: str
    │       ├── articles: List[Dict]
    │       ├── total_articles: int
    │       └── error: Optional[str]
    │
    └── metadata
        ├── execution_time_seconds: float
        ├── agents_executed: List[str]
        ├── status: str
        └── errors: List[Dict]
```

## Error Handling Strategy

```
┌─────────────────────────────────────────┐
│  Orchestrator Level                     │
│  - Catches agent initialization errors  │
│  - Catches agent execution exceptions   │
│  - Continues with remaining agents      │
└─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Agent Level                            │
│  - Catches symbol processing errors     │
│  - Marks individual symbols as failed   │
│  - Continues with remaining symbols     │
└─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Service Level                          │
│  - Catches HTTP errors                  │
│  - Catches API errors                   │
│  - Raises exceptions to agent           │
└─────────────────────────────────────────┘
```

### Error Propagation Example

```
API fails for TSLA earnings
    ↓
Service raises exception
    ↓
Agent catches, marks TSLA as error
    ↓
Agent continues with next symbol (SPY)
    ↓
Agent returns partial results
    ↓
Orchestrator marks agent as partial_success
    ↓
Orchestrator continues with other agents
    ↓
Final result: partial_success
```

## Configuration Flow

```
User Config
    ↓
{
  "enabled_agents": ["candlestick", "earnings"],
  "agent_configs": {
    "candlestick": {"period": "1mo"},
    "earnings": {"include_financials": true}
  }
}
    ↓
Layer1Orchestrator
    ↓
    ├─ CandlestickAgent(config={"period": "1mo"})
    └─ EarningsAgent(config={"include_financials": true})
```

## Scalability Design

### Current (3 agents)

```
max_workers = 3

Thread Pool:
├── Thread 1: CandlestickAgent
├── Thread 2: EarningsAgent
└── Thread 3: NewsAgent
```

### Future (10+ agents)

```
max_workers = 5

Thread Pool:
├── Thread 1: CandlestickAgent
├── Thread 2: EarningsAgent
├── Thread 3: NewsAgent
├── Thread 4: OptionsFlowAgent
├── Thread 5: SocialMediaAgent
└── [Queue]: SECFilingsAgent, InsiderTradingAgent, ...
```

Agents beyond max_workers wait in queue.

## Extension Points

### Adding a New Agent

1. **Create Agent Class**
   ```python
   # layer_1/agents/options_flow_agent.py
   class OptionsFlowAgent(BaseAgent):
       def _execute_internal(self, input_data):
           # Implementation
   ```

2. **Add Data Schema**
   ```python
   # layer_1/models/schemas.py
   @dataclass
   class OptionsFlowData:
       symbol: str
       options_chain: Dict
       # ...
   ```

3. **Register in Orchestrator**
   ```python
   # layer_1/orchestrator/layer_1_orchestrator.py
   if agent_name == "options_flow":
       agent = OptionsFlowAgent(config=agent_config)
   ```

4. **Update Layer1Output**
   ```python
   # layer_1/models/schemas.py
   @dataclass
   class Layer1Output:
       # ...
       options_data: Dict[str, OptionsFlowData]
   ```

## Performance Characteristics

| Aspect | Measurement |
|--------|-------------|
| **Latency** | Max of individual agent times |
| **Throughput** | Parallel: N agents in ~max(agent_times) |
| **Scalability** | Linear up to max_workers |
| **Resource Usage** | CPU: Low, I/O: Network-bound |
| **Bottleneck** | External API rate limits |

## Thread Safety

- **Orchestrator**: Thread-safe (uses ThreadPoolExecutor)
- **Agents**: Stateless execution (no shared state)
- **Services**: Thread-safe HTTP clients
- **Data Models**: Immutable (dataclasses)

## Future Architecture Evolution

```
Layer 1 (Current)
    ↓
Layer 2 (Normalization)
    • Unified schema
    • Time synchronization
    • Symbol mapping
    ↓
Layer 3 (Feature Extraction)
    • LLM/Neural AI
    • Pattern discovery
    • Trading signals
    ↓
Trading System
```

## See Also

- [Multi-Agent Design](./multi-agent-design.md) - Overall architecture
- [Layer 1 Guide](../guides/layer-1-guide.md) - Usage documentation
- [Core References](../core-refs/README.md) - Research inspiration
