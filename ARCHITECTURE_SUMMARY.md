# Event Horizon Architecture Summary

## Complete Directory Structure

```
Event-Horizon-AI/
│
├── core/                            ⭐ SHARED COMPONENTS
│   ├── base/
│   │   ├── base_agent.py           # Base class for all agents (all layers)
│   │   └── base_orchestrator.py    # Base class for all orchestrators
│   ├── schemas/                     # (Future) Common data models
│   ├── config/                      # (Future) Configuration management
│   └── utils/                       # (Future) Shared utilities
│
├── layer_1/                         ⭐ DATA RETRIEVAL LAYER
│   ├── agents/
│   │   ├── candlestick_agent.py    # OHLCV price data
│   │   ├── earnings_agent.py       # Financial reports
│   │   └── news_agent.py           # News articles
│   ├── models/
│   │   └── schemas.py              # Layer 1 output schemas
│   └── orchestrator/
│       └── layer_1_orchestrator.py # Parallel execution manager
│
├── layer_2/                         📋 NORMALIZATION LAYER (Future)
│   ├── agents/
│   │   ├── data_filter_agent.py    # Data cleaning
│   │   ├── time_sync_agent.py      # Time synchronization
│   │   └── symbol_mapper_agent.py  # Symbol normalization
│   ├── models/
│   │   └── dna_schema.py           # Unified "DNA" schema
│   └── orchestrator/
│       └── layer_2_orchestrator.py
│
├── layer_3/                         📋 FEATURE EXTRACTION LAYER (Future)
│   ├── agents/
│   │   ├── pattern_agent.py        # Pattern discovery
│   │   └── signal_agent.py         # Trading signals
│   ├── models/
│   │   └── feature_schema.py       # Feature schemas
│   └── orchestrator/
│       └── layer_3_orchestrator.py
│
├── services/                        🔌 EXTERNAL API CLIENTS
│   ├── news_api_client.py          # NewsAPI
│   ├── financial_data_client.py    # Yahoo Finance (financials)
│   ├── chart_data_client.py        # Yahoo Finance (charts)
│   └── massive_chart_client.py     # Massive.com
│
├── utils/                           🛠️ UTILITIES
│   ├── config_loader.py
│   ├── error_handler.py
│   └── rate_limiter.py
│
├── agents/                          ⚠️ LEGACY (Deprecated)
│   ├── base_agent.py               # Use core/base instead
│   ├── news_agent.py               # Use layer_1/agents instead
│   ├── report_agent.py             # Use layer_1/agents instead
│   └── chart_agent.py              # Use layer_1/agents instead
│
├── docs/
│   ├── architecture/
│   │   ├── multi-agent-design.md
│   │   └── layer-1-architecture.md
│   ├── guides/
│   │   ├── layer-1-guide.md
│   │   └── migration-to-layer1.md
│   └── core-refs/                  # Research papers
│
├── main_layer1.py                   🚀 Layer 1 demo script
├── main.py                          ⚠️ Legacy (still works)
│
├── QUICKSTART_LAYER1.md
└── README.md
```

## Architecture Layers

### Core (Shared Foundation)

**Purpose**: Shared base classes and utilities used by ALL layers

**Components**:
- `BaseAgent` - Template for all agents
- `BaseOrchestrator` - Template for all orchestrators
- Common schemas, config, utilities

**Used by**: Layer 1, Layer 2, Layer 3

### Layer 1: Data Retrieval

**Purpose**: Collect heterogeneous data from multiple sources

**Pattern**: Parallel, Independent Agents

**Agents**:
- CandlestickAgent → Yahoo/Massive → OHLCV data
- EarningsAgent → Yahoo → Financial reports
- NewsAgent → NewsAPI → News articles

**Output**: `Layer1Output` (heterogeneous, raw data)

**Status**: ✅ Complete

### Layer 2: Normalization (Future)

**Purpose**: Transform heterogeneous data into unified schema

**Pattern**: Sequential, Dependent Agents

