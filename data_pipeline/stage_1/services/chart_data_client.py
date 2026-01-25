"""Chart Data Client for retrieving OHLCV candlestick data"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential


class ChartDataClient:
    """Client for fetching candlestick chart data using yfinance"""

    def __init__(self):
        """Initialize Chart Data Client"""
        self.logger = logging.getLogger("services.chart_data_client")
        self.logger.info("ChartDataClient initialized")

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
        Get OHLCV candlestick data for a symbol

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            period: Time period - 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max
            interval: Data interval - 1m, 5m, 15m, 1h, 1d, 1wk, 1mo

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
            f"Fetching candle data for {symbol} (period={period}, interval={interval})"
        )

        try:
            ticker = yf.Ticker(symbol)

            # Fetch historical data
            hist = ticker.history(period=period, interval=interval)

            if hist is None or hist.empty:
                raise ValueError(f"No data available for {symbol}")

            self.logger.info(f"Retrieved {len(hist)} candles for {symbol}")

            # Convert to list of candles
            candles = []
            for date, row in hist.iterrows():
                candle = {
                    "date": date.isoformat() if hasattr(date, "isoformat") else str(date),
                    "timestamp": int(date.timestamp() * 1000) if hasattr(date, "timestamp") else None,
                    "open": float(row["Open"]) if row["Open"] is not None else None,
                    "high": float(row["High"]) if row["High"] is not None else None,
                    "low": float(row["Low"]) if row["Low"] is not None else None,
                    "close": float(row["Close"]) if row["Close"] is not None else None,
                    "volume": int(row["Volume"]) if row["Volume"] is not None else None,
                }
                candles.append(candle)

            # Log sample data (first and last candle)
            if candles:
                first_candle = candles[0]
                last_candle = candles[-1]

                self.logger.info(
                    f"  First candle: {first_candle['date']} - "
                    f"O:{first_candle['open']:.2f} H:{first_candle['high']:.2f} "
                    f"L:{first_candle['low']:.2f} C:{first_candle['close']:.2f}"
                )
                self.logger.info(
                    f"  Last candle: {last_candle['date']} - "
                    f"O:{last_candle['open']:.2f} H:{last_candle['high']:.2f} "
                    f"L:{last_candle['low']:.2f} C:{last_candle['close']:.2f}"
                )

            result = {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "candles": candles,
                "total_candles": len(candles),
                "first_date": candles[0]["date"] if candles else None,
                "last_date": candles[-1]["date"] if candles else None,
            }

            # Log complete candle data
            self.logger.info(f"📊 CANDLE DATA ({symbol}):\n{json.dumps(result, indent=2)}")

            return result

        except Exception as e:
            self.logger.error(f"Failed to fetch candle data for {symbol}: {str(e)}")
            raise

    def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get latest price data (current candle)

        Args:
            symbol: Stock symbol

        Returns:
            Dict with latest price data or None
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "symbol": symbol,
                "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
                "previous_close": info.get("previousClose"),
                "open": info.get("open"),
                "high": info.get("dayHigh"),
                "low": info.get("dayLow"),
                "volume": info.get("volume"),
                "change": info.get("regularMarketChange"),
                "change_percent": info.get("regularMarketChangePercent"),
            }

        except Exception as e:
            self.logger.error(f"Failed to fetch latest price for {symbol}: {str(e)}")
            return None
