"""Event Horizon AI Agents

DEPRECATED: This module is kept for backward compatibility.
New code should use layer_1.agents instead.
"""

from .base_agent import BaseAgent
from .news_agent import NewsAgent
from .report_agent import ReportAnalysisAgent
from .chart_agent import ChartDataAgent

# Import Layer 1 agents for convenience
try:
    from layer_1.agents import (
        CandlestickAgent,
        EarningsAgent,
        NewsAgent as Layer1NewsAgent,
    )
except ImportError:
    pass

__all__ = ["BaseAgent", "NewsAgent", "ReportAnalysisAgent", "ChartDataAgent"]
