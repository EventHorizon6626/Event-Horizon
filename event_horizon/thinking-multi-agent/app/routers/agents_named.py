"""Named agent endpoints — data agents, bull-bear, custom, prompt gen, think."""

import json
import logging
import os

from fastapi import APIRouter, HTTPException

from models import (
    AgentRequest,
    AnalysisResponse,
    AnalyzerRequest,
    CustomAgentRequest,
    GenerateSystemPromptRequest,
    ThinkingAgentRequest,
)
from services.data_agents import STAGE1_CONFIG, execute_tool
from services.llm import LLM_MODEL, call_llm, call_llm_full
from services.thinking_engine import (
    TOOLS_DESCRIPTION,
    generate_data_agent_prompt,
    run_thinking_loop,
    think_step,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents-named"])


# ── Data agent endpoints ──

@router.post("/candlestick")
async def run_candlestick_agent(request: AgentRequest):
    """Execute Candlestick agent for given stocks."""
    try:
        logger.info(f"Running Candlestick agent for {len(request.stocks)} stocks")
        result = await execute_tool("candlestick", request.stocks, period=request.period, interval=request.timeframe)
        return result
    except Exception as e:
        logger.error(f"Candlestick agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/earnings")
async def run_earnings_agent(request: AgentRequest):
    """Execute Earnings agent for given stocks."""
    try:
        logger.info(f"Running Earnings agent for {len(request.stocks)} stocks")
        result = await execute_tool("earnings", request.stocks)
        return result
    except Exception as e:
        logger.error(f"Earnings agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/news")
async def run_news_agent(request: AgentRequest):
    """Execute News agent for given stocks."""
    try:
        logger.info(f"Running News agent for {len(request.stocks)} stocks")
        result = await execute_tool("news", request.stocks, days_back=request.days or 7)
        return result
    except Exception as e:
        logger.error(f"News agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/technical")
async def run_technical_agent(request: AgentRequest):
    """Execute Technical Analysis agent for given stocks."""
    try:
        logger.info(f"Running Technical agent for {len(request.stocks)} stocks")
        overrides = {}
        if request.indicators:
            overrides["indicators"] = request.indicators
        result = await execute_tool("technical", request.stocks, **overrides)
        return result
    except Exception as e:
        logger.error(f"Technical agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/fundamentals")
async def run_fundamentals_agent(request: AgentRequest):
    """Execute Fundamentals agent for given stocks."""
    try:
        logger.info(f"Running Fundamentals agent for {len(request.stocks)} stocks")
        result = await execute_tool("fundamentals", request.stocks)
        return result
    except Exception as e:
        logger.error(f"Fundamentals agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ── Bull-Bear Analyzer ──

@router.post("/bull-bear-analyzer")
async def run_bull_bear_analyzer(request: AnalyzerRequest):
    """Run the Bull-Bear coupled analyzer that performs internal debate."""
    try:
        import asyncio

        from event_horizon.analyzer_system import BullBearAnalyzer
        from event_horizon.data_pipeline.stage_3.models.schemas import Stage3Output, SymbolFeatures

        logger.info("Bull-Bear Analyzer: starting for stocks=%s", request.stocks)
        analyzer = BullBearAnalyzer(
            config={"llm_model": os.getenv("LLM_MODEL", "mistralai/Ministral-3-14B-Reasoning-2512"), "temperature": 0.7, "enable_opik": False}
        )
        # Convert raw dicts to SymbolFeatures objects
        import dataclasses
        raw_features = request.data or {}
        logger.debug("Bull-Bear Analyzer: converting %d symbol features from raw dicts", len(raw_features))
        valid_fields = {f.name for f in dataclasses.fields(SymbolFeatures)}
        symbol_features = {}
        for sym, feat in raw_features.items():
            if isinstance(feat, dict):
                filtered = {k: v for k, v in feat.items() if k in valid_fields}
                filtered["symbol"] = sym
                symbol_features[sym] = SymbolFeatures(**filtered)
            else:
                symbol_features[sym] = feat
        stage3_data = Stage3Output(
            portfolio_id=f"portfolio_{'-'.join(request.stocks)}",
            symbols=request.stocks,
            symbol_features=symbol_features,
        )
        result = await asyncio.to_thread(analyzer.execute, stage3_data)
        logger.info("Bull-Bear Analyzer: complete for stocks=%s", request.stocks)
        return {"status": "success", "agent": "bull_bear_analyzer", "result": result}
    except Exception as e:
        logger.error(f"Bull-Bear Analyzer failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ── Custom agent ──

@router.post("/custom", response_model=AnalysisResponse)
async def run_custom_agent(request: CustomAgentRequest):
    """Execute a custom agent with user-provided system prompt.

    If input_data is provided (from connected pipeline nodes), runs analysis
    directly. Otherwise, uses a thinking step to discover what data agents
    are needed and returns them as required_agents with status='needs_data'.
    """
    try:
        logger.info(f"Running Custom Agent for {request.stocks}")

        # ── Path A: we already have data from connected nodes ──
        # input_data is expected to be SymbolFeatures (EH DNA) from the pipeline
        if request.input_data:
            logger.info("Custom Agent: Path A — using provided input_data")
            user_prompt = request.user_prompt or f"Analyze the following stocks: {request.stocks}"
            data_summary = json.dumps(request.input_data, indent=2, default=str)[:8000]
            messages = [
                {"role": "system", "content": request.system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"{user_prompt}\n\n"
                        f"Stocks: {request.stocks}\n\n"
                        f"EH-processed SymbolFeatures from data pipeline:\n{data_summary}\n\n"
                        f"Provide your analysis based on these extracted features."
                    ),
                },
            ]
            result = await call_llm_full(messages)
            return AnalysisResponse(
                status="success",
                analysis=result["content"],
                reasoning=result.get("reasoning"),
                model=result["model"],
                usage=result.get("usage"),
                agent_name="custom",
            )

        # ── Path B: no data — discover what's needed ──
        logger.info("Custom Agent: Path B — discovering required data")
        available_tools = list(TOOLS_DESCRIPTION.keys())
        context = {"stocks": request.stocks, "data": {}}
        thought = await think_step(request.system_prompt, context, available_tools)
        action = thought.get("action", "generate_response")
        logger.info("Custom Agent: think_step action=%s", action)

        if action == "create_data_agent":
            agent_name = thought.get("agent_name", "custom-data-agent")
            agent_desc = thought.get("agent_description", "")
            logger.info("Custom Agent: creating data agent name=%s, description=%s, reasoning=%s", agent_name, agent_desc, thought.get("reasoning", ""))
            return AnalysisResponse(
                status="needs_data",
                model=LLM_MODEL,
                analysis=None,
                required_agents=[
                    {
                        "name": agent_name,
                        "description": agent_desc,
                        "type": "data",
                        "source": "web_search",
                        "system_prompt": generate_data_agent_prompt(thought),
                        "temperature": "0.3",
                        "max_tokens": "4096",
                    }
                ],
            )

        if action == "call_tool":
            tool_name = thought.get("tool", "")
            logger.info("Custom Agent: needs built-in tool=%s, reasoning=%s", tool_name, thought.get("reasoning", ""))
            if tool_name in TOOLS_DESCRIPTION:
                return AnalysisResponse(
                    status="needs_data",
                    model=LLM_MODEL,
                    analysis=None,
                    required_agents=[
                        {
                            "name": tool_name,
                            "description": TOOLS_DESCRIPTION[tool_name],
                            "type": "data",
                            "source": "built-in" if tool_name != "web_search" else "web_search",
                            "system_prompt": f"Fetch {tool_name} data for stocks",
                            "temperature": "0.3",
                            "max_tokens": "4096",
                        }
                    ],
                )

        # action == "generate_response" — LLM thinks it can answer without data
        logger.info("Custom Agent: generating response directly (no data needed), reasoning=%s", thought.get("reasoning", ""))
        user_prompt = request.user_prompt or f"Analyze the following stocks: {request.stocks}"
        result = await call_llm(user_prompt, request.system_prompt)
        logger.info("Custom Agent: response complete, status=success")
        return AnalysisResponse(
            status="success",
            analysis=result,
            model=LLM_MODEL,
            agent_name="custom",
        )

    except Exception as e:
        logger.error(f"Custom Agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ── System prompt generator ──

CATEGORY_CONTEXTS = {
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


@router.post("/generate-agent-system-prompt")
async def generate_agent_system_prompt(request: GenerateSystemPromptRequest):
    """Generate a system prompt from agent name, description, and category."""
    try:
        logger.info(f"Generating system prompt for agent: {request.name}")
        category_context = CATEGORY_CONTEXTS.get(request.category, CATEGORY_CONTEXTS["strategy_agent"])
        description_text = request.description.strip() if request.description else ""

        if not description_text:
            meta_prompt = (
                f"You are an expert at creating system prompts for AI agents in a multi-agent trading system.\n\n"
                f"Create a detailed system prompt for an agent with the following characteristics:\n\n"
                f"**Agent Name:** {request.name}\n"
                f"**Category:** {category_context}\n\n"
                f"IMPORTANT: No description was provided, so you must:\n"
                f"1. Infer the agent's purpose and responsibilities from its NAME alone\n"
                f"2. Create a comprehensive, detailed system prompt based on what the name suggests\n"
                f"3. Define clear responsibilities (3-5 bullet points)\n"
                f"4. Specify expected input/output formats\n\n"
                f"The system prompt should:\n"
                f"1. Define the agent's role and expertise clearly\n"
                f"2. List specific responsibilities (3-5 bullet points)\n"
                f"3. Specify the input the agent receives\n"
                f"4. Define the expected output format (JSON structure preferred)\n"
                f"5. Include any relevant domain knowledge\n\n"
                f'Write ONLY the system prompt, nothing else. Start directly with "You are..."'
            )
        else:
            meta_prompt = (
                f"You are an expert at creating system prompts for AI agents in a multi-agent trading system.\n\n"
                f"Create a detailed system prompt for an agent with the following characteristics:\n\n"
                f"**Agent Name:** {request.name}\n"
                f"**Description:** {description_text}\n"
                f"**Category:** {category_context}\n\n"
                f"The system prompt should:\n"
                f"1. Define the agent's role and expertise clearly\n"
                f"2. List specific responsibilities (3-5 bullet points)\n"
                f"3. Specify the input the agent receives\n"
                f"4. Define the expected output format (JSON structure preferred)\n"
                f"5. Include any relevant domain knowledge\n\n"
                f'Write ONLY the system prompt, nothing else. Start directly with "You are..."'
            )

        system_prompt = await call_llm(meta_prompt)

        cleaned_prompt = system_prompt.strip()
        logger.info("Generated system prompt: length=%d", len(cleaned_prompt))
        if not cleaned_prompt:
            raise Exception("AI service generated an empty system prompt. Please try again or provide a description.")
        if len(cleaned_prompt) < 50:
            raise Exception("Generated system prompt is too short. Please provide a more descriptive agent name or add a description.")

        return {"status": "success", "system_prompt": cleaned_prompt}
    except Exception as e:
        logger.error(f"System prompt generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate system prompt: {e}. Please try providing a description for better results.",
        ) from e


# ── Thinking agent ──

@router.post("/think")
async def run_thinking_agent(request: ThinkingAgentRequest):
    """Execute a thinking agent with iterative ReAct-style reasoning loop."""
    try:
        logger.info(f"Running Thinking Agent for {request.stocks}")
        result = await run_thinking_loop(
            stocks=request.stocks,
            system_prompt=request.system_prompt,
            input_data=request.input_data,
            max_iterations=request.max_iterations,
            available_tools=request.available_tools,
        )
        logger.info("Thinking Agent complete: status=%s, iterations=%s", result.get("status"), result.get("iterations_used"))
        return result
    except Exception as e:
        logger.error(f"Thinking Agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
