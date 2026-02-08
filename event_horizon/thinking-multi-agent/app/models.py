from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ── Agent models ──

class CreateAgentRequest(BaseModel):
    """Create a specialized agent with a custom system prompt."""

    name: str = Field(..., description="Agent name (e.g., 'risk-analyst', 'quant-trader')")
    description: Optional[str] = Field(default="", description="What this agent does")
    type: Optional[str] = Field(
        default="analysis",
        description="Agent type: 'analysis' (runs LLM) or 'data' (provides data via EH pipeline or custom source)",
    )
    source: Optional[str] = Field(
        default=None,
        description="Data source for data agents: 'built-in' (EH Stage 1) or 'custom'. Ignored for analysis agents.",
    )
    system_prompt: str = Field(..., description="Custom system prompt that defines the agent's behavior")
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=4096, ge=1, le=16384)


class AgentResponse(BaseModel):
    agent_id: str
    name: str
    description: str
    type: str = "analysis"
    source: Optional[str] = None
    system_prompt: str
    temperature: float
    max_tokens: int
    created_at: str
    deletable: bool = True


# ── Analysis models ──

class AnalysisRequest(BaseModel):
    """Input schema for financial analysis requests."""

    task: str = Field(..., description="The analysis task to perform")
    financial_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Tabular financial data (e.g., OHLCV price data, balance sheet items, ratios)",
    )
    earnings_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Tabular earnings data (e.g., revenue, EPS, guidance, quarterly results)",
    )
    news_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="News articles or headlines with dates, sources, and content",
    )
    additional_context: Optional[str] = Field(
        default=None,
        description="Any extra context or instructions for the analysis",
    )
    stocks: Optional[List[str]] = Field(
        default=None,
        description="List of stock symbols to analyze (e.g., ['AAPL', 'MSFT'])",
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Custom system prompt override for this analysis",
    )
    metadata: Optional[Any] = Field(
        default=None,
        description="Nested metadata from Event-Horizon data agents (earnings, prices, news, etc.)",
    )
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=16384)


class AnalysisResponse(BaseModel):
    """Output schema for financial analysis responses."""

    agent_id: Optional[str] = Field(default=None, description="Agent used")
    agent_name: Optional[str] = Field(default=None, description="Agent name")
    reasoning: Optional[str] = Field(
        default=None,
        description="The model's chain-of-thought reasoning (from [THINK] tags)",
    )
    analysis: Optional[str] = Field(default=None, description="The final analysis output")
    model: str = Field(..., description="Model used for the analysis")
    status: str = Field(default="success", description="Response status: success, needs_data, data_source, error")
    provider: str = Field(default="eh-multi-agent", description="Service provider identifier")
    required_agents: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="List of EH data agents needed (returned when status=needs_data)",
    )
    data_source: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Data source spec returned when a data agent is called (status=data_source)",
    )
    usage: Optional[Dict[str, Any]] = Field(default=None, description="Token usage statistics")


class HealthResponse(BaseModel):
    status: str
    model: str
    agents_count: int = 0
    llm_backend_status: Optional[str] = None
    timestamp: Optional[str] = None


# ── Request models for legacy agent endpoints ──

class PortfolioRequest(BaseModel):
    portfolio: List[str]
    portfolio_id: Optional[str] = None
    enabled_agents: Optional[List[str]] = None
    agent_configs: Optional[dict] = None


class AgentRequest(BaseModel):
    """Request model for individual agent execution."""
    stocks: List[str]
    timeframe: Optional[str] = "1d"
    period: Optional[str] = "30d"
    days: Optional[int] = 7
    indicators: Optional[List[str]] = None


class System2Request(BaseModel):
    """Request model for System 2 agents (bull-bear, risk-manager, etc.)."""
    stocks: List[str]
    data: Optional[dict] = None


class CustomAgentRequest(BaseModel):
    """Request model for custom agent execution."""
    stocks: List[str]
    system_prompt: str
    user_prompt: Optional[str] = None
    llm_config: Optional[dict] = None


class GenerateSystemPromptRequest(BaseModel):
    """Request model for generating system prompts."""
    name: str
    description: Optional[str] = ""
    category: Optional[str] = "strategy_agent"


class ThinkingAgentRequest(BaseModel):
    """Request model for iterative thinking agent execution."""
    stocks: List[str]
    input_data: Optional[dict] = None
    system_prompt: str
    max_iterations: int = 5
    available_tools: List[str] = ["candlestick", "earnings", "news", "technical", "fundamentals"]
