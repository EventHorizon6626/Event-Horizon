"""
Candlestick Data Agent (Stage 1)

Retrieves OHLCV (candlestick) price data for stocks.
Part of Stage 1: Data Retrieval - Price Data category.
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from core.base import BaseAgent
from data_pipeline.stage_1.services.chart_data_client import ChartDataClient
from data_pipeline.stage_1.services.massive_chart_client import MassiveChartClient
from data_pipeline.stage_1.models.schemas import ChartData
import os


class CandlestickAgent(BaseAgent):
    """
    Stage 1 Agent: Candlestick/OHLCV Data Retrieval

    Specialization: Price data (Open, High, Low, Close, Volume)
    Data Sources: Yahoo Finance or Massive.com API
    Output Format: Raw OHLCV candles, agent-specific format
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Candlestick Agent

        Args:
            config: Configuration dictionary with optional keys:
                - period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
                - interval: Data interval (1m, 5m, 15m, 1h, 1d, 1wk, 1mo)
                - data_source: 'yahoo' or 'massive' (defaults to env var)
        """
        super().__init__("candlestick_agent", config)

        # Determine which chart client to use
        use_massive = self.get_config(
            "data_source", os.getenv("USE_MASSIVE_API", "false")
        ).lower() in ["true", "massive"]

        if use_massive:
            self.logger.info("Using Massive.com API for candlestick data")
            self.chart_client = MassiveChartClient()
            self.data_source = "massive.com"
        else:
            self.logger.info("Using Yahoo Finance for candlestick data")
            self.chart_client = ChartDataClient()
            self.data_source = "yahoo_finance"

        # Configuration
        self.period = self.get_config("period", "1mo")
        self.interval = self.get_config("interval", "1d")

        self.logger.info(
            f"Candlestick Agent configured: "
            f"period={self.period}, interval={self.interval}, "
            f"source={self.data_source}"
        )

    def _execute_internal(self, input_data: Any) -> Dict[str, Any]:
        """
        Retrieve candlestick data for portfolio symbols

        Args:
            input_data: Either:
                - Dict with "symbols" or "portfolio" key
                - List of symbols directly

        Returns:
            Dict with:
                - chart_data_by_symbol: Dict[symbol -> ChartData]
                - period: Period used
                - interval: Interval used
                - total_symbols: Number processed
                - successful: Count of successful retrievals
                - errors: List of errors
        """
        symbols = self._parse_input(input_data)

        if not symbols:
            raise ValueError("No symbols provided for candlestick data retrieval")

        self.logger.info(
            f"Retrieving candlestick data for {len(symbols)} symbols: {symbols}"
        )
        self.logger.info(f"Parameters: period={self.period}, interval={self.interval}")

        chart_data_by_symbol = {}
        errors = []
        successful = 0

        for symbol in symbols:
            symbol = symbol.upper().strip()
            self.logger.info(f"Fetching candlestick data for {symbol}...")

            try:
                candles = self.chart_client.get_candle_data(
                    symbol=symbol, period=self.period, interval=self.interval
                )

                # Create ChartData object
                chart_data = ChartData(
                    symbol=symbol,
                    candles=candles.get("candles", []),
                    period=self.period,
                    interval=self.interval,
                    data_source=self.data_source,
                    retrieved_at=datetime.now().isoformat(),
                    error=None,
                )

                chart_data_by_symbol[symbol] = chart_data
                successful += 1

                candle_count = len(chart_data.candles)
                self.logger.info(f"✓ Retrieved {candle_count} candles for {symbol}")

            except Exception as e:
                error_msg = f"Failed to fetch candlestick data for {symbol}: {str(e)}"
                self.logger.error(error_msg)

                errors.append({"symbol": symbol, "error": str(e)})

                # Add error entry
                chart_data_by_symbol[symbol] = ChartData(
                    symbol=symbol,
                    candles=[],
                    period=self.period,
                    interval=self.interval,
                    data_source=self.data_source,
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
            "chart_data_by_symbol": chart_data_by_symbol,
            "period": self.period,
            "interval": self.interval,
            "total_symbols": total_symbols,
            "successful": successful,
            "failed": len(errors),
            "errors": errors,
        }

    def _parse_input(self, input_data: Any) -> List[str]:
        """Parse input to extract symbol list"""
        if isinstance(input_data, dict):
            symbols = input_data.get("symbols", input_data.get("portfolio", []))
        elif isinstance(input_data, list):
            symbols = input_data
        else:
            raise ValueError(
                f"Invalid input format. Expected dict or list, got {type(input_data)}"
            )

        # Clean symbols
        return [s.upper().strip() for s in symbols if isinstance(s, str) and s.strip()]
