"""
Event Horizon AI - FastAPI Server
Exposes Stage 1 data pipeline as REST API endpoints
"""

import os
import logging
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from event_horizon.data_pipeline import Stage1Orchestrator
from event_horizon.data_pipeline.stage_1.agents.candlestick_agent import CandlestickAgent
from event_horizon.data_pipeline.stage_1.agents.earnings_agent import EarningsAgent
from event_horizon.data_pipeline.stage_1.agents.news_agent import NewsAgent
from event_horizon.data_pipeline.stage_1.agents.technical_agent import TechnicalAgent
from event_horizon.data_pipeline.stage_1.agents.fundamentals_agent import FundamentalsAgent

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


# ===== Individual Agent Endpoints =====

class AgentRequest(BaseModel):
    """Request model for individual agent execution"""
    stocks: List[str]
    timeframe: Optional[str] = "1d"
    period: Optional[str] = "30d"
    days: Optional[int] = 7
    indicators: Optional[List[str]] = None


@app.post("/agents/candlestick")
async def run_candlestick_agent(request: AgentRequest):
    """Execute Candlestick agent for given stocks"""
    try:
        logger.info(f"Running Candlestick agent for {len(request.stocks)} stocks")
        config = {
            "period": request.period,
            "interval": request.timeframe
        }
        agent = CandlestickAgent(config)
        result = agent._execute_internal(request.stocks)
        return result
    except Exception as e:
        logger.error(f"Candlestick agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/earnings")
async def run_earnings_agent(request: AgentRequest):
    """Execute Earnings agent for given stocks"""
    try:
        logger.info(f"Running Earnings agent for {len(request.stocks)} stocks")
        config = stage1_config["agent_configs"]["earnings"]
        agent = EarningsAgent(config)
        result = agent._execute_internal(request.stocks)
        return result
    except Exception as e:
        logger.error(f"Earnings agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/news")
async def run_news_agent(request: AgentRequest):
    """Execute News agent for given stocks"""
    try:
        logger.info(f"Running News agent for {len(request.stocks)} stocks")
        config = {
            "max_articles_per_stock": 10,
            "days_back": request.days or 7
        }
        agent = NewsAgent(config)
        result = agent._execute_internal(request.stocks)
        return result
    except Exception as e:
        logger.error(f"News agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/technical")
async def run_technical_agent(request: AgentRequest):
    """Execute Technical Analysis agent for given stocks"""
    try:
        logger.info(f"Running Technical agent for {len(request.stocks)} stocks")
        config = {
            "indicators": request.indicators or ["SMA", "RSI", "MACD"],
            "look_back_days": 30
        }
        agent = TechnicalAgent(config)
        result = agent._execute_internal(request.stocks)
        return result
    except Exception as e:
        logger.error(f"Technical agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/fundamentals")
