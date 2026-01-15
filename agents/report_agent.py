"""Report Analysis Agent for Event Horizon"""

import logging
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from services.financial_data_client import FinancialDataClient


class ReportAnalysisAgent(BaseAgent):
    """
    Agent for retrieving financial reports
    - Stocks: Earnings reports, financial statements
    - ETFs: Fund information, holdings, performance
    - Other: Equivalent financial disclosures
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Report Analysis Agent

        Args:
            config: Configuration dictionary with optional keys:
                - include_financials: Include full financial statements (default: True)
                - earnings_periods: Number of quarters to retrieve (default: 4)
                - top_holdings: Number of top holdings for ETFs (default: 10)
        """
        super().__init__("report_agent", config)

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
            f"Report Agent configured: "
            f"include_financials={self.include_financials}, "
            f"earnings_periods={self.earnings_periods}, "
            f"top_holdings={self.top_holdings}"
        )

    def _execute_internal(self, input_data: Any) -> Dict[str, Any]:
        """
        Execute report retrieval for portfolio securities

        Args:
            input_data: Either:
                - Dict with "portfolio" key containing list of symbols
                - List of symbols directly

        Returns:
            Dict with:
                - portfolio_id: Portfolio identifier
                - status: Overall status (success/partial_success/failed)
                - reports_by_symbol: Dict mapping symbols to report data
                - total_reports: Total number of reports retrieved
                - errors: List of errors encountered
                - stocks_processed: Number of symbols processed
                - securities_by_type: Count of each security type

        Raises:
            ValueError: If input format is invalid or portfolio is empty
        """
        # Parse input
        symbols, portfolio_id = self._parse_input(input_data)

        if not symbols:
            raise ValueError("Portfolio is empty - no symbols to analyze")

        self.logger.info(
            f"Processing portfolio {portfolio_id} with {len(symbols)} symbols: {symbols}"
        )

        # Retrieve reports for each symbol
        reports_by_symbol = {}
        errors = []
        total_reports = 0
        securities_by_type = {"stock": 0, "etf": 0, "mutual_fund": 0, "other": 0}

        for symbol in symbols:
            symbol = symbol.upper().strip()
            self.logger.info(f"Fetching reports for {symbol}...")

            try:
                security_info = self.financial_client.get_security_info(symbol)

                reports_by_symbol[symbol] = security_info
                total_reports += 1

                # Count by type
                sec_type = security_info.get("security_type", "other")
                if sec_type in securities_by_type:
                    securities_by_type[sec_type] += 1
                else:
                    securities_by_type["other"] += 1

                self.logger.info(f"✓ Retrieved {sec_type} reports for {symbol}")

            except Exception as e:
                error_msg = f"Failed to fetch reports for {symbol}: {str(e)}"
                self.logger.error(error_msg)

                errors.append(
                    {"symbol": symbol, "error": str(e), "error_type": type(e).__name__}
                )

                # Add empty entry for failed symbol
                reports_by_symbol[symbol] = {
                    "symbol": symbol,
                    "security_type": "unknown",
                    "name": None,
                    "reports": None,
                    "error": str(e),
                }

        # Determine overall status
        if len(errors) == len(symbols):
            status = "failed"
            self.logger.error("All symbols failed to fetch reports")
        elif errors:
            status = "partial_success"
            self.logger.warning(
                f"Partial success: {len(errors)}/{len(symbols)} symbols had errors"
            )
        else:
            status = "success"
            self.logger.info(
                f"Successfully retrieved reports for all {len(symbols)} symbols"
            )

        # Build result summary
        result = {
            "portfolio_id": portfolio_id,
            "status": status,
            "reports_by_symbol": reports_by_symbol,
            "total_reports": total_reports,
            "errors": errors,
            "stocks_processed": len(symbols),
            "stocks_with_errors": len(errors),
            "securities_by_type": securities_by_type,
            "summary": self._build_summary(reports_by_symbol, securities_by_type),
            "config_used": {
                "include_financials": self.include_financials,
                "earnings_periods": self.earnings_periods,
                "top_holdings": self.top_holdings,
            },
        }

        return result

    def _parse_input(self, input_data: Any) -> tuple[List[str], str]:
        """
        Parse input data to extract portfolio and ID

        Args:
            input_data: Input in various formats

        Returns:
            Tuple of (symbol_list, portfolio_id)

        Raises:
            ValueError: If input format is invalid
        """
        if isinstance(input_data, dict):
            symbols = input_data.get("portfolio", input_data.get("stocks", []))
            portfolio_id = input_data.get("portfolio_id", "unknown")
        elif isinstance(input_data, list):
            symbols = input_data
            portfolio_id = "unknown"
        else:
            raise ValueError(
                "Input must be either:\\n"
                "  - Dict with 'portfolio' or 'stocks' key containing list of symbols\\n"
                "  - List of symbols directly"
            )

        # Validate symbols list
        if not isinstance(symbols, list):
            raise ValueError("Portfolio/stocks must be a list of symbols")

        # Clean and validate symbols
        cleaned_symbols = []
        for symbol in symbols:
            if isinstance(symbol, str) and symbol.strip():
                cleaned_symbols.append(symbol.strip().upper())
            else:
                self.logger.warning(f"Skipping invalid symbol: {symbol}")

        return cleaned_symbols, portfolio_id

    def _build_summary(
        self, reports_by_symbol: Dict[str, Any], securities_by_type: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Build a summary of the portfolio reports

        Args:
            reports_by_symbol: All retrieved reports
            securities_by_type: Count of each security type

        Returns:
            Summary dict with key metrics
        """
        summary = {
            "total_securities": len(reports_by_symbol),
            "by_type": securities_by_type,
            "stocks": [],
            "etfs": [],
            "others": [],
        }

        for symbol, report in reports_by_symbol.items():
            if report.get("error"):
                continue

            sec_type = report.get("security_type")
            name = report.get("name", symbol)

            if sec_type == "stock":
                # Extract key stock metrics
                reports = report.get("reports", {})
                metrics = reports.get("metrics", {}) if reports else {}

                summary["stocks"].append(
                    {
                        "symbol": symbol,
                        "name": name,
                        "market_cap": metrics.get("market_cap"),
                        "pe_ratio": metrics.get("pe_ratio"),
                        "has_earnings": bool(
                            reports.get("earnings") if reports else False
                        ),
                    }
                )

            elif sec_type == "etf":
                # Extract key ETF metrics
                reports = report.get("reports", {})
                fund_info = reports.get("fund_info", {}) if reports else {}

                summary["etfs"].append(
                    {
                        "symbol": symbol,
                        "name": name,
                        "total_assets": fund_info.get("total_assets"),
                        "expense_ratio": fund_info.get("expense_ratio"),
                        "ytd_return": fund_info.get("ytd_return"),
                    }
                )

            else:
                summary["others"].append(
                    {"symbol": symbol, "name": name, "type": sec_type}
                )

        return summary
