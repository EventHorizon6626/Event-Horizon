"""Massive.com Chart Data Client for OHLCV candlestick data"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential


class MassiveChartClient:
    """Client for fetching candlestick chart data from Massive.com API"""

    BASE_URL = "https://api.massive.com"

    # Timespan mappings
    TIMESPAN_MAP = {
        "1m": ("minute", 1),
        "5m": ("minute", 5),
        "15m": ("minute", 15),
        "30m": ("minute", 30),
        "1h": ("hour", 1),
        "4h": ("hour", 4),
        "1d": ("day", 1),
        "1wk": ("week", 1),
        "1mo": ("month", 1),
    }

    # Period to days mapping
    PERIOD_DAYS = {
        "1d": 1,
        "5d": 5,
        "1mo": 30,
        "3mo": 90,
        "6mo": 180,
        "1y": 365,
        "2y": 730,
        "5y": 1825,
        "max": 7300,  # ~20 years
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Massive Chart Client

        Args:
            api_key: Massive.com API key (or from MASSIVE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("MASSIVE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Massive.com API key required. Set MASSIVE_API_KEY environment variable "
                "or pass api_key parameter. Get your key at: https://massive.com/dashboard"
            )

        self.logger = logging.getLogger("services.massive_chart_client")
        self.logger.info("MassiveChartClient initialized")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def get_candle_data(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """
        Get OHLCV candlestick data from Massive.com

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL")
            period: Time period - 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max
            interval: Data interval - 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1wk, 1mo

        Returns:
            Dict containing:
                - symbol: Stock symbol
                - period: Period used
                - interval: Interval used
                - candles: List of OHLCV data
                - total_candles: Number of candles
                - first_date: First candle date
                - last_date: Last candle date

        Raises:
            Exception: If data retrieval fails
        """
        self.logger.info(
            f"Fetching candle data from Massive.com for {symbol} "
            f"(period={period}, interval={interval})"
        )

        try:
            # Parse interval
            if interval not in self.TIMESPAN_MAP:
                raise ValueError(
                    f"Invalid interval: {interval}. "
                    f"Valid options: {list(self.TIMESPAN_MAP.keys())}"
                )

            timespan, multiplier = self.TIMESPAN_MAP[interval]

            # Calculate date range
            to_date = datetime.now()
            days_back = self.PERIOD_DAYS.get(period, 30)
            from_date = to_date - timedelta(days=days_back)

            # Format dates as YYYY-MM-DD
            from_str = from_date.strftime("%Y-%m-%d")
            to_str = to_date.strftime("%Y-%m-%d")

            # Build API URL
            # Format: /v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}
            url = (
                f"{self.BASE_URL}/v2/aggs/ticker/{symbol.upper()}"
                f"/range/{multiplier}/{timespan}/{from_str}/{to_str}"
            )

            # Make request
            params = {
                "apiKey": self.api_key,
                "adjusted": "true",
                "sort": "asc",
                "limit": 50000
            }

            self.logger.info(f"Requesting: {url}")

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check response status
            if data.get("status") != "OK":
                raise ValueError(
                    f"API returned non-OK status: {data.get('status')} - "
                    f"{data.get('error', 'Unknown error')}"
                )

            results = data.get("results", [])

            if not results:
                raise ValueError(f"No data available for {symbol}")

            self.logger.info(f"Retrieved {len(results)} candles from Massive.com")

            # Convert to standard candle format
            candles = []
            for bar in results:
                candle = {
                    "date": datetime.fromtimestamp(bar["t"] / 1000).isoformat(),
                    "timestamp": bar["t"],  # Unix milliseconds
                    "open": float(bar["o"]),
                    "high": float(bar["h"]),
                    "low": float(bar["l"]),
                    "close": float(bar["c"]),
                    "volume": int(bar["v"]),
                    "vwap": float(bar.get("vw", 0)),  # Volume-weighted average price
                    "transactions": bar.get("n"),  # Number of transactions
                }
                candles.append(candle)

            # Log sample data (first and last candle)
            if candles:
                first_candle = candles[0]
                last_candle = candles[-1]

                self.logger.info(
                    f"  First candle: {first_candle['date']} - "
                    f"O:{first_candle['open']:.2f} H:{first_candle['high']:.2f} "
                    f"L:{first_candle['low']:.2f} C:{first_candle['close']:.2f} "
                    f"V:{first_candle['volume']:,}"
                )
                self.logger.info(
                    f"  Last candle: {last_candle['date']} - "
                    f"O:{last_candle['open']:.2f} H:{last_candle['high']:.2f} "
                    f"L:{last_candle['low']:.2f} C:{last_candle['close']:.2f} "
                    f"V:{last_candle['volume']:,}"
                )

            result = {
                "symbol": symbol.upper(),
                "period": period,
                "interval": interval,
                "candles": candles,
                "total_candles": len(candles),
                "first_date": candles[0]["date"] if candles else None,
                "last_date": candles[-1]["date"] if candles else None,
                "source": "massive.com"
            }

            # Log complete candle data
            self.logger.info(
                f"📊 MASSIVE.COM CANDLE DATA ({symbol}):\n"
                f"{json.dumps(result, indent=2)}"
            )

            return result

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                self.logger.error("Authentication failed - check your Massive.com API key")
                raise ValueError("Invalid Massive.com API key")
            elif e.response.status_code == 429:
                self.logger.error("Rate limit exceeded on Massive.com API")
                raise ValueError("Massive.com rate limit exceeded")
            else:
                self.logger.error(f"HTTP error from Massive.com: {e}")
                raise

        except Exception as e:
            self.logger.error(
                f"Failed to fetch candle data from Massive.com for {symbol}: {str(e)}"
            )
            raise

    def test_connection(self) -> bool:
        """
        Test if Massive.com API is working properly

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Test with a known symbol (AAPL) for 1 day
            result = self.get_candle_data("AAPL", period="5d", interval="1d")

            if result and result.get("total_candles", 0) > 0:
                self.logger.info("Massive.com API connection test successful")
                return True
            else:
                self.logger.error("Massive.com test failed: No data returned")
                return False

        except Exception as e:
            self.logger.error(f"Massive.com connection test failed: {str(e)}")
            return False
