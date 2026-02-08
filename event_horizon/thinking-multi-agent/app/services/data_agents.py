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
    logger.info("Running agent: tool=%s, stocks=%s", tool_name, stocks)
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
        logger.error("Unknown tool: %s", tool_name)
        return {"error": f"Unknown tool: {tool_name}"}

    agent = cls(config)
    result = agent._execute_internal(stocks)
    logger.info("Agent complete: tool=%s, result_keys=%s", tool_name, list(result.keys()) if isinstance(result, dict) else type(result).__name__)
    return result


async def execute_tool(tool_name: str, stocks: List[str], **overrides) -> dict:
    """Execute a data tool (built-in Stage 1 agent or web search)."""
    logger.info("Executing tool: %s, stocks=%s", tool_name, stocks)
    try:
        if tool_name == "web_search":
            from services.web_search import search_for_stocks

            topic = overrides.get("topic", "company history background")
            result = await search_for_stocks(stocks, topic)
        else:
            result = await asyncio.to_thread(_run_agent_sync, tool_name, stocks, **overrides)
        logger.info("Tool complete: %s, result_keys=%s", tool_name, list(result.keys()) if isinstance(result, dict) else type(result).__name__)
        return result
    except Exception as e:
        logger.error("Tool execution failed for %s: %s", tool_name, e)
        return {"error": str(e)}


def summarize_data(data: dict) -> str:
    """Concise summary of collected data for thinking context."""
    logger.debug("Summarizing data: keys=%s", list(data.keys()) if data else [])
    if not data:
        return "No data collected yet"
    labels = {
        "candlestick": "price data",
        "earnings": "earnings/financials data",
        "news": "news articles",
        "technical": "technical indicators",
        "fundamentals": "fundamental metrics",
        "web_search": "web search results",
    }
    lines = [f"- {k}: {labels.get(k, 'custom data')} available" for k in data]
    return "\n".join(lines) if lines else "No data collected yet"


def summarize_tool_result(tool_name: str, result: Any) -> str:
    """Concise summary of a single tool result."""
    logger.debug("Summarizing tool result: tool=%s", tool_name)
    if isinstance(result, dict):
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Retrieved {len(result)} items"
    return "Data retrieved successfully"