**Agents**:
- DataFilterAgent - Clean and validate
- TimeSyncAgent - Align timestamps
- SymbolMapperAgent - Normalize symbols
- FormatNormalizerAgent - Unified format

**Output**: `DNA` (Data Normalized & Aligned) - tabular format

**Status**: 📋 Planned

### Layer 3: Feature Extraction (Future)

**Purpose**: Extract features and generate trading signals

**Pattern**: LLM/Neural AI

**Agents**:
- PatternDiscoveryAgent - Find patterns
- FeatureExtractionAgent - Extract features
- SignalGenerationAgent - Trading signals

**Output**: Trading signals, predictions

**Status**: 📋 Planned

### Services (External APIs)

**Purpose**: Communication with external data sources

**Components**:
- NewsAPIClient
- FinancialDataClient
- ChartDataClient
- MassiveChartClient

**Used by**: Layer 1 agents

## Data Flow

```
User Input
    ↓
┌─────────────────────────────────────┐
│  LAYER 1: Data Retrieval            │
│  (Parallel Execution)               │
│                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────┐│
│  │Candlestk│  │Earnings │  │News ││
│  │ Agent   │  │ Agent   │  │Agent││
│  └─────────┘  └─────────┘  └─────┘│
│       ↓             ↓          ↓   │
│  Layer1Output (heterogeneous)      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  LAYER 2: Normalization             │
│  (Sequential Transformation)        │
│                                     │
│  Filter → TimeSync → SymbolMap      │
│       ↓             ↓          ↓   │
│  DNA Schema (unified tabular)       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  LAYER 3: Feature Extraction        │
│  (LLM/Neural AI)                    │
│                                     │
│  Pattern → Feature → Signal         │
│       ↓             ↓          ↓   │
│  Trading Signals                    │
└─────────────────────────────────────┘
    ↓
Trading System
```

## Import Structure

### Correct Imports ✅

```python
# Layer 1 agents
from core.base import BaseAgent          # Base class from core
from services.chart_data_client import ChartDataClient  # Service
from layer_1.models.schemas import ChartData  # Layer 1 schema

# Layer 2 agents (future)
from core.base import BaseAgent          # Same base class
from layer_1.models.schemas import Layer1Output  # Input from Layer 1
from layer_2.models.schemas import DNA   # Layer 2 schema

# Layer 3 agents (future)
from core.base import BaseAgent          # Same base class
from layer_2.models.schemas import DNA   # Input from Layer 2
```

### Import Rules

1. **All agents** → import `BaseAgent` from `core.base`
2. **All orchestrators** → import `BaseOrchestrator` from `core.base`
3. **Layers can import** → from `services/` (shared API clients)
4. **Layers can import** → from `core/` (shared base classes)
5. **Layers can import** → from previous layer's models (for input)
6. **Layers CANNOT** → cross-import agents from other layers

## Execution Flow

### Layer 1 Execution

```python
from layer_1 import Layer1Orchestrator

# User provides portfolio
portfolio = ["AAPL", "TSLA", "SPY"]

# Orchestrator manages parallel execution
orchestrator = Layer1Orchestrator(config={
    "enabled_agents": ["candlestick", "earnings", "news"]
})

# Execute all agents in parallel
result = orchestrator.execute(portfolio)

# Get heterogeneous output
layer1_output = result["layer1_output"]
```

### Future: Full Pipeline

```python
from layer_1 import Layer1Orchestrator
from layer_2 import Layer2Orchestrator
from layer_3 import Layer3Orchestrator

# Layer 1: Data Retrieval
layer1 = Layer1Orchestrator()
layer1_output = layer1.execute(portfolio)

# Layer 2: Normalization
layer2 = Layer2Orchestrator()
dna = layer2.execute(layer1_output)  # Input: Layer1Output → Output: DNA

# Layer 3: Feature Extraction
layer3 = Layer3Orchestrator()
signals = layer3.execute(dna)  # Input: DNA → Output: Signals
```

## Component Relationships

