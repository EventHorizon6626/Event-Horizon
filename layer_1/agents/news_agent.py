"""
News Analysis Agent (Layer 1)

Retrieves news articles about stocks.
Part of Layer 1: Data Retrieval - News & Media category.
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from core.base import BaseAgent
from services.news_api_client import NewsAPIClient
from layer_1.models.schemas import NewsData


class NewsAgent(BaseAgent):
    """
    Layer 1 Agent: News Articles Retrieval

    Specialization: News articles and headlines
    Data Sources: NewsAPI, financial news providers
    Output Format: Raw articles, agent-specific format
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize News Agent

        Args:
            config: Configuration dictionary with optional keys:
                - max_articles_per_stock: Max articles per stock (default: 20)
                - days_back: How many days back to search (default: 7)
                - language: News language (default: "en")
        """
        super().__init__("news_agent", config)

        # Initialize News API client
        try:
            self.news_client = NewsAPIClient()
        except ValueError as e:
            self.logger.error(f"Failed to initialize News API client: {str(e)}")
            raise

        # Configuration
        self.max_articles_per_stock = self.get_config("max_articles_per_stock", 20)
        self.days_back = self.get_config("days_back", 7)
        self.language = self.get_config("language", "en")

        self.logger.info(
            f"News Agent configured: "
            f"max_articles={self.max_articles_per_stock}, "
            f"days_back={self.days_back}, "
            f"language={self.language}"
        )

    def _execute_internal(self, input_data: Any) -> Dict[str, Any]:
        """
        Retrieve news articles for portfolio symbols

        Args:
            input_data: Either:
                - Dict with "symbols" or "portfolio" key
                - List of symbols directly

        Returns:
            Dict with:
                - news_data_by_symbol: Dict[symbol -> NewsData]
                - total_articles: Total articles retrieved
                - total_symbols: Number of symbols processed
                - successful: Count of successful retrievals
                - errors: List of errors
        """
        symbols, portfolio_id = self._parse_input(input_data)

        if not symbols:
            raise ValueError("No symbols provided for news retrieval")

        self.logger.info(f"Retrieving news for {len(symbols)} symbols: {symbols}")

        news_data_by_symbol = {}
        errors = []
        successful = 0
        total_articles = 0

        for symbol in symbols:
            symbol = symbol.upper().strip()
            self.logger.info(f"Fetching news for {symbol}...")

            try:
                articles = self.news_client.get_stock_news(
                    symbol=symbol,
                    days_back=self.days_back,
                    max_articles=self.max_articles_per_stock,
                )

                # Create NewsData object
                news_data = NewsData(
                    symbol=symbol,
                    articles=articles,
                    total_articles=len(articles),
                    data_source="newsapi",
                    retrieved_at=datetime.now().isoformat(),
                    error=None,
                )

                news_data_by_symbol[symbol] = news_data
                successful += 1
                total_articles += len(articles)

                self.logger.info(f"✓ Retrieved {len(articles)} articles for {symbol}")

            except Exception as e:
                error_msg = f"Failed to fetch news for {symbol}: {str(e)}"
                self.logger.error(error_msg)

                errors.append({"symbol": symbol, "error": str(e)})

                # Add error entry
                news_data_by_symbol[symbol] = NewsData(
                    symbol=symbol,
                    articles=[],
                    total_articles=0,
                    data_source="newsapi",
                    retrieved_at=datetime.now().isoformat(),
                    error=str(e),
                )

        # Determine status
        total_symbols = len(symbols)
        if successful == total_symbols:
            status = "success"
        elif successful > 0:
            status = "partial_success"
        else:
            status = "failed"

        return {
            "status": status,
            "news_data_by_symbol": news_data_by_symbol,
            "portfolio_id": portfolio_id,
            "total_articles": total_articles,
            "total_symbols": total_symbols,
            "successful": successful,
            "failed": len(errors),
            "errors": errors,
        }

    def _parse_input(self, input_data: Any) -> tuple[List[str], str]:
        """Parse input to extract symbols and portfolio ID"""
        if isinstance(input_data, dict):
            symbols = input_data.get("symbols", input_data.get("portfolio", []))
            portfolio_id = input_data.get("portfolio_id", "unknown")
        elif isinstance(input_data, list):
            symbols = input_data
            portfolio_id = "unknown"
        else:
            raise ValueError(
                f"Invalid input format. Expected dict or list, got {type(input_data)}"
            )

        # Clean symbols
        cleaned = [s.upper().strip() for s in symbols if isinstance(s, str) and s.strip()]
        return cleaned, portfolio_id
