"""
Event Horizon AI - FastAPI Server
Exposes Stage 1 data pipeline as REST API endpoints
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Any, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from pydantic import BaseModel

from event_horizon.data_pipeline import Stage1Orchestrator
from event_horizon.data_pipeline.stage_1.agents.candlestick_agent import CandlestickAgent
from event_horizon.data_pipeline.stage_1.agents.earnings_agent import EarningsAgent
from event_horizon.data_pipeline.stage_1.agents.fundamentals_agent import FundamentalsAgent
from event_horizon.data_pipeline.stage_1.agents.news_agent import NewsAgent
from event_horizon.data_pipeline.stage_1.agents.technical_agent import TechnicalAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Event Horizon AI API", description="Multi-agent AI system for financial data analysis", version="1.0.0"
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
    return HealthResponse(status="healthy", timestamp=datetime.now().isoformat(), version="1.0.0")


@app.get("/health", response_model=HealthResponse)
async def health():
    """Detailed health check"""
    return HealthResponse(status="healthy", timestamp=datetime.now().isoformat(), version="1.0.0")


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
            "portfolio_id": request.portfolio_id or f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
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
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/v1/supported-agents")
async def get_supported_agents():
    """Get list of supported data agents"""
    return {
        "agents": [
            {"name": "candlestick", "description": "OHLCV price data", "config_options": ["period", "interval"]},
            {
                "name": "earnings",
                "description": "Financial reports & earnings",
                "config_options": ["include_financials", "earnings_periods"],
            },
            {
                "name": "news",
                "description": "News articles & headlines",
                "config_options": ["max_articles_per_stock", "days_back"],
            },
            {
                "name": "technical",
                "description": "Technical indicators (SMA, RSI, MACD)",
                "config_options": ["indicators", "look_back_days"],
            },
            {
                "name": "fundamentals",
                "description": "Fundamental metrics (P/E, ROE, etc.)",
                "config_options": ["include_ratios", "include_financials"],
            },
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
        config = {"period": request.period, "interval": request.timeframe}
        agent = CandlestickAgent(config)
        result = agent._execute_internal(request.stocks)
        return result
    except Exception as e:
        logger.error(f"Candlestick agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/agents/news")
async def run_news_agent(request: AgentRequest):
    """Execute News agent for given stocks"""
    try:
        logger.info(f"Running News agent for {len(request.stocks)} stocks")
        config = {"max_articles_per_stock": 10, "days_back": request.days or 7}
        agent = NewsAgent(config)
        result = agent._execute_internal(request.stocks)
        return result
    except Exception as e:
        logger.error(f"News agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/agents/technical")
async def run_technical_agent(request: AgentRequest):
    """Execute Technical Analysis agent for given stocks"""
    try:
        logger.info(f"Running Technical agent for {len(request.stocks)} stocks")
        config = {"indicators": request.indicators or ["SMA", "RSI", "MACD"], "look_back_days": 30}
        agent = TechnicalAgent(config)
        result = agent._execute_internal(request.stocks)
        return result
    except Exception as e:
        logger.error(f"Technical agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        raise HTTPException(status_code=500, detail=str(e)) from e


# ===== System 2: Team 2 Researcher Endpoints =====
# These use Google Gemini (FREE tier) by default

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gemini_client = None
if GOOGLE_API_KEY:
    gemini_client = genai.Client(api_key=GOOGLE_API_KEY)


class System2Request(BaseModel):
    """Request model for System 2 agents"""

    stocks: List[str]
    data: Optional[dict] = None


class CustomAgentRequest(BaseModel):
    """Request model for custom agent execution"""

    stocks: List[str]
    system_prompt: str
    user_prompt: Optional[str] = None
    llm_config: Optional[dict] = None


class GenerateSystemPromptRequest(BaseModel):
    """Request model for generating system prompts"""

    name: str
    description: Optional[str] = ""  # Make optional with empty default
    category: Optional[str] = "strategy_agent"


class ThinkingAgentRequest(BaseModel):
    """Request model for iterative thinking agent execution"""

    stocks: List[str]
    input_data: Optional[dict] = None
    system_prompt: str
    max_iterations: int = 5
    available_tools: List[str] = ["candlestick", "earnings", "news", "technical", "fundamentals"]


def call_gemini(prompt: str, system_prompt: str = None) -> str:
    """Call Google Gemini API"""
    if not gemini_client:
        return {"error": "GOOGLE_API_KEY not configured"}

    model_name = os.getenv("DEFAULT_DEEP_THINK_MODEL", "gemini-2.0-flash-exp")

    # Create config with system instruction if provided
    if system_prompt:
        config = types.GenerateContentConfig(system_instruction=system_prompt)
    else:
        config = None

    response = gemini_client.models.generate_content(model=model_name, contents=prompt, config=config)
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
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        raise HTTPException(status_code=500, detail=str(e)) from e


# ===== Custom Agent Endpoints =====


@app.post("/agents/custom")
async def run_custom_agent(request: CustomAgentRequest):
    """
    Execute a custom agent with user-provided system prompt.

    Request body:
    {
        "stocks": ["AAPL", "TSLA"],
        "system_prompt": "You are a dividend-focused analyst...",
        "user_prompt": "Analyze these stocks for dividend potential",
        "llm_config": { "provider": "google", "model": "gemini-1.5-pro" }
    }
    """
    try:
        logger.info(f"Running Custom Agent for {request.stocks}")

        # Build user prompt
        user_prompt = request.user_prompt or f"Analyze the following stocks: {request.stocks}"
        prompt = f"""{user_prompt}

