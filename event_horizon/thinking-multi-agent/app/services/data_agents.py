"""Data agent execution — runs EH Stage 1 agent classes."""

import asyncio
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

STAGE1_CONFIG = {
    "enabled_agents": ["candlestick", "earnings", "news", "technical", "fundamentals"],
    "max_workers": 5,
    "agent_configs": {
        "candlestick": {"period": "1mo", "interval": "1d"},
        "earnings": {"include_financials": True, "earnings_periods": 4},
        "news": {"max_articles_per_stock": 10, "days_back": 7},
        "technical": {"indicators": ["SMA", "RSI", "MACD"], "look_back_days": 30},
        "fundamentals": {"include_ratios": True, "include_financials": True},
    },
}


def _run_agent_sync(tool_name: str, stocks: List[str], **overrides) -> dict:
    """Instantiate and run a Stage 1 agent synchronously."""
    from event_horizon.data_pipeline.stage_1.agents.candlestick_agent import CandlestickAgent
    from event_horizon.data_pipeline.stage_1.agents.earnings_agent import EarningsAgent
    from event_horizon.data_pipeline.stage_1.agents.fundamentals_agent import FundamentalsAgent
    from event_horizon.data_pipeline.stage_1.agents.news_agent import NewsAgent
    from event_horizon.data_pipeline.stage_1.agents.technical_agent import TechnicalAgent

    config = {**STAGE1_CONFIG["agent_configs"].get(tool_name, {}), **overrides}

    agents = {
        "candlestick": CandlestickAgent,
        "earnings": EarningsAgent,
        "news": NewsAgent,
        "technical": TechnicalAgent,
        "fundamentals": FundamentalsAgent,
    }

    cls = agents.get(tool_name)
    if cls is None:
        return {"error": f"Unknown tool: {tool_name}"}

    agent = cls(config)
    return agent._execute_internal(stocks)


async def execute_tool(tool_name: str, stocks: List[str], **overrides) -> dict:
    """Execute a built-in data tool (async wrapper around sync agents)."""
    try:
        return await asyncio.to_thread(_run_agent_sync, tool_name, stocks, **overrides)
    except Exception as e:
        logger.error(f"Tool execution failed for {tool_name}: {e}")
        return {"error": str(e)}


def summarize_data(data: dict) -> str:
    """Concise summary of collected data for thinking context."""
    if not data:
        return "No data collected yet"
    labels = {
        "candlestick": "price data",
        "earnings": "earnings/financials data",
        "news": "news articles",
        "technical": "technical indicators",
        "fundamentals": "fundamental metrics",
    }
    lines = [f"- {k}: {labels.get(k, 'custom data')} available" for k in data]
    return "\n".join(lines) if lines else "No data collected yet"


def summarize_tool_result(tool_name: str, result: Any) -> str:
    """Concise summary of a single tool result."""
    if isinstance(result, dict):
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Retrieved {len(result)} items"
    return "Data retrieved successfully"
