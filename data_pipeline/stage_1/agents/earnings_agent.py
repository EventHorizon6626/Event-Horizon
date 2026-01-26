"""
Earnings Report Agent (Stage 1)

Retrieves financial reports and earnings data for stocks and ETFs.
Part of Stage 1: Data Retrieval - Fundamentals category.
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from core.base import BaseAgent
from data_pipeline.stage_1.services.financial_data_client import FinancialDataClient
from data_pipeline.stage_1.models.schemas import EarningsData


class EarningsAgent(BaseAgent):
    """
    Stage 1 Agent: Earnings and Financial Reports Retrieval

    Specialization: Fundamental data (earnings, financials, metrics)
    Data Sources: Yahoo Finance, Financial APIs
    Output Format: Raw financial reports, agent-specific format
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Earnings Agent

        Args:
            config: Configuration dictionary with optional keys:
                - include_financials: Include full financial statements (default: True)
                - earnings_periods: Number of quarters to retrieve (default: 4)
                - top_holdings: Number of top holdings for ETFs (default: 10)
        """
        super().__init__("earnings_agent", config)

        # Initialize Financial Data client
        try:
            self.financial_client = FinancialDataClient()
        except Exception as e:
            self.logger.error(f"Failed to initialize Financial Data client: {str(e)}")
            raise

        # Configuration
        self.include_financials = self.get_config("include_financials", True)
        self.earnings_periods = self.get_config("earnings_periods", 4)
        self.top_holdings = self.get_config("top_holdings", 10)

        self.logger.info(
            f"Earnings Agent configured: "
            f"include_financials={self.include_financials}, "
            f"earnings_periods={self.earnings_periods}, "
            f"top_holdings={self.top_holdings}"
        )

    def _execute_internal(self, input_data: Any) -> Dict[str, Any]:
        """
        Retrieve earnings and financial reports for portfolio

        Args:
            input_data: Either:
                - Dict with "symbols" or "portfolio" key
                - List of symbols directly

        Returns:
            Dict with:
                - earnings_data_by_symbol: Dict[symbol -> EarningsData]
                - total_symbols: Number processed
                - successful: Count of successful retrievals
                - securities_by_type: Count by security type
                - errors: List of errors
        """
        symbols, portfolio_id = self._parse_input(input_data)

        if not symbols:
            raise ValueError("No symbols provided for earnings data retrieval")

        self.logger.info(
            f"Retrieving earnings data for {len(symbols)} symbols: {symbols}"
        )

        earnings_data_by_symbol = {}
        errors = []
        successful = 0
        securities_by_type = {"stock": 0, "etf": 0, "mutual_fund": 0, "other": 0}

        for symbol in symbols:
            symbol = symbol.upper().strip()
            self.logger.info(f"Fetching earnings data for {symbol}...")

            try:
                # Get security info from financial client
                security_info = self.financial_client.get_security_info(symbol)

                sec_type = security_info.get("security_type", "other")
                reports = security_info.get("reports", {})

                # Create EarningsData object
                earnings_data = EarningsData(
                    symbol=symbol,
                    security_type=sec_type,
                    name=security_info.get("name"),
                    earnings_reports=reports.get("earnings") if reports else None,
                    financial_statements=reports.get("financials") if reports else None,
                    metrics=reports.get("metrics") if reports else None,
                    fund_info=reports.get("fund_info") if reports else None,
                    data_source="yahoo_finance",
                    retrieved_at=datetime.now().isoformat(),
                    error=None,
                )

                earnings_data_by_symbol[symbol] = earnings_data
                successful += 1

                # Count by type
                if sec_type in securities_by_type:
                    securities_by_type[sec_type] += 1
                else:
                    securities_by_type["other"] += 1

                self.logger.info(f"✓ Retrieved {sec_type} data for {symbol}")

            except Exception as e:
                error_msg = f"Failed to fetch earnings data for {symbol}: {str(e)}"
                self.logger.error(error_msg)

                errors.append({"symbol": symbol, "error": str(e)})

                # Add error entry
                earnings_data_by_symbol[symbol] = EarningsData(
                    symbol=symbol,
                    security_type="unknown",
                    name=None,
                    earnings_reports=None,
                    financial_statements=None,
                    metrics=None,
                    fund_info=None,
                    data_source="yahoo_finance",
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
            "earnings_data_by_symbol": earnings_data_by_symbol,
            "portfolio_id": portfolio_id,
            "total_symbols": total_symbols,
            "successful": successful,
            "failed": len(errors),
            "securities_by_type": securities_by_type,
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
