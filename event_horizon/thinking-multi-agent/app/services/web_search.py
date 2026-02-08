"""Web search service — Tavily API wrapper for non-market data retrieval."""

import logging
import os
from datetime import datetime

import httpx

from event_horizon.data_pipeline.stage_1.models.schemas import WebSearchData

logger = logging.getLogger(__name__)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
EXASEARCH_API_KEY = os.getenv("EXASEARCH_API_KEY")


async def web_search(query: str, max_results: int = 5) -> dict:
    """Search the web using Tavily API (falls back to Exa)."""
    if TAVILY_API_KEY:
        return await _tavily_search(query, max_results)
    if EXASEARCH_API_KEY:
        return await _exa_search(query, max_results)
    return {"error": "No search API key configured (set TAVILY_API_KEY or EXASEARCH_API_KEY)"}


async def _tavily_search(query: str, max_results: int) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": max_results,
                "include_answer": True,
            },
        )
        resp.raise_for_status()
        return resp.json()


async def _exa_search(query: str, max_results: int) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": EXASEARCH_API_KEY, "Content-Type": "application/json"},
            json={
                "query": query,
                "num_results": max_results,
                "use_autoprompt": True,
            },
        )
        resp.raise_for_status()
        return resp.json()


async def search_for_stocks(stocks: list[str], topic: str = "general") -> dict:
    """Search web for each stock symbol on a topic, return WebSearchData keyed by symbol."""
    results = {}
    for symbol in stocks:
        query = f"{symbol} {topic}"
        try:
            data = await web_search(query)
            if "error" in data:
                ws = WebSearchData(symbol=symbol, query=query, error=data["error"])
            else:
                ws = WebSearchData(
                    symbol=symbol,
                    query=query,
                    answer=data.get("answer", ""),
                    results=data.get("results", []),
                    data_source="tavily" if TAVILY_API_KEY else "exa",
                    retrieved_at=datetime.now().isoformat(),
                )
            results[symbol] = ws
        except Exception as e:
            logger.error(f"Web search failed for {symbol}: {e}")
            results[symbol] = WebSearchData(symbol=symbol, query=query, error=str(e))
    return {"status": "success", "web_search_data_by_symbol": results}
