"""
Data Normalizer

Transforms heterogeneous Stage 1 data into normalized Stage 2 format.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from event_horizon.data_pipeline.stage_1.models.schemas import (
    Stage1Output,
    ChartData,
    NewsData,
    EarningsData,
    TechnicalData,
    FundamentalsData,
)
from event_horizon.data_pipeline.stage_2.models.schemas import NormalizedSymbolData


class DataNormalizer:
    """
    Data Normalizer - Converts heterogeneous data to unified format

    Responsibilities:
    - Standardize data formats across sources
    - Align timestamps
    - Clean and validate data
    - Calculate quality scores
    """

    def __init__(self):
        self.logger = logging.getLogger("data_pipeline.stage_2.normalizer")

    def normalize_symbol_data(
        self,
        symbol: str,
        stage1_output: Stage1Output,
    ) -> NormalizedSymbolData:
        """
        Normalize all data for a single symbol

        Args:
            symbol: Stock symbol
            stage1_output: Complete Stage 1 output

        Returns:
            NormalizedSymbolData with unified format
        """
        self.logger.info(f"Normalizing data for {symbol}")

        normalized = NormalizedSymbolData(symbol=symbol)
        errors = []

        # Normalize price/chart data
        if symbol in stage1_output.chart_data:
            chart_data = stage1_output.chart_data[symbol]
            try:
                normalized.price_data = self._normalize_chart_data(chart_data)
            except Exception as e:
                errors.append(f"Chart data normalization failed: {str(e)}")
                self.logger.error(f"{symbol}: Chart data error - {e}")

        # Normalize technical indicators
        if symbol in stage1_output.technical_data:
            tech_data = stage1_output.technical_data[symbol]
            try:
                normalized.technical_indicators = self._normalize_technical_data(tech_data)
            except Exception as e:
                errors.append(f"Technical data normalization failed: {str(e)}")
                self.logger.error(f"{symbol}: Technical data error - {e}")

        # Normalize fundamentals
        if symbol in stage1_output.fundamentals_data:
            fund_data = stage1_output.fundamentals_data[symbol]
            try:
                normalized.fundamentals = self._normalize_fundamentals_data(fund_data)
            except Exception as e:
                errors.append(f"Fundamentals normalization failed: {str(e)}")
                self.logger.error(f"{symbol}: Fundamentals error - {e}")

        # Normalize news
        if symbol in stage1_output.news_data:
            news_data = stage1_output.news_data[symbol]
            try:
                normalized.news = self._normalize_news_data(news_data)
            except Exception as e:
                errors.append(f"News normalization failed: {str(e)}")
                self.logger.error(f"{symbol}: News error - {e}")

        # Normalize earnings
        if symbol in stage1_output.earnings_data:
            earnings_data = stage1_output.earnings_data[symbol]
            try:
                normalized.earnings = self._normalize_earnings_data(earnings_data)
            except Exception as e:
                errors.append(f"Earnings normalization failed: {str(e)}")
                self.logger.error(f"{symbol}: Earnings error - {e}")

        # Update metadata
        normalized.errors = errors
        normalized.has_errors = len(errors) > 0
        normalized.data_quality_score = self._calculate_quality_score(normalized)

        self.logger.info(
            f"{symbol}: Normalized (quality: {normalized.data_quality_score:.2f})"
        )

        return normalized

    def _normalize_chart_data(self, chart_data: ChartData) -> Dict[str, Any]:
        """Normalize price/chart data"""
        if chart_data.error:
            return {"error": chart_data.error}

        candles = chart_data.candles if hasattr(chart_data, 'candles') else []

        # Calculate latest price and change
        latest_price = None
        price_change_pct = None

        if len(candles) > 0:
            latest_candle = candles[-1]
            latest_price = latest_candle.get("close")

            if len(candles) > 1:
                prev_close = candles[-2].get("close")
                if prev_close and latest_price:
                    price_change_pct = ((latest_price - prev_close) / prev_close) * 100

        return {
            "latest_price": latest_price,
            "price_change_pct": price_change_pct,
            "candles": candles,
            "period": chart_data.period,
            "interval": chart_data.interval,
            "data_source": chart_data.data_source,
        }

    def _normalize_technical_data(self, tech_data: TechnicalData) -> Dict[str, Any]:
        """Normalize technical indicators"""
        if tech_data.error:
            return {"error": tech_data.error}

        normalized_indicators = {}

        # Parse indicator text into structured format
        for indicator_name, indicator_text in tech_data.indicators.items():
            normalized_indicators[indicator_name] = {
                "text": indicator_text,
                "raw": indicator_text,
            }

        return {
            "indicators": normalized_indicators,
            "trade_date": tech_data.trade_date,
            "look_back_days": tech_data.look_back_days,
            "data_source": tech_data.data_source,
        }

    def _normalize_fundamentals_data(self, fund_data: FundamentalsData) -> Dict[str, Any]:
        """Normalize fundamental metrics"""
        if fund_data.error:
            return {"error": fund_data.error}

        return {
            "text_summary": fund_data.fundamentals_text,
            "data_source": fund_data.data_source,
        }

    def _normalize_news_data(self, news_data: NewsData) -> Dict[str, Any]:
        """Normalize news articles"""
        if news_data.error:
            return {"error": news_data.error}

        articles = news_data.articles if hasattr(news_data, 'articles') else []

        # Find latest timestamp
        latest_timestamp = None
        if articles:
            timestamps = [
                a.get("publishedAt") for a in articles if a.get("publishedAt")
            ]
            if timestamps:
                latest_timestamp = max(timestamps)

        return {
            "articles": articles,
            "total_count": news_data.total_articles,
            "latest_timestamp": latest_timestamp,
            "data_source": news_data.data_source,
        }

    def _normalize_earnings_data(self, earnings_data: EarningsData) -> Dict[str, Any]:
        """Normalize earnings/report data"""
        if earnings_data.error:
            return {"error": earnings_data.error}

        return {
            "company_name": earnings_data.name,
            "security_type": earnings_data.security_type,
            "earnings_reports": earnings_data.earnings_reports,
            "financials": earnings_data.financial_statements,
            "metrics": earnings_data.metrics,
            "fund_info": earnings_data.fund_info,
            "data_source": earnings_data.data_source,
        }

    def _calculate_quality_score(self, normalized: NormalizedSymbolData) -> float:
        """
        Calculate data quality score (0-1)

        Based on completeness and absence of errors
        """
        score = 0.0
        max_score = 5.0  # 5 data categories

        # Price data
        if normalized.price_data and not normalized.price_data.get("error"):
            score += 1.0

        # Technical indicators
        if normalized.technical_indicators and not normalized.technical_indicators.get("error"):
            score += 1.0

        # Fundamentals
        if normalized.fundamentals and not normalized.fundamentals.get("error"):
            score += 1.0

        # News
        if normalized.news and not normalized.news.get("error"):
            score += 1.0

        # Earnings
        if normalized.earnings and not normalized.earnings.get("error"):
            score += 1.0

        # Normalize to 0-1
        quality = score / max_score

        # Penalize for errors
        if normalized.has_errors:
            quality *= 0.8  # 20% penalty

        return quality
