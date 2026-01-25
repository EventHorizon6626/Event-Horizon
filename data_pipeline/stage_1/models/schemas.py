"""
Stage 1 Output Schemas

Defines the data models for Stage 1 agent outputs.
Each agent returns raw, heterogeneous data in its own format.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NewsData:
    """Output schema for News Agent"""

    symbol: str
    articles: List[Dict[str, Any]] = field(default_factory=list)
    total_articles: int = 0
    data_source: str = "newsapi"
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


@dataclass
class EarningsData:
    """Output schema for Earnings/Report Agent"""

    symbol: str
    security_type: str  # stock, etf, mutual_fund
    name: Optional[str] = None
    earnings_reports: Optional[Dict[str, Any]] = None
    financial_statements: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    fund_info: Optional[Dict[str, Any]] = None  # For ETFs
    data_source: str = "yahoo_finance"
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


@dataclass
class ChartData:
    """Output schema for Chart/Candlestick Agent"""

    symbol: str
    candles: List[Dict[str, Any]] = field(default_factory=list)
    period: str = "1mo"
    interval: str = "1d"
    data_source: str = "yahoo_finance"
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


@dataclass
class OptionsFlowData:
    """Output schema for Options Flow Agent (Future)"""

    symbol: str
    options_chain: Optional[Dict[str, Any]] = None
    large_trades: List[Dict[str, Any]] = field(default_factory=list)
    unusual_activity: List[Dict[str, Any]] = field(default_factory=list)
    put_call_ratio: Optional[float] = None
    data_source: str = "options_api"
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


@dataclass
class SocialMediaData:
    """Output schema for Social Media Sentiment Agent (Future)"""

    symbol: str
    tweets: List[Dict[str, Any]] = field(default_factory=list)
    reddit_posts: List[Dict[str, Any]] = field(default_factory=list)
    total_mentions: int = 0
    sentiment_raw: Optional[Dict[str, Any]] = None
    data_source: str = "social_media"
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


@dataclass
class SECFilingsData:
    """Output schema for SEC Filings Agent (Future)"""

    symbol: str
    filings: List[Dict[str, Any]] = field(default_factory=list)
    filing_types: List[str] = field(default_factory=list)  # 10-K, 10-Q, 8-K, etc.
    data_source: str = "sec_edgar"
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


@dataclass
class TechnicalData:
    """Output schema for Technical Indicators Agent"""

    symbol: str
    indicators: Dict[str, str] = field(default_factory=dict)  # indicator_name -> result_text
    trade_date: str = ""
    look_back_days: int = 30
    data_source: str = "yfinance"
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


@dataclass
class FundamentalsData:
    """Output schema for Fundamentals Agent"""

    symbol: str
    fundamentals_text: str = ""
    data_source: str = "yfinance"
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


@dataclass
class Stage1Output:
    """
    Complete Stage 1 output for a portfolio

    Contains all heterogeneous data retrieved from various sources.
    Each field contains agent-specific formatted data.
    """

    portfolio_id: str
    symbols: List[str]

    # Data by agent type
    news_data: Dict[str, NewsData] = field(default_factory=dict)
    earnings_data: Dict[str, EarningsData] = field(default_factory=dict)
    chart_data: Dict[str, ChartData] = field(default_factory=dict)
    options_data: Dict[str, OptionsFlowData] = field(default_factory=dict)
    social_data: Dict[str, SocialMediaData] = field(default_factory=dict)
    sec_data: Dict[str, SECFilingsData] = field(default_factory=dict)
    technical_data: Dict[str, TechnicalData] = field(default_factory=dict)
    fundamentals_data: Dict[str, FundamentalsData] = field(default_factory=dict)

    # Metadata
    execution_time_seconds: float = 0.0
    agents_executed: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "success"  # success, partial_success, failed
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "portfolio_id": self.portfolio_id,
            "symbols": self.symbols,
            "news_data": {k: v.__dict__ for k, v in self.news_data.items()},
            "earnings_data": {k: v.__dict__ for k, v in self.earnings_data.items()},
            "chart_data": {k: v.__dict__ for k, v in self.chart_data.items()},
            "options_data": {k: v.__dict__ for k, v in self.options_data.items()},
            "social_data": {k: v.__dict__ for k, v in self.social_data.items()},
            "sec_data": {k: v.__dict__ for k, v in self.sec_data.items()},
            "technical_data": {k: v.__dict__ for k, v in self.technical_data.items()},
            "fundamentals_data": {k: v.__dict__ for k, v in self.fundamentals_data.items()},
            "execution_time_seconds": self.execution_time_seconds,
            "agents_executed": self.agents_executed,
            "timestamp": self.timestamp,
            "status": self.status,
            "errors": self.errors,
        }
