"""
Stock Data Tools for Stage 1

Utility functions for retrieving stock data, technical indicators, and fundamentals.
Inspired by Tauric Research TradingAgents framework.
"""

import logging
from typing import Optional
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def get_stock_data(
    symbol: str,
    start_date: str,
    end_date: str,
) -> str:
    """
    Retrieve stock price data (OHLCV) for a given ticker symbol.

    Args:
        symbol: Ticker symbol of the company (e.g., AAPL, TSLA)
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format

    Returns:
        Formatted string containing stock price data
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)

        if df.empty:
            return f"No data found for {symbol} between {start_date} and {end_date}"

        # Format as string for LLM consumption
        result = f"Stock Data for {symbol} ({start_date} to {end_date}):\n"
        result += df.to_string()

        return result

    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
        return f"Error retrieving data for {symbol}: {str(e)}"


def get_indicators(
    symbol: str,
    indicator: str,
    curr_date: str,
    look_back_days: int = 30,
) -> str:
    """
    Retrieve technical indicators for a given ticker symbol.

    Args:
        symbol: Ticker symbol of the company (e.g., AAPL, TSLA)
        indicator: Technical indicator name (e.g., SMA, EMA, RSI, MACD)
        curr_date: Current trading date in YYYY-mm-dd format
        look_back_days: How many days to look back (default: 30)

    Returns:
        Formatted string containing technical indicator data
    """
    try:
        # Calculate date range
        end_date = datetime.strptime(curr_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=look_back_days + 100)  # Extra buffer for calculation

        # Fetch stock data
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date.strftime("%Y-%m-%d"),
                           end=end_date.strftime("%Y-%m-%d"))

        if df.empty:
            return f"No data found for {symbol}"

        # Calculate indicator
        indicator_upper = indicator.upper()

        if indicator_upper == "SMA":
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            result_df = df[['Close', 'SMA_20', 'SMA_50']].tail(look_back_days)

        elif indicator_upper == "EMA":
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            result_df = df[['Close', 'EMA_12', 'EMA_26']].tail(look_back_days)

        elif indicator_upper == "RSI":
            # Calculate RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            result_df = df[['Close', 'RSI']].tail(look_back_days)

        elif indicator_upper == "MACD":
            # Calculate MACD
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['Histogram'] = df['MACD'] - df['Signal']
            result_df = df[['Close', 'MACD', 'Signal', 'Histogram']].tail(look_back_days)

        else:
            return f"Unsupported indicator: {indicator}. Supported: SMA, EMA, RSI, MACD"

        # Format output
        result = f"Technical Indicator: {indicator.upper()} for {symbol}\n"
        result += f"Period: Last {look_back_days} days ending {curr_date}\n\n"
        result += result_df.to_string()

        return result

    except Exception as e:
        logger.error(f"Error calculating {indicator} for {symbol}: {str(e)}")
        return f"Error calculating {indicator} for {symbol}: {str(e)}"


def get_fundamentals(
    symbol: str,
) -> str:
    """
    Retrieve fundamental data for a given ticker symbol.

    Args:
        symbol: Ticker symbol of the company (e.g., AAPL, TSLA)

    Returns:
        Formatted string containing fundamental data
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if not info:
            return f"No fundamental data found for {symbol}"

        # Extract key fundamental metrics
        result = f"Fundamental Data for {symbol}:\n\n"

        # Company Info
        result += "Company Information:\n"
        result += f"  Name: {info.get('longName', 'N/A')}\n"
        result += f"  Sector: {info.get('sector', 'N/A')}\n"
        result += f"  Industry: {info.get('industry', 'N/A')}\n"
        result += f"  Market Cap: ${info.get('marketCap', 0):,.0f}\n\n"

        # Valuation Metrics
        result += "Valuation Metrics:\n"
        result += f"  P/E Ratio: {info.get('trailingPE', 'N/A')}\n"
        result += f"  Forward P/E: {info.get('forwardPE', 'N/A')}\n"
        result += f"  PEG Ratio: {info.get('pegRatio', 'N/A')}\n"
        result += f"  Price/Book: {info.get('priceToBook', 'N/A')}\n"
        result += f"  Price/Sales: {info.get('priceToSalesTrailing12Months', 'N/A')}\n\n"

        # Profitability
        result += "Profitability:\n"
        result += f"  Profit Margin: {info.get('profitMargins', 'N/A')}\n"
        result += f"  Operating Margin: {info.get('operatingMargins', 'N/A')}\n"
        result += f"  ROE: {info.get('returnOnEquity', 'N/A')}\n"
        result += f"  ROA: {info.get('returnOnAssets', 'N/A')}\n\n"

        # Financial Health
        result += "Financial Health:\n"
        result += f"  Total Cash: ${info.get('totalCash', 0):,.0f}\n"
        result += f"  Total Debt: ${info.get('totalDebt', 0):,.0f}\n"
        result += f"  Current Ratio: {info.get('currentRatio', 'N/A')}\n"
        result += f"  Debt/Equity: {info.get('debtToEquity', 'N/A')}\n\n"

        # Growth
        result += "Growth:\n"
        result += f"  Revenue Growth: {info.get('revenueGrowth', 'N/A')}\n"
        result += f"  Earnings Growth: {info.get('earningsGrowth', 'N/A')}\n\n"

        # Dividends
        result += "Dividends:\n"
        result += f"  Dividend Yield: {info.get('dividendYield', 'N/A')}\n"
        result += f"  Payout Ratio: {info.get('payoutRatio', 'N/A')}\n"

        return result

    except Exception as e:
        logger.error(f"Error fetching fundamentals for {symbol}: {str(e)}")
        return f"Error retrieving fundamentals for {symbol}: {str(e)}"
