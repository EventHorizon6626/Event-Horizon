"""
Event Horizon AI - FastAPI Server
Exposes Stage 1 data pipeline as REST API endpoints
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from event_horizon.data_pipeline import Stage1Orchestrator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Event Horizon AI API",
    description="Multi-agent AI system for financial data analysis",
    version="1.0.0"
)

# CORS middleware - configure for your FE domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your FE domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class PortfolioRequest(BaseModel):
    portfolio: List[str]
    portfolio_id: Optional[str] = None
    enabled_agents: Optional[List[str]] = None
    agent_configs: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


# Global Stage1 Orchestrator
stage1_config = {
    "enabled_agents": ["candlestick", "earnings", "news", "technical", "fundamentals"],
    "max_workers": 5,
    "agent_configs": {
        "candlestick": {
            "period": "1mo",
            "interval": "1d",
        },
        "earnings": {
            "include_financials": True,
            "earnings_periods": 4,
        },
        "news": {
            "max_articles_per_stock": 10,
            "days_back": 7,
        },
        "technical": {
            "indicators": ["SMA", "RSI", "MACD"],
            "look_back_days": 30,
        },
        "fundamentals": {
            "include_ratios": True,
            "include_financials": True,
        },
    },
}


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.post("/api/v1/analyze-portfolio")
async def analyze_portfolio(request: PortfolioRequest):
    """
    Analyze a portfolio using Stage 1 data pipeline

    Request body:
    {
        "portfolio": ["AAPL", "TSLA", "SPY", "NVDA"],
        "portfolio_id": "optional_custom_id",
        "enabled_agents": ["candlestick", "earnings", "news", "technical", "fundamentals"],
        "agent_configs": { ... }
    }

    Returns:
    {
        "status": "success",
        "stage1_output": { ... },
        "execution_time_seconds": 12.34,
        "agents_executed": [...],
        "errors": [...]
    }
    """
    try:
        logger.info(f"Analyzing portfolio: {request.portfolio}")

        # Create custom config if provided
        config = stage1_config.copy()
        if request.enabled_agents:
            config["enabled_agents"] = request.enabled_agents
        if request.agent_configs:
            config["agent_configs"].update(request.agent_configs)

        # Initialize orchestrator
        orchestrator = Stage1Orchestrator(config=config)

        # Prepare input
        portfolio_input = {
            "portfolio": request.portfolio,
            "portfolio_id": request.portfolio_id or f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }

        # Execute Stage 1
        result = orchestrator.execute(portfolio_input)

        # Convert Stage1Output to dict if needed
        if hasattr(result.get("stage1_output"), "to_dict"):
            result["stage1_output"] = result["stage1_output"].to_dict()

        logger.info(f"Analysis completed: {result['status']}")
        return result

    except Exception as e:
        logger.error(f"Error analyzing portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/supported-agents")
async def get_supported_agents():
    """Get list of supported data agents"""
    return {
        "agents": [
            {
                "name": "candlestick",
                "description": "OHLCV price data",
                "config_options": ["period", "interval"]
            },
            {
                "name": "earnings",
                "description": "Financial reports & earnings",
                "config_options": ["include_financials", "earnings_periods"]
            },
            {
                "name": "news",
                "description": "News articles & headlines",
                "config_options": ["max_articles_per_stock", "days_back"]
            },
            {
                "name": "technical",
                "description": "Technical indicators (SMA, RSI, MACD)",
                "config_options": ["indicators", "look_back_days"]
            },
            {
                "name": "fundamentals",
                "description": "Fundamental metrics (P/E, ROE, etc.)",
                "config_options": ["include_ratios", "include_financials"]
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
