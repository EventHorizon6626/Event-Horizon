"""
Technical Indicators Agent (Stage 1)

Retrieves and calculates technical indicators for stocks.
Part of Stage 1: Data Retrieval - Technical Analysis category.
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from event_horizon.core.base import BaseAgent
from event_horizon.data_pipeline.stage_1.agents.utils.stock_tools import get_indicators
from event_horizon.data_pipeline.stage_1.models.schemas import TechnicalData


class TechnicalAgent(BaseAgent):
    """
    Stage 1 Agent: Technical Indicators Retrieval

    Specialization: Technical indicators (SMA, EMA, RSI, MACD)
    Data Sources: Yahoo Finance via yfinance
    Output Format: Raw technical indicator data
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Technical Agent

        Args:
            config: Configuration dictionary with optional keys:
                - indicators: List of indicators to calculate (default: ["SMA", "EMA", "RSI", "MACD"])
                - look_back_days: Days to look back (default: 30)
                - trade_date: Current trading date (default: today)
        """
        super().__init__("technical_agent", config)

        # Configuration
        self.indicators = self.get_config("indicators", ["SMA", "EMA", "RSI", "MACD"])
        self.look_back_days = self.get_config("look_back_days", 30)
        self.trade_date = self.get_config("trade_date", datetime.now().strftime("%Y-%m-%d"))

        self.logger.info(
            f"Technical Agent configured: "
            f"indicators={self.indicators}, "
            f"look_back_days={self.look_back_days}, "
            f"trade_date={self.trade_date}"
        )

    def _execute_internal(self, input_data: Any) -> Dict[str, Any]:
        """
        Retrieve technical indicators for portfolio symbols

        Args:
            input_data: Either:
                - Dict with "symbols" or "portfolio" key
                - List of symbols directly

        Returns:
            Dict with:
                - technical_data_by_symbol: Dict[symbol -> TechnicalData]
                - indicators: List of indicators calculated
                - total_symbols: Number of symbols processed
                - successful: Count of successful retrievals
                - errors: List of errors
        """
        symbols, portfolio_id = self._parse_input(input_data)

        if not symbols:
            raise ValueError("No symbols provided for technical indicators retrieval")

        self.logger.info(
            f"Retrieving technical indicators for {len(symbols)} symbols: {symbols}"
        )
        self.logger.info(f"Indicators: {self.indicators}")

        technical_data_by_symbol = {}
        errors = []
        successful = 0

        for symbol in symbols:
            symbol = symbol.upper().strip()
            self.logger.info(f"Calculating technical indicators for {symbol}...")

            try:
                # Fetch all requested indicators
                indicator_results = {}

                for indicator in self.indicators:
                    try:
                        result = get_indicators(
                            symbol=symbol,
                            indicator=indicator,
                            curr_date=self.trade_date,
                            look_back_days=self.look_back_days,
                        )
                        indicator_results[indicator] = result

                    except Exception as e:
                        self.logger.error(
                            f"Failed to calculate {indicator} for {symbol}: {str(e)}"
                        )
                        indicator_results[indicator] = f"Error: {str(e)}"

                # Create TechnicalData object
                technical_data = TechnicalData(
                    symbol=symbol,
                    indicators=indicator_results,
                    trade_date=self.trade_date,
                    look_back_days=self.look_back_days,
                    data_source="yfinance",
                    retrieved_at=datetime.now().isoformat(),
                    error=None,
                )

                technical_data_by_symbol[symbol] = technical_data
                successful += 1

                self.logger.info(
                    f"✓ Calculated {len(self.indicators)} indicators for {symbol}"
                )

            except Exception as e:
                error_msg = f"Failed to fetch technical data for {symbol}: {str(e)}"
                self.logger.error(error_msg)

                errors.append({"symbol": symbol, "error": str(e)})

                # Add error entry
                technical_data_by_symbol[symbol] = TechnicalData(
                    symbol=symbol,
                    indicators={},
                    trade_date=self.trade_date,
                    look_back_days=self.look_back_days,
                    data_source="yfinance",
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
            "technical_data_by_symbol": technical_data_by_symbol,
            "portfolio_id": portfolio_id,
            "indicators": self.indicators,
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