async def run_fundamentals_agent(request: AgentRequest):
    """Execute Fundamentals agent for given stocks"""
    try:
        logger.info(f"Running Fundamentals agent for {len(request.stocks)} stocks")
        config = stage1_config["agent_configs"]["fundamentals"]
        agent = FundamentalsAgent(config)
        result = agent._execute_internal(request.stocks)
        return result
    except Exception as e:
        logger.error(f"Fundamentals agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== System 2: Team 2 Researcher Endpoints =====
# These use Google Gemini (FREE tier) by default

import google.generativeai as genai

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


class System2Request(BaseModel):
    """Request model for System 2 agents"""
    stocks: List[str]
    data: Optional[dict] = None


def call_gemini(prompt: str, system_prompt: str = None) -> str:
    """Call Google Gemini API"""
    if not GOOGLE_API_KEY:
        return {"error": "GOOGLE_API_KEY not configured"}

    model = genai.GenerativeModel(
        model_name=os.getenv("DEFAULT_DEEP_THINK_MODEL", "gemini-1.5-pro"),
        system_instruction=system_prompt
    )
    response = model.generate_content(prompt)
    return response.text


@app.post("/agents/bull-researcher")
async def run_bull_researcher(request: System2Request):
    """Execute Bull Researcher agent - builds bullish investment case"""
    try:
        logger.info(f"Running Bull Researcher for {request.stocks}")

        system_prompt = """You are a BULLISH investment researcher. Your job is to build the strongest possible BULL case for stocks.
Focus on: Growth opportunities, positive catalysts, competitive advantages, upside potential.
Return a JSON response with: recommendation, confidence (0-1), thesis, key_catalysts, supporting_evidence."""

        prompt = f"""Analyze these stocks and build a BULLISH investment case: {request.stocks}

Additional context: {request.data if request.data else 'No additional data provided'}

Return JSON format:
{{
    "recommendation": "BUY" or "STRONG_BUY",
    "confidence": 0.0-1.0,
    "thesis": "Main bullish thesis (2-3 sentences)",
    "key_catalysts": ["catalyst1", "catalyst2"],
    "supporting_evidence": ["evidence1", "evidence2"],
    "target_upside": "potential % gain"
}}"""

        result = call_gemini(prompt, system_prompt)
        return {"status": "success", "agent": "bull_researcher", "result": result}
    except Exception as e:
        logger.error(f"Bull Researcher failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/bear-researcher")
async def run_bear_researcher(request: System2Request):
    """Execute Bear Researcher agent - builds bearish investment case"""
    try:
        logger.info(f"Running Bear Researcher for {request.stocks}")

        system_prompt = """You are a BEARISH investment researcher. Your job is to build the strongest possible BEAR case for stocks.
Focus on: Risks, competitive threats, overvaluation concerns, negative trends.
Return a JSON response with: recommendation, confidence (0-1), thesis, key_risks, warning_signs."""

        prompt = f"""Analyze these stocks and build a BEARISH investment case: {request.stocks}

Additional context: {request.data if request.data else 'No additional data provided'}

Return JSON format:
{{
    "recommendation": "SELL" or "STRONG_SELL",
    "confidence": 0.0-1.0,
    "thesis": "Main bearish thesis (2-3 sentences)",
    "key_risks": ["risk1", "risk2"],
    "warning_signs": ["warning1", "warning2"],
    "target_downside": "potential % loss"
}}"""

        result = call_gemini(prompt, system_prompt)
        return {"status": "success", "agent": "bear_researcher", "result": result}
    except Exception as e:
        logger.error(f"Bear Researcher failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/research-manager")
async def run_research_manager(request: System2Request):
    """Execute Research Manager - synthesizes bull/bear arguments"""
    try:
        logger.info(f"Running Research Manager for {request.stocks}")

        system_prompt = """You are a senior Research Manager. Your job is to synthesize bull and bear arguments and make a final investment recommendation.
Be balanced and objective. Consider both sides fairly."""

        prompt = f"""As Research Manager, synthesize the investment analysis for: {request.stocks}

Bull/Bear data: {request.data if request.data else 'Run bull and bear researchers first'}

Provide final recommendation in JSON:
{{
    "final_recommendation": "STRONG_BUY" | "BUY" | "HOLD" | "SELL" | "STRONG_SELL",
    "conviction": 0.0-1.0,
    "thesis": "Final investment thesis",
    "bull_summary": "Key bull points",
    "bear_summary": "Key bear points",
    "decisive_factors": ["what tipped the decision"],
    "suggested_position_size": "% of portfolio"
}}"""

        result = call_gemini(prompt, system_prompt)
        return {"status": "success", "agent": "research_manager", "result": result}
    except Exception as e:
        logger.error(f"Research Manager failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== System 2: Team 1 Analyst Endpoints =====

@app.post("/agents/fundamentals-analyst")
async def run_fundamentals_analyst(request: System2Request):
    """Execute Fundamentals Analyst - analyzes company financials"""
    try:
        logger.info(f"Running Fundamentals Analyst for {request.stocks}")

        system_prompt = """You are a Fundamentals Analyst. Assess company financials, valuation metrics, and intrinsic value.
Focus on: P/E, P/B, EPS, revenue growth, profit margins, competitive moat."""

        prompt = f"""Analyze the fundamentals of: {request.stocks}

Provide analysis in JSON:
{{
    "valuation_assessment": "undervalued" | "fair" | "overvalued",
    "financial_health": "strong" | "moderate" | "weak",
    "key_metrics": {{"pe_ratio": "", "pb_ratio": "", "eps_growth": ""}},
    "competitive_moat": "wide" | "narrow" | "none",
    "analysis": "2-3 sentence summary"
}}"""

        result = call_gemini(prompt, system_prompt)
        return {"status": "success", "agent": "fundamentals_analyst", "result": result}
    except Exception as e:
        logger.error(f"Fundamentals Analyst failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/sentiment-analyst")
async def run_sentiment_analyst(request: System2Request):
    """Execute Sentiment Analyst - analyzes market sentiment"""
    try:
        logger.info(f"Running Sentiment Analyst for {request.stocks}")

        system_prompt = """You are a Sentiment Analyst. Examine social media trends, public opinion, and market psychology.
Focus on: Social sentiment, institutional positioning, retail sentiment, fear/greed indicators."""

        prompt = f"""Analyze market sentiment for: {request.stocks}

Provide analysis in JSON:
{{
    "overall_sentiment": -100 to +100 (bearish to bullish),
    "social_media_sentiment": "positive" | "neutral" | "negative",
    "institutional_sentiment": "bullish" | "neutral" | "bearish",
    "retail_sentiment": "bullish" | "neutral" | "bearish",
    "sentiment_trend": "improving" | "stable" | "deteriorating",
    "analysis": "2-3 sentence summary"
}}"""

        result = call_gemini(prompt, system_prompt)
        return {"status": "success", "agent": "sentiment_analyst", "result": result}
    except Exception as e:
        logger.error(f"Sentiment Analyst failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/news-analyst")
async def run_news_analyst(request: System2Request):
    """Execute News Analyst - analyzes news and macro indicators"""
    try:
        logger.info(f"Running News Analyst for {request.stocks}")

        system_prompt = """You are a News Analyst. Track global news and macroeconomic indicators for market impact.
Focus on: Breaking news, earnings announcements, macro data, geopolitical events."""

        prompt = f"""Analyze recent news impact for: {request.stocks}

Provide analysis in JSON:
{{
    "news_impact_score": 1-10,
    "key_headlines": ["headline1", "headline2"],
    "macro_context": "summary of macro environment",
    "sector_implications": "how sector is affected",
    "recommended_action": "based on news flow",
    "analysis": "2-3 sentence summary"
}}"""

        result = call_gemini(prompt, system_prompt)
        return {"status": "success", "agent": "news_analyst", "result": result}
    except Exception as e:
        logger.error(f"News Analyst failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/technical-analyst")
async def run_technical_analyst(request: System2Request):
    """Execute Technical Analyst - analyzes price patterns and indicators"""
    try:
        logger.info(f"Running Technical Analyst for {request.stocks}")

        system_prompt = """You are a Technical Analyst. Apply technical indicators to detect trends and forecast price movements.
Focus on: MACD, RSI, moving averages, support/resistance, chart patterns."""

        prompt = f"""Provide technical analysis for: {request.stocks}

Provide analysis in JSON:
{{
    "trend_direction": "bullish" | "bearish" | "neutral",
    "trend_strength": "strong" | "moderate" | "weak",
    "key_support": "price level",
    "key_resistance": "price level",
    "momentum": "overbought" | "neutral" | "oversold",
    "pattern_detected": "pattern name if any",
    "technical_signal": "BUY" | "HOLD" | "SELL",
    "analysis": "2-3 sentence summary"
}}"""

        result = call_gemini(prompt, system_prompt)
        return {"status": "success", "agent": "technical_analyst", "result": result}
    except Exception as e:
        logger.error(f"Technical Analyst failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== System 2: Team 3 Portfolio =====

@app.post("/agents/portfolio-manager")
async def run_portfolio_manager(request: System2Request):
    """Execute Portfolio Manager - manages allocation and position sizing"""
    try:
        logger.info(f"Running Portfolio Manager for {request.stocks}")

        system_prompt = """You are a Portfolio Manager. Evaluate portfolio-level decisions, position sizing, and asset allocation.
Focus on: Diversification, correlation, risk-adjusted returns, rebalancing."""

        prompt = f"""Provide portfolio recommendations for: {request.stocks}

Context: {request.data if request.data else 'No existing positions'}

Provide analysis in JSON:
{{
    "portfolio_action": {{"symbol": "ADD/REDUCE/HOLD/EXIT" for each}},
    "target_allocation": {{"symbol": "% of portfolio" for each}},
    "diversification_score": 1-10,
    "correlation_risk": "low" | "moderate" | "high",
    "rebalancing_needed": true | false,
    "recommendations": ["action1", "action2"]
}}"""

        result = call_gemini(prompt, system_prompt)
        return {"status": "success", "agent": "portfolio_manager", "result": result}
    except Exception as e:
        logger.error(f"Portfolio Manager failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== System 2: Team 4 Risk & Execution =====

@app.post("/agents/risk-manager")
async def run_risk_manager(request: System2Request):
    """Execute Risk Manager - evaluates risk and approves transactions"""
    try:
        logger.info(f"Running Risk Manager for {request.stocks}")

        system_prompt = """You are a Risk Manager. Evaluate portfolio risk, volatility, and liquidity before approving transactions.
Focus on: VaR, drawdown limits, position limits, liquidity risk."""

        prompt = f"""Evaluate risk for positions in: {request.stocks}

Context: {request.data if request.data else 'Standard risk parameters'}

Provide analysis in JSON:
{{
    "risk_assessment": "APPROVED" | "REJECTED" | "CONDITIONAL",
    "risk_score": 1-10,
    "key_risks": ["risk1", "risk2"],
    "var_impact": "estimated VaR change",
    "conditions": ["condition if conditional approval"],
    "risk_mitigation": ["mitigation1", "mitigation2"]
}}"""

        result = call_gemini(prompt, system_prompt)
        return {"status": "success", "agent": "risk_manager", "result": result}
    except Exception as e:
        logger.error(f"Risk Manager failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/trader")
async def run_trader(request: System2Request):
    """Execute Trader Agent - determines trade timing and execution"""
    try:
        logger.info(f"Running Trader Agent for {request.stocks}")

        system_prompt = """You are a Trader Agent. Synthesize all analysis to determine trade timing, sizing, and execution.
Focus on: Entry/exit points, order types, position sizing, execution strategy."""

        prompt = f"""Generate trade execution plan for: {request.stocks}

Context: {request.data if request.data else 'Based on current analysis'}

Provide execution plan in JSON:
{{
    "trade_action": "BUY" | "SELL" | "HOLD",
    "order_type": "MARKET" | "LIMIT" | "STOP_LIMIT",
    "entry_price": "target entry",
    "stop_loss": "stop loss level",
    "take_profit": "take profit level",
    "position_size": "recommended size",
    "time_horizon": "day trade" | "swing" | "position",
    "urgency": "immediate" | "wait for pullback" | "scale in",
    "execution_notes": "additional notes"
}}"""

        result = call_gemini(prompt, system_prompt)
        return {"status": "success", "agent": "trader", "result": result}
    except Exception as e:
        logger.error(f"Trader Agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
