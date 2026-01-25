"""News API Client for retrieving financial news"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests
from tenacity import retry, stop_after_attempt, wait_exponential


class NewsAPIClient:
    """Client for fetching news from NewsAPI.org"""

    # Mapping of common stock symbols to company names for better search
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
    }

    def __init__(self, api_key: str = None):
        """
        Initialize News API client

        Args:
            api_key: NewsAPI.org API key (or set NEWS_API_KEY env var)

        Raises:
            ValueError: If API key not provided
        """
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
        self.logger = logging.getLogger("services.news_api_client")

        if not self.api_key:
            raise ValueError(
                "NEWS_API_KEY not found. Set environment variable or pass api_key parameter.\n"
                "Get your free API key at: https://newsapi.org/"
            )

        self.logger.info("NewsAPIClient initialized")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def get_stock_news(
        self,
        symbol: str,
        days_back: int = 7,
        max_articles: int = 20,
        language: str = "en",
    ) -> List[Dict[str, Any]]:
        """
        Fetch news for a specific stock symbol

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            days_back: Number of days to look back (default: 7)
            max_articles: Maximum number of articles to return (default: 20)
            language: Language code (default: "en")

        Returns:
            List of news articles with metadata

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        self.logger.info(
            f"Fetching news for {symbol} (last {days_back} days, max {max_articles} articles)"
        )

        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)

        # Build query - search for both symbol and company name
        company_name = self._get_company_name(symbol)
        query = f"{symbol} OR {company_name}" if company_name != symbol else symbol

        params = {
            "q": query,
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d"),
            "language": language,
            "sortBy": "publishedAt",
            "pageSize": min(max_articles, 100),  # API max is 100
            "apiKey": self.api_key,
        }

        try:
            response = requests.get(
                f"{self.base_url}/everything", params=params, timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if data.get("status") != "ok":
                error_message = data.get("message", "Unknown error")
                self.logger.error(f"NewsAPI error for {symbol}: {error_message}")

                # Check for rate limit error
                if "rate limit" in error_message.lower():
                    self.logger.warning(
                        "Rate limit reached. Consider upgrading your NewsAPI plan."
                    )

                return []

            articles = data.get("articles", [])
            self.logger.info(f"Retrieved {len(articles)} articles for {symbol}")

            return self._format_articles(symbol, articles)

        except requests.exceptions.Timeout:
            self.logger.error(f"Request timeout for {symbol}")
            return []
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch news for {symbol}: {str(e)}")
            raise

    def _format_articles(
        self, symbol: str, articles: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Format API response into standardized structure

        Args:
            symbol: Stock symbol
            articles: Raw articles from API

        Returns:
            List of formatted article dictionaries
        """
        formatted = []
        retrieved_time = datetime.now().isoformat()

        for article in articles:
            # Skip articles with missing critical data
            if not article.get("title") or not article.get("url"):
                continue

            formatted.append(
                {
                    "symbol": symbol,
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "author": article.get("author"),
                    "published_at": article.get("publishedAt", ""),
                    "image_url": article.get("urlToImage"),
                    "content": article.get("content", ""),
                    "retrieved_at": retrieved_time,
                }
            )

        return formatted

    def _get_company_name(self, symbol: str) -> str:
        """
        Map stock symbol to company name for better search results

        Args:
            symbol: Stock symbol

        Returns:
            Company name or symbol if not found
        """
        return self.SYMBOL_TO_COMPANY.get(symbol.upper(), symbol)

    def test_connection(self) -> bool:
        """
        Test if API key is valid and connection works

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/top-headlines",
                params={"country": "us", "pageSize": 1, "apiKey": self.api_key},
                timeout=10,
            )

            if response.status_code == 401:
                self.logger.error("Invalid API key")
                return False

            response.raise_for_status()
            data = response.json()

            if data.get("status") == "ok":
                self.logger.info("NewsAPI connection test successful")
                return True
            else:
                self.logger.error(f"NewsAPI test failed: {data.get('message')}")
                return False

        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