Stocks to analyze: {request.stocks}

Provide your analysis in a structured JSON format."""

        result = call_gemini(prompt, request.system_prompt)
        return {"status": "success", "agent": "custom", "result": result}
    except Exception as e:
        logger.error(f"Custom Agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/agents/generate-agent-system-prompt")
async def generate_agent_system_prompt(request: GenerateSystemPromptRequest):
    """
    Generate a system prompt from agent name, description, and category.

    Request body:
    {
        "name": "Dividend Hunter",
        "description": "An agent that finds high-yield dividend stocks",
        "category": "strategy_agent"
    }

    Returns:
    {
        "status": "success",
        "system_prompt": "You are a Dividend Hunter agent..."
    }
    """
    try:
        logger.info(f"Generating system prompt for agent: {request.name}")

        # Define category contexts
        category_contexts = {
            "market_analyzer": "You analyze market data, trends, and patterns to provide investment insights.",
            "risk_analyzer": "You evaluate and manage risk for investment decisions, focusing on portfolio safety.",
            "bull_bear_analyzer": "You provide balanced analysis of both bullish and bearish perspectives on investments.",
            "sentiment_analyzer": "You analyze market sentiment from news, social media, and public opinion.",
            "technical_analyzer": "You perform technical analysis on price charts and trading indicators.",
            "fundamental_analyzer": "You analyze company fundamentals, financials, and intrinsic value.",
            "custom_analyzer": "You perform specialized analysis based on your unique focus area.",
            "strategy_agent": "You provide strategic investment recommendations based on your analysis.",
            "data_retriever": "You retrieve and process financial data for other agents.",
            "news_agent": "You analyze news and market sentiment.",
            "technical_agent": "You perform technical analysis on price and volume data.",
        }

        category_context = category_contexts.get(request.category, category_contexts["strategy_agent"])

        # Build enhanced meta-prompt based on whether description is provided
        description_text = request.description.strip() if request.description else ""

        if not description_text:
            # Enhanced prompt for name-only generation
            meta_prompt = f"""You are an expert at creating system prompts for AI agents in a multi-agent trading system.

Create a detailed system prompt for an agent with the following characteristics:

**Agent Name:** {request.name}
**Category:** {category_context}

