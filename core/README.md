# Core Components

Shared base classes, utilities, and schemas used across all layers of Event Horizon.

## Purpose

The `core/` directory contains components that are **layer-independent** and used by multiple layers (Layer 1, Layer 2, Layer 3). This promotes code reuse and maintains consistency across the system.

## Directory Structure

```
core/
├── base/                  # Base classes
│   ├── base_agent.py     # Base class for all agents
│   └── base_orchestrator.py  # Base class for layer orchestrators
│
├── schemas/              # Shared data models (future)
│   └── common.py         # Common data types
│
├── config/               # Configuration management (future)
│   ├── settings.py       # Global settings
│   └── validator.py      # Config validation
│
└── utils/                # Shared utilities (future)
    ├── logging.py        # Logging setup
    ├── validation.py     # Data validation
    └── helpers.py        # Common helper functions
```

## Base Classes

### BaseAgent

Base class for all agents across all layers.

**Location**: `core/base/base_agent.py`

**Usage**:
```python
from core.base import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__("my_agent", config)

    def _execute_internal(self, input_data):
        # Implement agent logic
        return {"result": "data"}
```

**Provides**:
- Common execution framework (`execute()` method)
- Structured result format
- Error handling and logging
- Configuration management
- Execution timing and metadata

**Used by**:
- Layer 1 agents (CandlestickAgent, EarningsAgent, NewsAgent)
- Layer 2 agents (future)
- Layer 3 agents (future)

### BaseOrchestrator

Base class for layer orchestrators.

**Location**: `core/base/base_orchestrator.py`

**Usage**:
```python
from core.base import BaseOrchestrator

class Layer1Orchestrator(BaseOrchestrator):
    def __init__(self, config=None):
        super().__init__("layer_1", config)

    def execute(self, input_data):
        # Implement layer orchestration
        return {"status": "success", "output": ...}
```

**Provides**:
- Common orchestration framework
- Agent management (enable/disable agents)
- Configuration handling
- Logging setup

**Used by**:
- Layer 1 orchestrator
- Layer 2 orchestrator (future)
- Layer 3 orchestrator (future)

## Why Core?

### Without Core (Problematic)

```
layer_1/
├── base_agent.py         # Duplicated
├── agents/...

layer_2/
├── base_agent.py         # Duplicated (same code!)
├── agents/...

layer_3/
├── base_agent.py         # Duplicated (same code!)
├── agents/...
```

**Problems**:
- Code duplication
- Inconsistent behavior across layers
- Hard to maintain (change in 3 places)
- No single source of truth

### With Core (Clean)

```
core/
└── base/
    ├── base_agent.py     # Single source of truth

layer_1/
└── agents/
    ├── candlestick_agent.py  → imports from core.base
    └── news_agent.py         → imports from core.base

layer_2/
└── agents/
    └── normalizer_agent.py   → imports from core.base

layer_3/
└── agents/
    └── feature_agent.py      → imports from core.base
```

**Benefits**:
- ✅ Single source of truth
- ✅ Consistent behavior
- ✅ Easy to maintain
- ✅ DRY (Don't Repeat Yourself)

## What Goes in Core vs Layers?

### Goes in Core ✅

**Shared across multiple layers**:
- Base classes (BaseAgent, BaseOrchestrator)
- Common data validation
- Shared utilities (logging, config)
- Universal schemas (Portfolio, Symbol)
- Error handling framework

### Goes in Layers ❌

**Layer-specific**:
- Layer 1: Data retrieval agents, ChartData schema
- Layer 2: Normalization agents, DNA schema
- Layer 3: Feature extraction agents, Signal schema
- Layer-specific models and logic

## Design Pattern

Core follows the **Template Method Pattern**:

```python
# core/base/base_agent.py
class BaseAgent(ABC):
    def execute(self, input_data):
        # Common logic (template)
        try:
            result = self._execute_internal(input_data)  # Hook
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    @abstractmethod
    def _execute_internal(self, input_data):
        # Implemented by subclass
        pass

# layer_1/agents/news_agent.py
class NewsAgent(BaseAgent):
    def _execute_internal(self, input_data):
        # Layer 1 specific logic
        articles = self.news_client.fetch(...)
        return {"articles": articles}
```

## Import Guidelines

### Correct ✅

```python
# In layer_1/agents/news_agent.py
from core.base import BaseAgent  # Import from core
from services.news_api_client import NewsAPIClient  # Import service
```

### Incorrect ❌

```python
# In layer_1/agents/news_agent.py
from layer_1.agents.base_agent import BaseAgent  # Wrong! Use core
from layer_2.utils.helper import some_function  # Wrong! Cross-layer import
```

**Rules**:
1. Always import base classes from `core/`
2. Never import between layers (layer_1 → layer_2)
3. Layers can import from `services/` (shared)
4. Layers can import from `utils/` (shared)
5. Layers can import from `core/` (shared)

## Extension Points

### Adding New Base Classes

When you find yourself copying code between layers, create a base class in `core/`:

```python
# If multiple layers need similar validation
# core/base/base_validator.py
class BaseValidator(ABC):
    @abstractmethod
    def validate(self, data):
        pass
```

### Adding Shared Utilities

```python
# If multiple layers need similar helpers
# core/utils/data_helpers.py
def normalize_symbol(symbol: str) -> str:
    """Normalize stock symbols to uppercase"""
    return symbol.strip().upper()
```

### Adding Common Schemas

```python
# If multiple layers use the same data structure
# core/schemas/common.py
@dataclass
class Portfolio:
    portfolio_id: str
    symbols: List[str]
    created_at: str
```

## Future Additions

Planned `core/` components:

1. **core/config/**
   - Global configuration management
   - Environment variable loading
   - Config validation

2. **core/schemas/**
   - Portfolio schema
   - Symbol validation
   - Common enums

3. **core/utils/**
   - Logging configuration
   - Rate limiting
   - Retry logic
   - Data validation

4. **core/exceptions/**
   - Custom exception classes
   - Error handling utilities

## Testing

Base classes should be thoroughly tested:

```python
# tests/core/test_base_agent.py
def test_base_agent_execution():
    class TestAgent(BaseAgent):
        def _execute_internal(self, data):
            return {"value": data * 2}

    agent = TestAgent(config={})
    result = agent.execute(5)

    assert result["status"] == "success"
    assert result["result"]["value"] == 10
```

## Migration

If you have code in a layer that should be in core:

1. Move to appropriate `core/` subdirectory
2. Update all imports across layers
3. Add tests
4. Update documentation

Example:
```bash
# Move base_agent from layer_1 to core
mv layer_1/agents/base_agent.py core/base/base_agent.py

# Update imports in all agents
# from layer_1.agents.base_agent import BaseAgent
# to
# from core.base import BaseAgent
```

## See Also

- [Layer 1 README](../layer_1/README.md) - Layer 1 specific components
- [Services README](../services/README.md) - External API clients
- [Architecture](../docs/architecture/multi-agent-design.md) - System architecture
