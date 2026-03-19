"""
Fundamentals Analysis Agent (Stage 1)

Retrieves fundamental data and financial metrics for stocks.
Part of Stage 1: Data Retrieval - Fundamental Data category.
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from event_horizon.core.base import BaseAgent
from event_horizon.data_pipeline.stage_1.agents.utils.stock_tools import get_fundamentals
from event_horizon.data_pipeline.stage_1.models.schemas import FundamentalsData


class FundamentalsAgent(BaseAgent):
    """
    Stage 1 Agent: Fundamental Data Retrieval

    Specialization: Company fundamentals, financial metrics, valuation ratios
    Data Sources: Yahoo Finance via yfinance
    Output Format: Raw fundamental data
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Fundamentals Agent

        Args:
            config: Configuration dictionary with optional keys:
                - include_ratios: Include valuation ratios (default: True)
                - include_financials: Include financial health metrics (default: True)
        """
        super().__init__("fundamentals_agent", config)

        # Configuration
        self.include_ratios = self.get_config("include_ratios", True)
        self.include_financials = self.get_config("include_financials", True)

        self.logger.info(
            f"Fundamentals Agent configured: "
            f"include_ratios={self.include_ratios}, "
            f"include_financials={self.include_financials}"
        )

    def _execute_internal(self, input_data: Any) -> Dict[str, Any]:
        """
        Retrieve fundamental data for portfolio symbols

        Args:
            input_data: Either:
                - Dict with "symbols" or "portfolio" key
                - List of symbols directly

        Returns:
            Dict with:
                - fundamentals_data_by_symbol: Dict[symbol -> FundamentalsData]
                - total_symbols: Number of symbols processed
                - successful: Count of successful retrievals
                - errors: List of errors
        """
        symbols, portfolio_id = self._parse_input(input_data)

        if not symbols:
            raise ValueError("No symbols provided for fundamentals retrieval")

        self.logger.info(
            f"Retrieving fundamental data for {len(symbols)} symbols: {symbols}"
        )

        fundamentals_data_by_symbol = {}
        errors = []
        successful = 0

        for symbol in symbols:
            symbol = symbol.upper().strip()
            self.logger.info(f"Fetching fundamentals for {symbol}...")

            try:
                # Fetch fundamental data
                fundamentals_text = get_fundamentals(symbol)

                # Create FundamentalsData object
                fundamentals_data = FundamentalsData(
                    symbol=symbol,
                    fundamentals_text=fundamentals_text,
                    data_source="yfinance",
                    retrieved_at=datetime.now().isoformat(),
                    error=None if "Error" not in fundamentals_text else fundamentals_text,
                )

                fundamentals_data_by_symbol[symbol] = fundamentals_data
                successful += 1

                self.logger.info(f"✓ Retrieved fundamentals for {symbol}")

            except Exception as e:
                error_msg = f"Failed to fetch fundamentals for {symbol}: {str(e)}"
                self.logger.error(error_msg)

                errors.append({"symbol": symbol, "error": str(e)})

                # Add error entry
                fundamentals_data_by_symbol[symbol] = FundamentalsData(
                    symbol=symbol,
                    fundamentals_text="",
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
            "fundamentals_data_by_symbol": fundamentals_data_by_symbol,
            "portfolio_id": portfolio_id,
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
