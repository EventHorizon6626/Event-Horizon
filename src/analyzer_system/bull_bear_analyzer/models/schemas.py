"""
Bull-Bear Analyzer: Debate Schemas

Output structures for the bull/bear debate system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class BullArgument:
    """
    Bull researcher's argument for buying/long position

    The bull agent argues why the stock will go UP.
    """

    symbol: str

    # Core argument
    recommendation: str = "BUY"  # BUY, STRONG_BUY
    confidence: float = 0.0  # 0-1
    target_price: Optional[float] = None
    time_horizon: str = ""  # "1 week", "1 month", "3 months"

    # Reasoning
    thesis: str = ""  # Main bullish thesis
    key_catalysts: List[str] = field(default_factory=list)  # Growth drivers
    supporting_evidence: List[str] = field(default_factory=list)  # Data points
    risk_acknowledgment: List[str] = field(default_factory=list)  # Known risks

    # Opik tracking
    opik_trace_id: Optional[str] = None
    tokens_used: int = 0

    # Full LLM reasoning (for transparency and debugging)
    raw_llm_response: str = ""  # Complete LLM output including all reasoning
    llm_prompt: str = ""  # The prompt sent to the LLM

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class BearArgument:
    """
    Bear researcher's argument for selling/short position

    The bear agent argues why the stock will go DOWN.
    """

    symbol: str

    # Core argument
    recommendation: str = "SELL"  # SELL, STRONG_SELL, SHORT
    confidence: float = 0.0  # 0-1
    target_price: Optional[float] = None
    time_horizon: str = ""  # "1 week", "1 month", "3 months"

    # Reasoning
    thesis: str = ""  # Main bearish thesis
    key_risks: List[str] = field(default_factory=list)  # Downside risks
    supporting_evidence: List[str] = field(default_factory=list)  # Data points
    bull_case_rebuttal: List[str] = field(default_factory=list)  # Counter-arguments

    # Opik tracking
    opik_trace_id: Optional[str] = None
    tokens_used: int = 0

    # Full LLM reasoning (for transparency and debugging)
    raw_llm_response: str = ""  # Complete LLM output including all reasoning
    llm_prompt: str = ""  # The prompt sent to the LLM

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class InvestmentThesis:
    """
    Synthesized investment thesis from bull/bear debate

    Research manager combines both perspectives into final recommendation.
    """

    symbol: str

    # Final recommendation
    recommendation: str = ""  # BUY, HOLD, SELL
    confidence: float = 0.0  # 0-1
    position_size: str = ""  # "small", "medium", "large"

    # Synthesis
    thesis_summary: str = ""  # Balanced view
    bull_case_summary: str = ""  # Key bull points
    bear_case_summary: str = ""  # Key bear points

    # Probabilities
    bull_probability: float = 0.5  # 0-1, probability of upside
    bear_probability: float = 0.5  # 0-1, probability of downside

    # Scenarios
    base_case: str = ""  # Most likely outcome
    bull_case: str = ""  # Best case scenario
    bear_case: str = ""  # Worst case scenario

    # Opik tracking
    opik_trace_id: Optional[str] = None
    tokens_used: int = 0

    # Full LLM reasoning (for transparency and debugging)
    raw_llm_response: str = ""  # Complete LLM output including all reasoning
    llm_prompt: str = ""  # The prompt sent to the LLM

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "position_size": self.position_size,
            "thesis_summary": self.thesis_summary,
            "bull_case_summary": self.bull_case_summary,
            "bear_case_summary": self.bear_case_summary,
            "bull_probability": self.bull_probability,
            "bear_probability": self.bear_probability,
            "base_case": self.base_case,
            "bull_case": self.bull_case,
            "bear_case": self.bear_case,
            "opik_trace_id": self.opik_trace_id,
            "tokens_used": self.tokens_used,
            "raw_llm_response": self.raw_llm_response,
            "llm_prompt": self.llm_prompt,
            "timestamp": self.timestamp,
        }


@dataclass
class BullBearAnalysisOutput:
    """
    Complete Bull-Bear analysis output for a portfolio

    Contains bull/bear debates and investment theses for all symbols.
    """

    portfolio_id: str
    symbols: List[str]

    # Debate results per symbol
    bull_arguments: Dict[str, BullArgument] = field(default_factory=dict)
    bear_arguments: Dict[str, BearArgument] = field(default_factory=dict)
    investment_theses: Dict[str, InvestmentThesis] = field(default_factory=dict)

    # Opik tracking
    total_debates: int = 0
    total_tokens_used: int = 0
    opik_project_name: str = "event-horizon"

    # Metadata
    execution_time_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "success"
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "portfolio_id": self.portfolio_id,
            "symbols": self.symbols,
            "bull_arguments": {k: v.__dict__ for k, v in self.bull_arguments.items()},
            "bear_arguments": {k: v.__dict__ for k, v in self.bear_arguments.items()},
            "investment_theses": {k: v.to_dict() for k, v in self.investment_theses.items()},
            "total_debates": self.total_debates,
            "total_tokens_used": self.total_tokens_used,
            "opik_project_name": self.opik_project_name,
            "execution_time_seconds": self.execution_time_seconds,
            "timestamp": self.timestamp,
            "status": self.status,
            "errors": self.errors,
        }
