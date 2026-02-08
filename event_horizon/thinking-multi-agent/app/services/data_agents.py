"""Data agent execution — runs EH Stage 1 agent classes."""

import asyncio
import json
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
    logger.info("Running agent: tool=%s, stocks=%s, overrides=%s", tool_name, stocks, overrides)
    from event_horizon.data_pipeline.stage_1.agents.candlestick_agent import CandlestickAgent
    from event_horizon.data_pipeline.stage_1.agents.earnings_agent import EarningsAgent
    from event_horizon.data_pipeline.stage_1.agents.fundamentals_agent import FundamentalsAgent
    from event_horizon.data_pipeline.stage_1.agents.news_agent import NewsAgent
    from event_horizon.data_pipeline.stage_1.agents.technical_agent import TechnicalAgent

    config = {**STAGE1_CONFIG["agent_configs"].get(tool_name, {}), **overrides}
    logger.info("Agent config for %s: %s", tool_name, config)

    agents = {
        "candlestick": CandlestickAgent,
        "earnings": EarningsAgent,
        "news": NewsAgent,
        "technical": TechnicalAgent,
        "fundamentals": FundamentalsAgent,
    }

    cls = agents.get(tool_name)
    if cls is None:
        logger.error("Unknown tool: %s (available: %s)", tool_name, list(agents.keys()))
        return {"error": f"Unknown tool: {tool_name}"}

    agent = cls(config)
    logger.info("Agent %s instantiated, executing for stocks=%s", tool_name, stocks)
    result = agent._execute_internal(stocks)

    result_keys = list(result.keys()) if isinstance(result, dict) else type(result).__name__
    result_json = json.dumps(result, indent=2, default=str)
    logger.info(
        "Agent complete: tool=%s, result_keys=%s, result_len=%d",
        tool_name, result_keys, len(result_json),
    )
    logger.debug("Agent %s full result:\n%s", tool_name, result_json[:5000])
    return result


async def execute_tool(tool_name: str, stocks: List[str], **overrides) -> dict:
    """Execute a data tool (built-in Stage 1 agent or web search)."""
    logger.info("=== EXECUTE TOOL === tool=%s, stocks=%s, overrides=%s", tool_name, stocks, overrides)
    try:
        if tool_name == "web_search":
            from services.web_search import search_for_stocks

            topic = overrides.get("topic", "company history background")
            logger.info("Executing web_search: stocks=%s, topic=%s", stocks, topic)
            result = await search_for_stocks(stocks, topic)
        else:
            result = await asyncio.to_thread(_run_agent_sync, tool_name, stocks, **overrides)

        result_keys = list(result.keys()) if isinstance(result, dict) else type(result).__name__
        result_json = json.dumps(result, indent=2, default=str)
        logger.info(
            "Tool complete: tool=%s, result_keys=%s, result_len=%d",
            tool_name, result_keys, len(result_json),
        )
        logger.debug("Tool %s full result:\n%s", tool_name, result_json[:5000])
        return result
    except Exception as e:
        logger.error("Tool execution failed for %s: %s", tool_name, e, exc_info=True)
        return {"error": str(e)}


def summarize_data(data: dict) -> str:
    """Concise summary of collected data for thinking context."""
    if not data:
        logger.info("summarize_data: no data collected yet")
        return "No data collected yet"

    labels = {
        "candlestick": "price data",
        "earnings": "earnings/financials data",
        "news": "news articles",
        "technical": "technical indicators",
        "fundamentals": "fundamental metrics",
        "web_search": "web search results",
    }
    lines = []
    for k in data:
        label = labels.get(k, "custom data")
        data_size = len(json.dumps(data[k], default=str)) if data[k] else 0
        lines.append(f"- {k}: {label} available (size={data_size} chars)")
    summary = "\n".join(lines)
    logger.info("summarize_data: keys=%s\n%s", list(data.keys()), summary)
    return summary


def summarize_tool_result(tool_name: str, result: Any) -> str:
    """Concise summary of a single tool result."""
    if isinstance(result, dict):
        if "error" in result:
            summary = f"Error: {result['error']}"
        else:
            result_len = len(json.dumps(result, default=str))
            summary = f"Retrieved {len(result)} items (total {result_len} chars)"
    else:
        summary = "Data retrieved successfully"
    logger.info("summarize_tool_result: tool=%s — %s", tool_name, summary)
    return summary