```
┌───────────────────────────────────────────────┐
│                    CORE                       │
│  BaseAgent, BaseOrchestrator, Common Utils    │
└───────────────────────────────────────────────┘
            ↑            ↑            ↑
            │            │            │
     ┌──────┴────┐  ┌───┴─────┐  ┌──┴──────┐
     │  Layer 1  │  │ Layer 2 │  │ Layer 3 │
     │  Agents   │  │ Agents  │  │ Agents  │
     └──────┬────┘  └───┬─────┘  └──┬──────┘
            ↓            │            │
     ┌──────────┐       │            │
     │ Services │←──────┘            │
     └──────────┘                    │
            ↓                         │
     External APIs                   │
     (NewsAPI, Yahoo, etc)           │
```

## Key Design Principles

### 1. Separation of Concerns

- **Core**: Shared functionality
- **Layers**: Specific processing stages
- **Services**: External communication

### 2. Inheritance Hierarchy

```
BaseAgent (core)
    ↓
CandlestickAgent (layer_1)
    ↓
(instantiated for execution)
```

### 3. Parallel vs Sequential

- **Layer 1**: Parallel (agents independent)
- **Layer 2**: Sequential (data transformation pipeline)
- **Layer 3**: Hybrid (parallel feature extraction, sequential signal gen)

### 4. Data Schemas

Each layer has its own output schema:
- Layer 1: `Layer1Output` (heterogeneous)
- Layer 2: `DNA` (normalized, tabular)
- Layer 3: `Signals` (actionable)

## Performance

| Layer | Pattern | Execution | Bottleneck |
|-------|---------|-----------|------------|
| **Layer 1** | Parallel | ~7s (4 stocks, 3 agents) | External API calls |
| **Layer 2** | Sequential | TBD | Data transformation |
| **Layer 3** | Hybrid | TBD | LLM inference |

## Migration Path

### From Old System → New System

**Old**:
```python
from agents.news_agent import NewsAgent
agent = NewsAgent()
result = agent.execute(portfolio)
```

**New**:
```python
from layer_1 import Layer1Orchestrator
orchestrator = Layer1Orchestrator()
result = orchestrator.execute(portfolio)
```

**Benefits**:
- 2x faster (parallel execution)
- Structured output schemas
- Better error handling
- Scalable to 10+ agents

## Future Roadmap

### Phase 1: Layer 1 ✅ Complete
- Parallel data retrieval
- 3 agents (Candlestick, Earnings, News)
- Core base classes

### Phase 2: Layer 1 Expansion
- Add OptionsFlowAgent
- Add SocialMediaAgent
- Add SECFilingsAgent
- Add InsiderTradingAgent

### Phase 3: Layer 2
- Build normalization agents
- Design DNA schema
- Implement Layer 2 orchestrator

### Phase 4: Layer 3
- Research tabular LLM frameworks
- Implement feature extraction
- Build signal generation

### Phase 5: Integration
- End-to-end pipeline
- Backtesting framework
- Production deployment

## Documentation

- **Getting Started**: [QUICKSTART_LAYER1.md](QUICKSTART_LAYER1.md)
- **Layer 1 Guide**: [docs/guides/layer-1-guide.md](docs/guides/layer-1-guide.md)
- **Architecture**: [docs/architecture/layer-1-architecture.md](docs/architecture/layer-1-architecture.md)
- **Core Components**: [core/README.md](core/README.md)
- **Migration**: [docs/guides/migration-to-layer1.md](docs/guides/migration-to-layer1.md)

## Summary

Event Horizon is a **three-layer multi-agent trading system**:

1. **Core** - Shared foundation for all layers
2. **Layer 1** - Heterogeneous data retrieval (✅ Complete)
3. **Layer 2** - Data normalization (📋 Planned)
4. **Layer 3** - Feature extraction & signals (📋 Planned)

**Current Status**: Layer 1 production-ready with core foundation established.

**Next Step**: Expand Layer 1 agents or begin Layer 2 design.

---

**Version**: Layer 1 v1.0
**Last Updated**: 2026-01-25
