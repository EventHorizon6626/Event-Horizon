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
        logger.info("Running Candlestick agent for stocks=%s, period=%s, timeframe=%s", request.stocks, request.period, request.timeframe)
        result = await execute_tool("candlestick", request.stocks, period=request.period, interval=request.timeframe)
        logger.info("Candlestick agent complete: result_keys=%s", list(result.keys()) if isinstance(result, dict) else type(result).__name__)
        return result
    except Exception as e:
        logger.error("Candlestick agent failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/earnings")
async def run_earnings_agent(request: AgentRequest):
    """Execute Earnings agent for given stocks."""
    try:
        logger.info("Running Earnings agent for stocks=%s", request.stocks)
        result = await execute_tool("earnings", request.stocks)
        logger.info("Earnings agent complete: result_keys=%s", list(result.keys()) if isinstance(result, dict) else type(result).__name__)
        return result
    except Exception as e:
        logger.error("Earnings agent failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/news")
async def run_news_agent(request: AgentRequest):
    """Execute News agent for given stocks."""
    try:
        days = request.days or 7
        logger.info("Running News agent for stocks=%s, days=%d", request.stocks, days)
        result = await execute_tool("news", request.stocks, days_back=days)
        logger.info("News agent complete: result_keys=%s", list(result.keys()) if isinstance(result, dict) else type(result).__name__)
        return result
    except Exception as e:
        logger.error("News agent failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/technical")
async def run_technical_agent(request: AgentRequest):
    """Execute Technical Analysis agent for given stocks."""
    try:
        logger.info("Running Technical agent for stocks=%s, indicators=%s", request.stocks, request.indicators)
        overrides = {}
        if request.indicators:
            overrides["indicators"] = request.indicators
        result = await execute_tool("technical", request.stocks, **overrides)
        logger.info("Technical agent complete: result_keys=%s", list(result.keys()) if isinstance(result, dict) else type(result).__name__)
        return result
    except Exception as e:
        logger.error("Technical agent failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/fundamentals")
