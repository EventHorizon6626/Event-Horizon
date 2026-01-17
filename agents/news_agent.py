x"""News Analysis Agent for Event Horizon"""

import logging
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from services.news_api_client import NewsAPIClient


class NewsAgent(BaseAgent):
    """Agent for retrieving financial news about portfolio stocks"""

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
        Execute news retrieval for portfolio stocks

        Args:
            input_data: Either:
                - Dict with "portfolio" key containing list of stock symbols
                - List of stock symbols directly

        Returns:
            Dict with:
                - portfolio_id: Portfolio identifier
                - status: Overall status (success/partial_success/failed)
                - news_by_stock: Dict mapping symbols to article lists
                - total_articles: Total number of articles retrieved
                - errors: List of errors encountered
                - stocks_processed: Number of stocks processed
                - stocks_with_errors: Number of stocks that had errors

        Raises:
            ValueError: If input format is invalid or portfolio is empty
        """
        # Parse input
        stocks, portfolio_id = self._parse_input(input_data)

        if not stocks:
            raise ValueError("Portfolio is empty - no stocks to analyze")

        self.logger.info(
            f"Processing portfolio {portfolio_id} with {len(stocks)} stocks: {stocks}"
        )

        # Retrieve news for each stock
        news_by_stock = {}
        errors = []
        total_articles = 0

        for symbol in stocks:
            symbol = symbol.upper().strip()
            self.logger.info(f"Fetching news for {symbol}...")

            try:
                articles = self.news_client.get_stock_news(
                    symbol=symbol,
                    days_back=self.days_back,
                    max_articles=self.max_articles_per_stock,
                )

                news_by_stock[symbol] = articles
                total_articles += len(articles)

                self.logger.info(f"✓ Retrieved {len(articles)} articles for {symbol}")

            except Exception as e:
                error_msg = f"Failed to fetch news for {symbol}: {str(e)}"
                self.logger.error(error_msg)

                errors.append(
                    {"symbol": symbol, "error": str(e), "error_type": type(e).__name__}
                )

                # Add empty list for failed stock
                news_by_stock[symbol] = []

        # Determine overall status
        if len(errors) == len(stocks):
            status = "failed"
            self.logger.error("All stocks failed to fetch news")
        elif errors:
            status = "partial_success"
            self.logger.warning(
                f"Partial success: {len(errors)}/{len(stocks)} stocks had errors"
            )
        else:
            status = "success"
            self.logger.info(
                f"Successfully retrieved news for all {len(stocks)} stocks"
            )

        # Build result
        result = {
            "portfolio_id": portfolio_id,
            "status": status,
            "news_by_stock": news_by_stock,
            "total_articles": total_articles,
            "errors": errors,
            "stocks_processed": len(stocks),
            "stocks_with_errors": len(errors),
            "config_used": {
                "max_articles_per_stock": self.max_articles_per_stock,
                "days_back": self.days_back,
                "language": self.language,
            },
        }

        return result

    def _parse_input(self, input_data: Any) -> tuple[List[str], str]:
        """
        Parse input data to extract portfolio and ID

        Args:
            input_data: Input in various formats

        Returns:
            Tuple of (stock_list, portfolio_id)

        Raises:
            ValueError: If input format is invalid
        """
        if isinstance(input_data, dict):
            stocks = input_data.get("portfolio", input_data.get("stocks", []))
            portfolio_id = input_data.get("portfolio_id", "unknown")
        elif isinstance(input_data, list):
            stocks = input_data
            portfolio_id = "unknown"
        else:
            raise ValueError(
                "Input must be either:\n"
                "  - Dict with 'portfolio' or 'stocks' key containing list of symbols\n"
                "  - List of stock symbols directly"
            )

        # Validate stocks list
        if not isinstance(stocks, list):
            raise ValueError("Portfolio/stocks must be a list of stock symbols")

        # Clean and validate symbols
        cleaned_stocks = []
        for symbol in stocks:
            if isinstance(symbol, str) and symbol.strip():
                cleaned_stocks.append(symbol.strip().upper())
            else:
                self.logger.warning(f"Skipping invalid symbol: {symbol}")

        return cleaned_stocks, portfolio_id
