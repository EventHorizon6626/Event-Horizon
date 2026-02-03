"""
Stage 3 Output Schemas

Defines LLM-extracted features and insights from normalized data.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SymbolFeatures:
    """
    LLM-extracted features for a single symbol

    Contains insights, patterns, and structured features
    extracted by LLM from normalized Stage 2 data.
    """

    symbol: str

    # LLM-extracted insights
    market_sentiment: str = ""  # bullish, bearish, neutral
    sentiment_confidence: float = 0.0  # 0-1
    sentiment_reasoning: str = ""  # LLM explanation

    technical_signal: str = ""  # buy, sell, hold
    technical_confidence: float = 0.0
    technical_reasoning: str = ""

    fundamental_health: str = ""  # strong, moderate, weak
    fundamental_confidence: float = 0.0
    fundamental_reasoning: str = ""

    # Extracted patterns
    key_patterns: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)

    # News sentiment
    news_sentiment: str = ""  # positive, negative, neutral
    news_summary: str = ""

    # Structured feature vector (for ML models)
    feature_vector: Dict[str, float] = field(default_factory=dict)

    # Opik tracking metadata
    opik_trace_id: Optional[str] = None
    llm_model_used: str = ""
    total_tokens: int = 0
    extraction_time_seconds: float = 0.0

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    has_errors: bool = False
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "market_sentiment": self.market_sentiment,
            "sentiment_confidence": self.sentiment_confidence,
            "sentiment_reasoning": self.sentiment_reasoning,
            "technical_signal": self.technical_signal,
            "technical_confidence": self.technical_confidence,
            "technical_reasoning": self.technical_reasoning,
            "fundamental_health": self.fundamental_health,
            "fundamental_confidence": self.fundamental_confidence,
            "fundamental_reasoning": self.fundamental_reasoning,
            "key_patterns": self.key_patterns,
            "risk_factors": self.risk_factors,
            "opportunities": self.opportunities,
            "news_sentiment": self.news_sentiment,
            "news_summary": self.news_summary,
            "feature_vector": self.feature_vector,
            "opik_trace_id": self.opik_trace_id,
            "llm_model_used": self.llm_model_used,
            "total_tokens": self.total_tokens,
            "extraction_time_seconds": self.extraction_time_seconds,
            "timestamp": self.timestamp,
            "has_errors": self.has_errors,
            "errors": self.errors,
        }


@dataclass
class Stage3Output:
    """
    Complete Stage 3 output for a portfolio

    Contains LLM-extracted features for all symbols,
    ready for analyzer system (decision-making teams).
    """

    portfolio_id: str
    symbols: List[str]

    # Features per symbol
    symbol_features: Dict[str, SymbolFeatures] = field(default_factory=dict)
    # Key: symbol, Value: SymbolFeatures

    # Opik tracking
    total_llm_calls: int = 0
    total_tokens_used: int = 0
    average_extraction_time: float = 0.0
    opik_project_name: str = "event-horizon"

    # Metadata
    execution_time_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "success"  # success, partial_success, failed
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "portfolio_id": self.portfolio_id,
            "symbols": self.symbols,
            "symbol_features": {k: v.to_dict() for k, v in self.symbol_features.items()},
            "total_llm_calls": self.total_llm_calls,
            "total_tokens_used": self.total_tokens_used,
            "average_extraction_time": self.average_extraction_time,
            "opik_project_name": self.opik_project_name,
            "execution_time_seconds": self.execution_time_seconds,
            "timestamp": self.timestamp,
            "status": self.status,
            "errors": self.errors,
        }
