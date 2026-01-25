"""
Layer 1 Data Retrieval Agents

Each agent specializes in retrieving data from ONE source:
- CandlestickAgent: OHLCV price data
- EarningsAgent: Financial reports and earnings
- NewsAgent: News articles and headlines
- TechnicalAgent: Technical indicators (SMA, RSI, MACD) - Tauric-inspired
- FundamentalsAgent: Fundamental metrics and ratios - Tauric-inspired
- OptionsFlowAgent: Options chain and flow data (future)
- SocialMediaAgent: Twitter/Reddit sentiment (future)
- SECFilingsAgent: SEC filings (future)

All agents inherit from BaseAgent and operate independently.
"""

from layer_1.agents.candlestick_agent import CandlestickAgent
from layer_1.agents.earnings_agent import EarningsAgent
from layer_1.agents.news_agent import NewsAgent
from layer_1.agents.technical_agent import TechnicalAgent
from layer_1.agents.fundamentals_agent import FundamentalsAgent

# Future agents (placeholders)
# from layer_1.agents.options_flow_agent import OptionsFlowAgent
# from layer_1.agents.social_media_agent import SocialMediaAgent
# from layer_1.agents.sec_filings_agent import SECFilingsAgent

__all__ = [
    "CandlestickAgent",
    "EarningsAgent",
    "NewsAgent",
    "TechnicalAgent",
    "FundamentalsAgent",
]
