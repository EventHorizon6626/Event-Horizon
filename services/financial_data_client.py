"""Financial Data Client for retrieving earnings and fund reports"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential


class FinancialDataClient:
    """Client for fetching financial reports using yfinance"""

    # Security type mappings
    STOCK_TYPES = {"EQUITY", "STOCK"}
    ETF_TYPES = {"ETF"}
    FUND_TYPES = {"MUTUALFUND"}

    def __init__(self):
        """Initialize Financial Data Client"""
        self.logger = logging.getLogger("services.financial_data_client")
        self.logger.info("FinancialDataClient initialized")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def get_security_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a security

        Args:
            symbol: Stock/ETF symbol (e.g., "AAPL", "SPY")

        Returns:
            Dict containing security info and reports

        Raises:
            Exception: If data retrieval fails
        """
        self.logger.info(f"Fetching security information for {symbol}")

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Check if symbol exists
            if not info or "symbol" not in info:
                raise ValueError(f"Symbol {symbol} not found or no data available")

            security_type = self._determine_security_type(info)
            self.logger.info(f"{symbol} identified as {security_type}")

            # Fetch appropriate reports based on type
            if security_type == "stock":
                reports = self._get_stock_reports(ticker, info)
            elif security_type == "etf":
                reports = self._get_etf_reports(ticker, info)
            else:
                reports = self._get_generic_reports(ticker, info)

            return {
                "symbol": symbol,
                "security_type": security_type,
                "name": info.get("longName", info.get("shortName", symbol)),
                "reports": reports,
                "retrieved_at": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
            raise

    def _determine_security_type(self, info: Dict) -> str:
        """
        Determine if security is stock, ETF, or other

        Args:
            info: Security info from yfinance

        Returns:
            'stock', 'etf', 'mutual_fund', or 'other'
        """
        quote_type = info.get("quoteType", "").upper()

        if quote_type in self.STOCK_TYPES:
            return "stock"
        elif quote_type in self.ETF_TYPES:
            return "etf"
        elif quote_type in self.FUND_TYPES:
            return "mutual_fund"
        else:
            self.logger.warning(
                f"Unknown quote type: {quote_type}, defaulting to 'other'"
            )
            return "other"

    def _get_stock_reports(self, ticker: yf.Ticker, info: Dict) -> Dict[str, Any]:
        """
        Fetch earnings and financial reports for stocks

        Args:
            ticker: yfinance Ticker object
            info: Basic security info

        Returns:
            Dict containing earnings, financials, and calendar data
        """
        reports = {}

        # Earnings data
        try:
            earnings_data = self._get_earnings_data(ticker)
            reports["earnings"] = earnings_data
        except Exception as e:
            self.logger.warning(f"Failed to fetch earnings: {str(e)}")
            reports["earnings"] = None

        # Earnings calendar (upcoming dates)
        try:
            calendar = ticker.calendar
            if calendar is not None and not calendar.empty:
                reports["calendar"] = {
                    "earnings_date": (
                        calendar.get("Earnings Date", [None])[0].isoformat()
                        if hasattr(
                            calendar.get("Earnings Date", [None])[0], "isoformat"
                        )
                        else str(calendar.get("Earnings Date", [None])[0])
                    ),
                    "earnings_estimate": (
                        float(calendar.get("Earnings Average", [0])[0])
                        if calendar.get("Earnings Average") is not None
                        else None
                    ),
                    "revenue_estimate": (
                        float(calendar.get("Revenue Average", [0])[0])
                        if calendar.get("Revenue Average") is not None
                        else None
                    ),
                }
            else:
                reports["calendar"] = None
        except Exception as e:
            self.logger.warning(f"Failed to fetch calendar: {str(e)}")
            reports["calendar"] = None

        # Financial statements
        try:
            financials = self._get_financial_statements(ticker)
            reports["financials"] = financials
        except Exception as e:
            self.logger.warning(f"Failed to fetch financials: {str(e)}")
            reports["financials"] = None

        # Key metrics from info
        reports["metrics"] = {
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "price_to_book": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
            "beta": info.get("beta"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        }

        return reports

    def _get_earnings_data(self, ticker: yf.Ticker) -> Dict[str, Any]:
        """
        Extract earnings history (quarterly and annual)

        Args:
            ticker: yfinance Ticker object

        Returns:
            Dict with quarterly and annual earnings
        """
        earnings = {}

        # Quarterly earnings
        try:
            quarterly = ticker.quarterly_earnings
            if quarterly is not None and not quarterly.empty:
                quarterly_list = []
                for date, row in quarterly.head(8).iterrows():  # Last 8 quarters
                    quarterly_list.append(
                        {
                            "date": (
                                date.isoformat()
                                if hasattr(date, "isoformat")
                                else str(date)
                            ),
                            "revenue": (
                                float(row.get("Revenue", 0))
                                if row.get("Revenue") is not None
                                else None
                            ),
                            "earnings": (
                                float(row.get("Earnings", 0))
                                if row.get("Earnings") is not None
                                else None
                            ),
                        }
                    )
                earnings["quarterly"] = quarterly_list
            else:
                earnings["quarterly"] = []
        except Exception as e:
            self.logger.warning(f"Failed to parse quarterly earnings: {str(e)}")
            earnings["quarterly"] = []

        # Annual earnings
        try:
            annual = ticker.earnings
            if annual is not None and not annual.empty:
                annual_list = []
                for date, row in annual.head(5).iterrows():  # Last 5 years
                    annual_list.append(
                        {
                            "year": str(date),
                            "revenue": (
                                float(row.get("Revenue", 0))
                                if row.get("Revenue") is not None
                                else None
                            ),
                            "earnings": (
                                float(row.get("Earnings", 0))
                                if row.get("Earnings") is not None
                                else None
                            ),
                        }
                    )
                earnings["annual"] = annual_list
            else:
                earnings["annual"] = []
        except Exception as e:
            self.logger.warning(f"Failed to parse annual earnings: {str(e)}")
            earnings["annual"] = []

        return earnings

    def _get_financial_statements(self, ticker: yf.Ticker) -> Dict[str, Any]:
        """
        Extract financial statements (income, balance sheet, cash flow)

        Args:
            ticker: yfinance Ticker object

        Returns:
            Dict with financial statements
        """
        financials = {}

        try:
            # Income statement (most recent)
            income_stmt = ticker.financials
            if income_stmt is not None and not income_stmt.empty:
                latest = income_stmt.iloc[:, 0]
                financials["income_statement"] = {
                    "date": (
                        income_stmt.columns[0].isoformat()
                        if hasattr(income_stmt.columns[0], "isoformat")
                        else str(income_stmt.columns[0])
                    ),
                    "total_revenue": (
                        float(latest.get("Total Revenue", 0))
                        if latest.get("Total Revenue") is not None
                        else None
                    ),
                    "gross_profit": (
                        float(latest.get("Gross Profit", 0))
                        if latest.get("Gross Profit") is not None
                        else None
                    ),
                    "operating_income": (
                        float(latest.get("Operating Income", 0))
                        if latest.get("Operating Income") is not None
                        else None
                    ),
                    "net_income": (
                        float(latest.get("Net Income", 0))
                        if latest.get("Net Income") is not None
                        else None
                    ),
                }
            else:
                financials["income_statement"] = None
        except Exception as e:
            self.logger.warning(f"Failed to parse income statement: {str(e)}")
            financials["income_statement"] = None

        try:
            # Balance sheet (most recent)
            balance_sheet = ticker.balance_sheet
            if balance_sheet is not None and not balance_sheet.empty:
                latest = balance_sheet.iloc[:, 0]
                financials["balance_sheet"] = {
                    "date": (
                        balance_sheet.columns[0].isoformat()
                        if hasattr(balance_sheet.columns[0], "isoformat")
                        else str(balance_sheet.columns[0])
                    ),
                    "total_assets": (
                        float(latest.get("Total Assets", 0))
                        if latest.get("Total Assets") is not None
                        else None
                    ),
                    "total_liabilities": (
                        float(latest.get("Total Liabilities Net Minority Interest", 0))
                        if latest.get("Total Liabilities Net Minority Interest")
                        is not None
                        else None
                    ),
                    "stockholder_equity": (
                        float(latest.get("Stockholders Equity", 0))
                        if latest.get("Stockholders Equity") is not None
                        else None
                    ),
                    "cash": (
                        float(latest.get("Cash And Cash Equivalents", 0))
                        if latest.get("Cash And Cash Equivalents") is not None
                        else None
                    ),
                }
            else:
                financials["balance_sheet"] = None
        except Exception as e:
            self.logger.warning(f"Failed to parse balance sheet: {str(e)}")
            financials["balance_sheet"] = None

        try:
            # Cash flow (most recent)
            cash_flow = ticker.cashflow
            if cash_flow is not None and not cash_flow.empty:
                latest = cash_flow.iloc[:, 0]
                financials["cash_flow"] = {
                    "date": (
                        cash_flow.columns[0].isoformat()
                        if hasattr(cash_flow.columns[0], "isoformat")
                        else str(cash_flow.columns[0])
                    ),
                    "operating_cash_flow": (
                        float(latest.get("Operating Cash Flow", 0))
                        if latest.get("Operating Cash Flow") is not None
                        else None
                    ),
                    "investing_cash_flow": (
                        float(latest.get("Investing Cash Flow", 0))
                        if latest.get("Investing Cash Flow") is not None
                        else None
                    ),
                    "financing_cash_flow": (
                        float(latest.get("Financing Cash Flow", 0))
                        if latest.get("Financing Cash Flow") is not None
                        else None
                    ),
                    "free_cash_flow": (
                        float(latest.get("Free Cash Flow", 0))
                        if latest.get("Free Cash Flow") is not None
                        else None
                    ),
                }
            else:
                financials["cash_flow"] = None
        except Exception as e:
            self.logger.warning(f"Failed to parse cash flow: {str(e)}")
            financials["cash_flow"] = None

        return financials

    def _get_etf_reports(self, ticker: yf.Ticker, info: Dict) -> Dict[str, Any]:
        """
        Fetch fund information and holdings for ETFs

        Args:
            ticker: yfinance Ticker object
            info: Basic security info

        Returns:
            Dict containing fund info, holdings, and performance
        """
        reports = {}

        # Fund information
        reports["fund_info"] = {
            "name": info.get("longName", info.get("shortName")),
            "category": info.get("category"),
            "family": info.get("fundFamily"),
            "total_assets": info.get("totalAssets"),
            "nav": info.get("navPrice"),
            "expense_ratio": info.get("annualReportExpenseRatio"),
            "yield": info.get("yield"),
            "ytd_return": info.get("ytdReturn"),
            "beta": info.get("beta3Year"),
            "inception_date": info.get("fundInceptionDate"),
        }

        # Holdings
        try:
            holdings = ticker.major_holders
            if holdings is not None and not holdings.empty:
                reports["major_holders"] = holdings.to_dict()
            else:
                reports["major_holders"] = None

            # Try to get fund holdings (top positions)
            fund_holdings = ticker.funds_data
            if fund_holdings:
                reports["holdings"] = fund_holdings
            else:
                reports["holdings"] = None
        except Exception as e:
            self.logger.warning(f"Failed to fetch holdings: {str(e)}")
            reports["holdings"] = None
            reports["major_holders"] = None

        # Performance metrics
        reports["performance"] = {
            "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
            "previous_close": info.get("previousClose"),
            "fifty_day_average": info.get("fiftyDayAverage"),
            "two_hundred_day_average": info.get("twoHundredDayAverage"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "year_change": info.get("52WeekChange"),
        }

        # Distributions (dividends)
        try:
            dividends = ticker.dividends
            if dividends is not None and not dividends.empty:
                recent_divs = []
                for date, value in dividends.tail(12).items():  # Last 12 distributions
                    recent_divs.append(
                        {
                            "date": (
                                date.isoformat()
                                if hasattr(date, "isoformat")
                                else str(date)
                            ),
                            "amount": float(value),
                        }
                    )
                reports["distributions"] = recent_divs
            else:
                reports["distributions"] = []
        except Exception as e:
            self.logger.warning(f"Failed to fetch distributions: {str(e)}")
            reports["distributions"] = []

        return reports

    def _get_generic_reports(self, ticker: yf.Ticker, info: Dict) -> Dict[str, Any]:
        """
        Fetch generic reports for other security types

        Args:
            ticker: yfinance Ticker object
            info: Basic security info

        Returns:
            Dict containing basic information
        """
        return {
            "info": {
                "name": info.get("longName", info.get("shortName")),
                "quote_type": info.get("quoteType"),
                "exchange": info.get("exchange"),
                "currency": info.get("currency"),
                "current_price": info.get(
                    "currentPrice", info.get("regularMarketPrice")
                ),
                "market_cap": info.get("marketCap"),
            }
        }

    def test_connection(self) -> bool:
        """
        Test if yfinance is working properly

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Test with a known symbol
            test_ticker = yf.Ticker("AAPL")
            info = test_ticker.info

            if info and "symbol" in info:
                self.logger.info("yfinance connection test successful")
                return True
            else:
                self.logger.error("yfinance test failed: No data returned")
                return False

        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
