"""Stage 1 Orchestrator — parallel data collection pipeline."""

import asyncio
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException

from models import PortfolioRequest
from services.data_agents import STAGE1_CONFIG

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["data-pipeline"])


def _run_orchestrator(request: PortfolioRequest) -> dict:
    """Synchronous Stage1Orchestrator execution (runs in thread)."""
    from event_horizon.data_pipeline import Stage1Orchestrator

    config = STAGE1_CONFIG.copy()
    if request.enabled_agents:
        config["enabled_agents"] = request.enabled_agents
    if request.agent_configs:
        config["agent_configs"].update(request.agent_configs)

    orchestrator = Stage1Orchestrator(config=config)
    portfolio_input = {
        "portfolio": request.portfolio,
        "portfolio_id": request.portfolio_id or f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    }
    result = orchestrator.execute(portfolio_input)

    if hasattr(result.get("stage1_output"), "to_dict"):
        result["stage1_output"] = result["stage1_output"].to_dict()

    return result


@router.post("/analyze-portfolio")
async def analyze_portfolio(request: PortfolioRequest):
    """Analyze a portfolio using Stage 1 data pipeline."""
    try:
        logger.info(f"Analyzing portfolio: {request.portfolio}")
        result = await asyncio.to_thread(_run_orchestrator, request)
        logger.info(f"Analysis completed: {result['status']}")
        return result
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/supported-agents")
async def get_supported_agents():
    """List data agent types supported by the Stage 1 pipeline."""
    return {
        "agents": [
            {"name": "candlestick", "description": "OHLCV price data", "config_options": ["period", "interval"]},
            {"name": "earnings", "description": "Financial reports & earnings", "config_options": ["include_financials", "earnings_periods"]},
            {"name": "news", "description": "News articles & headlines", "config_options": ["max_articles_per_stock", "days_back"]},
            {"name": "technical", "description": "Technical indicators (SMA, RSI, MACD)", "config_options": ["indicators", "look_back_days"]},
            {"name": "fundamentals", "description": "Fundamental metrics (P/E, ROE, etc.)", "config_options": ["include_ratios", "include_financials"]},
        ]
    }