async def run_fundamentals_agent(request: AgentRequest):
    """Execute Fundamentals agent for given stocks."""
    try:
        logger.info("Running Fundamentals agent for stocks=%s", request.stocks)
        result = await execute_tool("fundamentals", request.stocks)
        logger.info("Fundamentals agent complete: result_keys=%s", list(result.keys()) if isinstance(result, dict) else type(result).__name__)
        return result
    except Exception as e:
        logger.error("Fundamentals agent failed: %s", e)
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
        logger.info("Bull-Bear Analyzer: converting %d symbol features from raw dicts", len(raw_features))
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
        logger.error("Bull-Bear Analyzer failed: %s", e)
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
        logger.info(
            "=== CUSTOM AGENT START === stocks=%s, has_input_data=%s, has_user_prompt=%s, system_prompt_len=%d",
            request.stocks, request.input_data is not None, request.user_prompt is not None, len(request.system_prompt or ""),
        )
        logger.info("Custom Agent system_prompt:\n%s", request.system_prompt)

        # ── Path A: we already have data from connected nodes ──
        # input_data is expected to be SymbolFeatures (EH DNA) from the pipeline
        if request.input_data:
            logger.info("Custom Agent: Path A — using provided input_data")
            input_data_json = json.dumps(request.input_data, indent=2, default=str)
            logger.info("Custom Agent: input_data keys=%s, total_len=%d", list(request.input_data.keys()) if isinstance(request.input_data, dict) else type(request.input_data).__name__, len(input_data_json))
            logger.debug("Custom Agent: full input_data:\n%s", input_data_json)

            user_prompt = request.user_prompt or f"Analyze the following stocks: {request.stocks}"
            data_summary = input_data_json[:8000]
            if len(input_data_json) > 8000:
                logger.info("Custom Agent: input_data truncated from %d to 8000 chars for LLM prompt", len(input_data_json))

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
            logger.info("Custom Agent: sending %d messages to LLM (system_len=%d, user_len=%d)", len(messages), len(messages[0]["content"]), len(messages[1]["content"]))

            result = await call_llm_full(messages)
            logger.info(
                "Custom Agent: Path A complete — model=%s, content_len=%d, has_reasoning=%s",
                result["model"], len(result.get("content", "")), result.get("reasoning") is not None,
            )
            logger.info("Custom Agent: Path A analysis result:\n%s", result.get("content", "")[:3000])
            if result.get("reasoning"):
                logger.info("Custom Agent: Path A reasoning:\n%s", result["reasoning"][:3000])

            return AnalysisResponse(
                status="success",
                analysis=result["content"],
                reasoning=result.get("reasoning"),
                model=result["model"],
                usage=result.get("usage"),
                agent_name="custom",
            )

        # ── Path B: no data — discover what tools are needed ──
        logger.info("Custom Agent: Path B — running discovery mode (no input_data provided)")
        available_tools = list(TOOLS_DESCRIPTION.keys())
        logger.info("Custom Agent: Path B available_tools=%s", available_tools)

        loop_result = await run_thinking_loop(
            stocks=request.stocks,
            system_prompt=request.system_prompt,
            max_iterations=3,
            available_tools=available_tools,
            discovery_only=True,
        )

        loop_status = loop_result.get("status", "error")
        tools_discovered = loop_result.get("tools_discovered", [])
        iterations = loop_result.get("iterations_used", 0)
        thinking_steps = loop_result.get("thinking_steps", [])
        logger.info(
            "Custom Agent: discovery complete — status=%s, tools_discovered=%s, iterations=%d, steps_count=%d",
            loop_status, tools_discovered, iterations, len(thinking_steps),
        )

        # Log each thinking step
        for i, step in enumerate(thinking_steps):
            logger.info(
                "Custom Agent: thinking step %d — iteration=%s, action=%s, thought=%s",
                i, step.get("iteration"), step.get("action"), step.get("thought"),
            )
            if step.get("tool"):
                logger.info("Custom Agent: thinking step %d — tool=%s", i, step.get("tool"))
            if step.get("suggested_data_agent"):
                logger.info("Custom Agent: thinking step %d — suggested_data_agent=%s", i, json.dumps(step["suggested_data_agent"], default=str))

        # If the loop paused because it needs an exotic/custom data agent
        if loop_status == "paused":
            suggested = loop_result.get("suggested_data_agent", {})
            logger.info(
                "=== CUSTOM AGENT: NEEDS_DATA (exotic) === agent_name=%s, data_type=%s, description=%s",
                suggested.get("name"), suggested.get("data_type"), suggested.get("description"),
            )

            # Combine any standard tools discovered before the pause with the exotic agent
            required_agents = []
            for tool_name in tools_discovered:
                required_agents.append({
                    "name": tool_name,
                    "type": "data",
                    "source": "eh_pipeline",
                    "description": TOOLS_DESCRIPTION.get(tool_name, "data"),
                })
            # Add the exotic/custom data agent
            required_agents.append({
                "name": suggested.get("name", "custom-data-agent"),
                "description": suggested.get("description", ""),
                "type": "data",
                "source": "web_search",
                "system_prompt": suggested.get("suggested_system_prompt", ""),
                "temperature": "0.3",
                "max_tokens": "4096",
            })

            response = AnalysisResponse(
                status="needs_data",
                model=LLM_MODEL,
                analysis=None,
                required_agents=required_agents,
            )
            logger.info(
                "Custom Agent: returning needs_data response — required_agents=%s",
                json.dumps(response.required_agents, default=str),
            )
            return response

        # Standard tools discovered — return needs_data with EH pipeline agents
        if tools_discovered:
            required_agents = []
            for tool_name in tools_discovered:
                required_agents.append({
                    "name": tool_name,
                    "type": "data",
                    "source": "eh_pipeline",
                    "description": TOOLS_DESCRIPTION.get(tool_name, "data"),
                })
            logger.info(
                "=== CUSTOM AGENT: NEEDS_DATA (standard) === required_agents=%s",
                json.dumps(required_agents, default=str),
            )
            return AnalysisResponse(
                status="needs_data",
                model=LLM_MODEL,
                required_agents=required_agents,
            )

        # No tools discovered (LLM said generate_response without needing tools)
        # Fall through to generate a response directly
        logger.info("Custom Agent: Path B — no tools discovered, generating response directly")
        loop_result = await run_thinking_loop(
            stocks=request.stocks,
            system_prompt=request.system_prompt,
            max_iterations=3,
            available_tools=available_tools,
            discovery_only=False,
        )
        final = loop_result.get("final_result", {})
        analysis_text = json.dumps(final, indent=2, default=str) if isinstance(final, dict) else str(final)
        logger.info("Custom Agent: fallback analysis_text_len=%d", len(analysis_text))

        logger.info("=== CUSTOM AGENT COMPLETE === status=success (no tools needed)")
        return AnalysisResponse(
            status="success",
            analysis=analysis_text,
            model=LLM_MODEL,
            agent_name="custom",
        )

    except Exception as e:
        logger.error("Custom Agent failed: %s", e, exc_info=True)
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
        logger.info("Generating system prompt for agent: name=%s, category=%s, description_len=%d", request.name, request.category, len(request.description or ""))
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

        logger.info("System prompt generation: meta_prompt_len=%d", len(meta_prompt))
        system_prompt = await call_llm(meta_prompt)

        cleaned_prompt = system_prompt.strip()
        logger.info("Generated system prompt: length=%d", len(cleaned_prompt))
        logger.info("Generated system prompt content:\n%s", cleaned_prompt)
        if not cleaned_prompt:
            raise Exception("AI service generated an empty system prompt. Please try again or provide a description.")
        if len(cleaned_prompt) < 50:
            raise Exception("Generated system prompt is too short. Please provide a more descriptive agent name or add a description.")

        return {"status": "success", "system_prompt": cleaned_prompt}
    except Exception as e:
        logger.error("System prompt generation failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate system prompt: {e}. Please try providing a description for better results.",
        ) from e