IMPORTANT: No description was provided, so you must:
1. Infer the agent's purpose and responsibilities from its NAME alone
2. Create a comprehensive, detailed system prompt based on what the name suggests
3. Define clear responsibilities (3-5 bullet points)
4. Specify expected input/output formats

The system prompt should:
1. Define the agent's role and expertise clearly
2. List specific responsibilities (3-5 bullet points)
3. Specify the input the agent receives
4. Define the expected output format (JSON structure preferred)
5. Include any relevant domain knowledge

Write ONLY the system prompt, nothing else. Start directly with "You are..." """
        else:
            # Original meta-prompt with description
            meta_prompt = f"""You are an expert at creating system prompts for AI agents in a multi-agent trading system.

Create a detailed system prompt for an agent with the following characteristics:

**Agent Name:** {request.name}
**Description:** {description_text}
**Category:** {category_context}

The system prompt should:
1. Define the agent's role and expertise clearly
2. List specific responsibilities (3-5 bullet points)
3. Specify the input the agent receives
4. Define the expected output format (JSON structure preferred)
5. Include any relevant domain knowledge

Write ONLY the system prompt, nothing else. Start directly with "You are..." """

        system_prompt = call_gemini(meta_prompt)

        # Clean up the response if needed
        if isinstance(system_prompt, dict) and "error" in system_prompt:
            raise Exception(system_prompt["error"])

        # Validate non-empty and minimum length
        cleaned_prompt = system_prompt.strip()
        if not cleaned_prompt:
            raise Exception("AI service generated an empty system prompt. Please try again or provide a description.")

        if len(cleaned_prompt) < 50:
            raise Exception(
                "Generated system prompt is too short. Please provide a more descriptive agent name or add a description."
            )

        return {"status": "success", "system_prompt": cleaned_prompt}
    except Exception as e:
        logger.error(f"System prompt generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate system prompt: {str(e)}. Please try providing a description for better results.",
        ) from e


# ===== Bull-Bear Analyzer Endpoint =====


@app.post("/agents/bull-bear-analyzer")
async def run_bull_bear_analyzer(request: System2Request):
    """
    Run the Bull-Bear coupled analyzer that performs internal debate.
    Returns both bull argument, bear counter-argument, and synthesized thesis.

    Request body:
    {
        "stocks": ["AAPL", "GOOGL"],
        "data": {...}  # Optional Stage3Output data
    }

    Returns:
    {
        "status": "success",
        "agent": "bull_bear_analyzer",
        "result": {
            "bull_bear_output": {...},
            "total_debates": 2,
            "total_tokens_used": 1234,
            "execution_time_seconds": 5.67
        }
    }
    """
    try:
        from event_horizon.analyzer_system import BullBearAnalyzer
        from event_horizon.data_pipeline.stage_3.models.schemas import Stage3Output

        analyzer = BullBearAnalyzer(
            config={
                "llm_model": "gpt-4o-mini",
                "temperature": 0.7,
                "enable_opik": False,
            }
        )

        # Convert request data to Stage3Output format if needed
        # For now, we'll use a simplified approach
        stage3_data = Stage3Output(
            portfolio_id=f"portfolio_{'-'.join(request.stocks)}",
            symbols=request.stocks,
            symbol_features=request.data or {},
        )

        result = analyzer.execute(stage3_data)

        return {"status": "success", "agent": "bull_bear_analyzer", "result": result}
    except Exception as e:
        logger.error(f"Bull-Bear Analyzer failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ===== Thinking Agent Endpoint =====

TOOLS_DESCRIPTION = {
    "candlestick": "OHLCV price data including open, high, low, close, volume for each trading day",
    "earnings": "Financial reports, quarterly earnings, EPS history, revenue data",
    "news": "Recent news articles, headlines, and press releases about the stocks",
    "technical": "Technical indicators including RSI, MACD, SMA, EMA, Bollinger Bands",
    "fundamentals": "Fundamental metrics like P/E ratio, P/B ratio, EPS, dividend yield, market cap",
}

THINK_PROMPT = """You are an intelligent financial analysis agent with access to data tools.

