"""Tavily + Exa news search client for Stage 1 data retrieval."""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)

SYMBOL_TO_COMPANY = {
    "AAPL": "Apple",
    "TSLA": "Tesla",
    "GOOGL": "Google Alphabet",
    "GOOG": "Google Alphabet",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "META": "Meta Facebook",
    "NVDA": "Nvidia",
    "NFLX": "Netflix",
    "AMD": "Advanced Micro Devices",
    "INTC": "Intel",
    "CRM": "Salesforce",
    "ORCL": "Oracle",
    "IBM": "IBM",
    "DIS": "Disney",
    "BA": "Boeing",
    "GE": "General Electric",
    "JPM": "JPMorgan Chase",
    "BAC": "Bank of America",
    "WMT": "Walmart",
    "QQQ": "Invesco QQQ Trust NASDAQ",
    "SPY": "SPDR S&P 500 ETF",
    "IWM": "iShares Russell 2000 ETF",
    "COIN": "Coinbase",
    "SQ": "Block Square",
    "PYPL": "PayPal",
    "V": "Visa",
    "MA": "Mastercard",
}


def _build_query(symbol: str) -> str:
    """Build a search query from a stock symbol."""
    company = SYMBOL_TO_COMPANY.get(symbol.upper(), symbol)
    if company == symbol:
        return f"{symbol} stock"
    return f"{symbol} OR {company} stock"


def tavily_news_search(symbol: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """Search news via Tavily API.

    Returns articles in the standard pipeline dict format.
    Raises on HTTP/network errors so callers can fall back.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY not set")

    query = _build_query(symbol)

    payload = {
        "api_key": api_key,
        "query": query,
        "topic": "news",
        "max_results": min(max_results, 20),
        "include_answer": False,
    }

    resp = requests.post("https://api.tavily.com/search", json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    logger.info(f"Tavily returned {len(results)} articles for {symbol}")

    return _format_tavily(symbol, results)


def _format_tavily(symbol: str, results: List[Dict]) -> List[Dict[str, Any]]:
    """Convert Tavily results to the standard article format."""
    now = datetime.now().isoformat()
    articles = []
    for r in results:
        if not r.get("title") or not r.get("url"):
            continue
        articles.append({
            "symbol": symbol,
            "title": r.get("title", ""),
            "description": r.get("content", "")[:500],
            "url": r.get("url", ""),
            "source": r.get("url", "").split("/")[2] if r.get("url") else "Unknown",
            "author": None,
            "published_at": r.get("published_date", ""),
            "image_url": None,
            "content": r.get("content", ""),
            "retrieved_at": now,
        })
    return articles


def exa_news_search(symbol: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """Search news via Exa API.

    Returns articles in the standard pipeline dict format.
    Raises on HTTP/network errors so callers can fall back.
    """
    api_key = os.getenv("EXASEARCH_API_KEY")
    if not api_key:
        raise RuntimeError("EXASEARCH_API_KEY not set")

    query = _build_query(symbol)

    payload = {
        "query": query,
        "category": "news",
        "numResults": min(max_results, 20),
        "contents": {
            "text": {"maxCharacters": 2000},
        },
    }
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    resp = requests.post(
        "https://api.exa.ai/search", json=payload, headers=headers, timeout=30
    )
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    logger.info(f"Exa returned {len(results)} articles for {symbol}")

    return _format_exa(symbol, results)


def _format_exa(symbol: str, results: List[Dict]) -> List[Dict[str, Any]]:
    """Convert Exa results to the standard article format."""
    now = datetime.now().isoformat()
    articles = []
    for r in results:
        if not r.get("title") or not r.get("url"):
            continue
        articles.append({
            "symbol": symbol,
            "title": r.get("title", ""),
            "description": (r.get("text") or "")[:500],
            "url": r.get("url", ""),
            "source": r.get("url", "").split("/")[2] if r.get("url") else "Unknown",
            "author": r.get("author"),
            "published_at": r.get("publishedDate", ""),
            "image_url": r.get("image"),
            "content": r.get("text", ""),
            "retrieved_at": now,
        })
    return articles