# ── Thinking agent ──

@router.post("/think")
async def run_thinking_agent(request: ThinkingAgentRequest):
    """Execute a thinking agent with iterative ReAct-style reasoning loop."""
    try:
        logger.info(
            "=== THINKING AGENT START === stocks=%s, system_prompt_len=%d, has_input_data=%s, max_iterations=%d, available_tools=%s",
            request.stocks, len(request.system_prompt or ""), request.input_data is not None, request.max_iterations, request.available_tools,
        )
        logger.info("Thinking Agent system_prompt:\n%s", request.system_prompt)
        if request.input_data:
            logger.info("Thinking Agent input_data keys: %s", list(request.input_data.keys()) if isinstance(request.input_data, dict) else type(request.input_data).__name__)

        result = await run_thinking_loop(
            stocks=request.stocks,
            system_prompt=request.system_prompt,
            input_data=request.input_data,
            max_iterations=request.max_iterations,
            available_tools=request.available_tools,
        )

        logger.info(
            "=== THINKING AGENT COMPLETE === status=%s, iterations=%s, tools_used=%s",
            result.get("status"), result.get("iterations_used"), result.get("tools_used"),
        )
        if result.get("final_result"):
            final = result["final_result"]
            logger.info(
                "Thinking Agent final_result keys=%s",
                list(final.keys()) if isinstance(final, dict) else type(final).__name__,
            )
            logger.info("Thinking Agent final_result:\n%s", json.dumps(final, indent=2, default=str) if isinstance(final, dict) else str(final))

        return result
    except Exception as e:
        logger.error("Thinking Agent failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