Your task: {system_prompt}

Available data tools:
{tools_description}

Current context:
- Stocks: {stocks}
- Data already collected: {collected_data_summary}

Decide your next action. You must respond in JSON only (no markdown, no explanation):

Option 1 - Need data from existing tool:
{{"action": "call_tool", "tool": "tool_name", "reasoning": "why I need this data"}}

Option 2 - Need specialized data that existing tools don't provide:
{{"action": "create_data_agent", "agent_name": "Name for the agent", "agent_description": "Describe what data this agent should fetch", "data_type": "what kind of data (e.g., options chain, insider trading, SEC filings)", "reasoning": "why existing tools don't have this data"}}

Option 3 - Ready to answer (have sufficient data):
{{"action": "generate_response", "reasoning": "I have sufficient data because..."}}

Think step by step. What data do you need to complete the analysis?"""


def summarize_data(data: dict) -> str:
    """Create a concise summary of collected data for context"""
    if not data:
        return "No data collected yet"

    summaries = []
    for tool_name, _tool_data in data.items():
        if tool_name == "candlestick":
            summaries.append(f"- {tool_name}: price data available")
        elif tool_name == "earnings":
            summaries.append(f"- {tool_name}: earnings/financials data available")
        elif tool_name == "news":
            summaries.append(f"- {tool_name}: news articles available")
        elif tool_name == "technical":
            summaries.append(f"- {tool_name}: technical indicators available")
        elif tool_name == "fundamentals":
            summaries.append(f"- {tool_name}: fundamental metrics available")
        else:
            summaries.append(f"- {tool_name}: custom data available")

    return "\n".join(summaries) if summaries else "No data collected yet"


def summarize_tool_result(tool_name: str, result: Any) -> str:
    """Create a concise summary of tool execution result"""
    if isinstance(result, dict):
        if "error" in result:
            return f"Error: {result['error']}"
        # Count items or keys
        if isinstance(result, dict):
            return f"Retrieved {len(result)} items"
    return "Data retrieved successfully"


async def execute_tool(tool_name: str, stocks: List[str]) -> dict:
    """Execute a built-in data tool and return results"""
    try:
        if tool_name == "candlestick":
            config = {"period": "1mo", "interval": "1d"}
            agent = CandlestickAgent(config)
            return agent._execute_internal(stocks)

        elif tool_name == "earnings":
            config = stage1_config["agent_configs"]["earnings"]
            agent = EarningsAgent(config)
            return agent._execute_internal(stocks)

        elif tool_name == "news":
            config = {"max_articles_per_stock": 10, "days_back": 7}
            agent = NewsAgent(config)
            return agent._execute_internal(stocks)

        elif tool_name == "technical":
            config = {"indicators": ["SMA", "RSI", "MACD"], "look_back_days": 30}
            agent = TechnicalAgent(config)
            return agent._execute_internal(stocks)

        elif tool_name == "fundamentals":
            config = stage1_config["agent_configs"]["fundamentals"]
            agent = FundamentalsAgent(config)
            return agent._execute_internal(stocks)

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    except Exception as e:
        logger.error(f"Tool execution failed for {tool_name}: {e}")
        return {"error": str(e)}


async def think_step(system_prompt: str, context: dict, available_tools: List[str]) -> dict:
    """Execute a thinking step - ask the LLM what action to take next"""
    stocks = context.get("stocks", [])
    collected_data = context.get("data", {})

    # Build tools description for available tools only
    tools_desc = "\n".join([f"- {tool}: {TOOLS_DESCRIPTION.get(tool, 'Custom data tool')}" for tool in available_tools])

    # Format the thinking prompt
    prompt = THINK_PROMPT.format(
        system_prompt=system_prompt,
        tools_description=tools_desc,
        stocks=stocks,
        collected_data_summary=summarize_data(collected_data),
    )

    try:
        # Call LLM to decide next action
        response = call_gemini(prompt)

        if isinstance(response, dict) and "error" in response:
            return {"action": "generate_response", "reasoning": "LLM error, generating response with available data"}

        # Parse JSON response
        # Clean up markdown code blocks if present
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = re.sub(r"^```(?:json)?\s*", "", clean_response)
            clean_response = re.sub(r"\s*```$", "", clean_response)

        thought = json.loads(clean_response)
        return thought

    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse thinking response as JSON: {e}")
        # Default to generating response if JSON parsing fails
        return {"action": "generate_response", "reasoning": "Could not parse LLM response, generating final response"}
    except Exception as e:
        logger.error(f"Think step failed: {e}")
        return {"action": "generate_response", "reasoning": f"Error in thinking: {str(e)}"}


async def generate_final_response(system_prompt: str, context: dict) -> dict:
    """Generate the final analysis response using collected data"""
    stocks = context.get("stocks", [])
    collected_data = context.get("data", {})

    prompt = f"""Based on the following data, provide your analysis.

