"""
Stage 1 Services Stages

External API clients for data retrieval.
Services handle low-level API communication and return raw data.
Agents use these services to fetch and process data.
"""

# News services
from data_pipeline.stage_1.services.news_api_client import NewsAPIClient

# Financial services
from data_pipeline.stage_1.services.financial_data_client import FinancialDataClient

# Chart services
from data_pipeline.stage_1.services.chart_data_client import ChartDataClient
from data_pipeline.stage_1.services.massive_chart_client import MassiveChartClient

__all__ = [
    "NewsAPIClient",
    "FinancialDataClient",
    "ChartDataClient",
    "MassiveChartClient",
]
