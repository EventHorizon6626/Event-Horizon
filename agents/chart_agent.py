"""Chart Data Agent for Event Horizon - Fetches candlestick/OHLCV data"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from agents.base_agent import BaseAgent
from services.chart_data_client import ChartDataClient


class ChartDataAgent(BaseAgent):
    """Agent for retrieving candlestick chart data (OHLCV)"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Chart Data Agent

        Args:
            config: Configuration dictionary with optional keys:
                - period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
                - interval: Data interval (1m, 5m, 15m, 1h, 1d, 1wk, 1mo)
        """
        super().__init__("chart_agent", config)

        # Initialize Chart Data client
        self.chart_client = ChartDataClient()

        # Configuration
        self.period = self.get_config("period", "1mo")  # Default: 1 month
        self.interval = self.get_config("interval", "1d")  # Default: 1 day

        self.logger.info(
            f"Chart Agent configured: period={self.period}, interval={self.interval}"
        )

    def _execute_internal(self, input_data: Any) -> Dict[str, Any]:
        """
        Execute chart data retrieval for stocks

        Args:
            input_data: Either:
                - Dict with "symbols" key containing list of symbols
                - List of symbols directly

        Returns:
            Dict with:
                - chart_data: Dict mapping symbols to OHLCV data
                - period: Period used
                - interval: Interval used
                - total_symbols: Number of symbols processed
                - errors: List of errors encountered

        Raises:
            ValueError: If input format is invalid
        """
        # Parse input
        symbols = self._parse_input(input_data)

        if not symbols:
            raise ValueError("No symbols provided for chart data")

        self.logger.info(
            f"Fetching chart data for {len(symbols)} symbols: {symbols}"
        )
        self.logger.info(f"Period: {self.period}, Interval: {self.interval}")

        # Retrieve chart data for each symbol
        chart_data = {}
        errors = []

        for symbol in symbols:
            symbol = symbol.upper().strip()
            self.logger.info(f"Fetching chart data for {symbol}...")

            try:
                candles = self.chart_client.get_candle_data(
                    symbol=symbol,
                    period=self.period,
                    interval=self.interval
                )

                chart_data[symbol] = candles
                candle_count = len(candles.get("candles", []))
                self.logger.info(f"✓ Retrieved {candle_count} candles for {symbol}")

            except Exception as e:
                error_msg = f"Failed to fetch chart data for {symbol}: {str(e)}"
                self.logger.error(error_msg)
                errors.append({
                    "symbol": symbol,
                    "error": str(e)
                })
                chart_data[symbol] = {
                    "symbol": symbol,
                    "error": str(e),
                    "candles": []
                }

        # Determine overall status
        successful = len(chart_data) - len(errors)
        if successful == len(symbols):
            status = "success"
        elif successful > 0:
            status = "partial_success"
        else:
            status = "failed"

        return {
            "status": status,
            "chart_data": chart_data,
            "period": self.period,
            "interval": self.interval,
            "total_symbols": len(symbols),
            "successful": successful,
            "failed": len(errors),
            "errors": errors,
        }

    def _parse_input(self, input_data: Any) -> List[str]:
        """Parse input data to extract symbol list"""
        if isinstance(input_data, dict):
            return input_data.get("symbols", input_data.get("portfolio", []))
        elif isinstance(input_data, list):
            return input_data
        else:
            raise ValueError(
                f"Invalid input format. Expected dict or list, got {type(input_data)}"
            )