Your role: {system_prompt}

Stocks: {stocks}

Available data:
{json.dumps(collected_data, indent=2, default=str)[:8000]}

Provide your final analysis in JSON format. Include:
- summary: Brief overview of your findings
- recommendations: List of actionable recommendations
- confidence: Your confidence level (0-1)
- key_insights: Most important findings
- risks: Any risks or caveats to note"""

    try:
        response = call_gemini(prompt)

        if isinstance(response, dict) and "error" in response:
            return response

        # Try to parse as JSON, otherwise return as text
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = re.sub(r"^```(?:json)?\s*", "", clean_response)
            clean_response = re.sub(r"\s*```$", "", clean_response)

        try:
            return json.loads(clean_response)
        except json.JSONDecodeError:
            return {"summary": response, "raw_response": True}

    except Exception as e:
        logger.error(f"Final response generation failed: {e}")
        return {"error": str(e)}


def generate_data_agent_prompt(thought: dict) -> str:
    """Generate system prompt for a custom data agent"""
    data_type = thought.get("data_type", "specialized data")
    description = thought.get("agent_description", "Retrieve and process financial data")

    return f"""You are a specialized data retrieval agent.

Your job is to fetch {data_type} data for the given stocks.

Data to retrieve: {description}

For each stock, retrieve the relevant data and return it in a structured JSON format.
Include timestamps and source information where available.

