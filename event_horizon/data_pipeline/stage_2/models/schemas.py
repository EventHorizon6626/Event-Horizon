"""
Stage 2 Output Schemas

Defines normalized, standardized data structures for Stage 2 output.
All heterogeneous Stage 1 data is transformed into a unified format.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NormalizedSymbolData:
    """
    Normalized data for a single symbol

    All data from Stage 1 (price, news, fundamentals, etc.)
    is unified into this single structure per symbol.
    """

    symbol: str

    # Price & Chart Data (normalized)
    price_data: Dict[str, Any] = field(default_factory=dict)
    # {
    #   "latest_price": float,
    #   "price_change_pct": float,
    #   "candles": List[dict],  # Standardized OHLCV
    #   "period": str,
    #   "interval": str
    # }

    # Technical Indicators (normalized)
    technical_indicators: Dict[str, Any] = field(default_factory=dict)
    # {
    #   "RSI": {"value": float, "signal": str, "text": str},
    #   "SMA": {...},
    #   "MACD": {...}
    # }

    # Fundamental Metrics (normalized)
    fundamentals: Dict[str, Any] = field(default_factory=dict)
    # {
    #   "valuation": {...},
    #   "profitability": {...},
    #   "financial_health": {...},
    #   "text_summary": str
    # }

    # News Data (normalized)
    news: Dict[str, Any] = field(default_factory=dict)
    # {
    #   "articles": List[dict],  # Standardized article format
    #   "total_count": int,
    #   "latest_timestamp": str
    # }

    # Earnings Data (normalized)
    earnings: Dict[str, Any] = field(default_factory=dict)
    # {
    #   "company_name": str,
    #   "security_type": str,
    #   "earnings_reports": {...},
    #   "financials": {...}
    # }

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    data_quality_score: float = 0.0  # 0-1, based on completeness
    has_errors: bool = False
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "price_data": self.price_data,
            "technical_indicators": self.technical_indicators,
            "fundamentals": self.fundamentals,
            "news": self.news,
            "earnings": self.earnings,
            "timestamp": self.timestamp,
            "data_quality_score": self.data_quality_score,
            "has_errors": self.has_errors,
            "errors": self.errors,
        }


@dataclass
class Stage2Output:
    """
    Complete Stage 2 output for a portfolio

    Contains normalized data for all symbols,
    ready for Stage 3 LLM feature extraction.
    """

    portfolio_id: str
    symbols: List[str]

    # Normalized data per symbol
    normalized_data: Dict[str, NormalizedSymbolData] = field(default_factory=dict)
    # Key: symbol, Value: NormalizedSymbolData

    # Metadata
    execution_time_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "success"  # success, partial_success, failed
    errors: List[Dict[str, Any]] = field(default_factory=list)

    # Quality metrics
    overall_quality_score: float = 0.0
    symbols_with_complete_data: List[str] = field(default_factory=list)
    symbols_with_partial_data: List[str] = field(default_factory=list)
    symbols_with_errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "portfolio_id": self.portfolio_id,
            "symbols": self.symbols,
            "normalized_data": {k: v.to_dict() for k, v in self.normalized_data.items()},
            "execution_time_seconds": self.execution_time_seconds,
            "timestamp": self.timestamp,
            "status": self.status,
            "errors": self.errors,
            "overall_quality_score": self.overall_quality_score,
            "symbols_with_complete_data": self.symbols_with_complete_data,
            "symbols_with_partial_data": self.symbols_with_partial_data,
            "symbols_with_errors": self.symbols_with_errors,
        }