Output format:
{{
    "status": "success",
    "data": {{
        "<SYMBOL>": {{
            // relevant data fields
        }}
    }},
    "metadata": {{
        "retrieved_at": "ISO timestamp",
        "source": "data source name"
    }}
}}"""


@app.post("/agents/think")
async def run_thinking_agent(request: ThinkingAgentRequest):
    """
    Execute a thinking agent with iterative ReAct-style reasoning loop.

    The agent will:
    1. Analyze what data it needs
    2. Call available tools to gather data
    3. Optionally suggest creating new data agents
    4. Generate final analysis when ready

    Request body:
    {
        "stocks": ["AAPL", "TSLA"],
        "input_data": { ... },           # Optional: data from prior agent
        "system_prompt": "You are...",
        "max_iterations": 5,
        "available_tools": ["candlestick", "earnings", "news", "technical", "fundamentals"]
    }

    Returns:
    {
        "status": "success" | "paused",
        "final_result": { ... },
        "thinking_steps": [...],
        "tools_used": [...],
        "iterations_used": N
    }
    """
    try:
        logger.info(f"Running Thinking Agent for {request.stocks}")

        thinking_steps = []
        context = {"stocks": request.stocks, "data": request.input_data.copy() if request.input_data else {}}
        final_result = None
        tools_used = []

        for iteration in range(1, request.max_iterations + 1):
            logger.info(f"Thinking iteration {iteration}/{request.max_iterations}")

            # Step 1: Think - what do I need?
            thought = await think_step(request.system_prompt, context, request.available_tools)

            action = thought.get("action", "generate_response")
            reasoning = thought.get("reasoning", "")

            # Step 2: Execute action based on thought
            if action == "call_tool":
                tool_name = thought.get("tool", "")

                # Validate tool is available
                if tool_name not in request.available_tools:
                    thinking_steps.append(
                        {
                            "iteration": iteration,
                            "thought": reasoning,
                            "action": "error",
                            "error": f"Tool '{tool_name}' not in available tools",
                        }
                    )
                    continue

                # Skip if already have this data
                if tool_name in context["data"]:
                    thinking_steps.append(
                        {
                            "iteration": iteration,
                            "thought": reasoning,
                            "action": "skip",
                            "message": f"Already have {tool_name} data",
                        }
                    )
                    continue

                # Execute the tool
                tool_result = await execute_tool(tool_name, request.stocks)
                context["data"][tool_name] = tool_result
                tools_used.append(tool_name)

                thinking_steps.append(
                    {
                        "iteration": iteration,
                        "thought": reasoning,
                        "action": "call_tool",
                        "tool": tool_name,
                        "tool_result_summary": summarize_tool_result(tool_name, tool_result),
                    }
                )

            elif action == "create_data_agent":
                # PAUSE execution - need custom data agent
                agent_name = thought.get("agent_name", "Custom Data Agent")
                agent_description = thought.get("agent_description", "")
                data_type = thought.get("data_type", "specialized data")

                thinking_steps.append(
                    {
                        "iteration": iteration,
                        "thought": reasoning,
                        "action": "need_custom_data_agent",
                        "suggested_data_agent": {
                            "name": agent_name,
                            "description": agent_description,
                            "data_type": data_type,
                        },
                    }
                )

                return {
                    "status": "paused",
                    "reason": "need_data_agent",
                    "message": f"Need data agent to fetch: {data_type}",
                    "final_result": None,
                    "thinking_steps": thinking_steps,
                    "suggested_data_agent": {
                        "name": agent_name,
                        "description": agent_description,
                        "data_type": data_type,
                        "suggested_system_prompt": generate_data_agent_prompt(thought),
                    },
                    "resume_context": {
                        "stocks": request.stocks,
                        "system_prompt": request.system_prompt,
                        "collected_data": context["data"],
                        "iteration": iteration,
                    },
                    "tools_used": tools_used,
                    "iterations_used": iteration,
                }

            elif action == "generate_response":
                # Final analysis - generate response
                final_result = await generate_final_response(request.system_prompt, context)

                thinking_steps.append(
                    {
                        "iteration": iteration,
                        "thought": reasoning,
                        "action": "generate_response",
                        "result": final_result,
                    }
                )
                break

            else:
                # Unknown action - default to generating response
                logger.warning(f"Unknown action: {action}, generating response")
                final_result = await generate_final_response(request.system_prompt, context)
                thinking_steps.append(
                    {
                        "iteration": iteration,
                        "thought": f"Unknown action '{action}', generating response",
                        "action": "generate_response",
                        "result": final_result,
                    }
                )
                break

        # If we exhausted iterations without generating response, do it now
        if final_result is None:
            final_result = await generate_final_response(request.system_prompt, context)
            thinking_steps.append(
                {
                    "iteration": request.max_iterations,
                    "thought": "Max iterations reached, generating final response",
                    "action": "generate_response",
                    "result": final_result,
                }
            )

        return {
            "status": "success",
            "final_result": final_result,
            "thinking_steps": thinking_steps,
            "tools_used": list(set(tools_used)),
            "iterations_used": len(thinking_steps),
        }

    except Exception as e:
        logger.error(f"Thinking Agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_server:app", host="0.0.0.0", port=8001, reload=True, log_level="info")
