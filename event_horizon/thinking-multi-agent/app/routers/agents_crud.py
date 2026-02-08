"""Agent CRUD + unified analyze dispatch."""

import asyncio
import json
import logging

from fastapi import APIRouter, HTTPException

from agents import store
from models import AgentResponse, AnalysisRequest, AnalysisResponse, CreateAgentRequest
from prompts import build_user_prompt
from services.data_agents import execute_tool
from services.llm import LLM_MODEL, call_llm_full

from event_horizon.data_pipeline.stage_1.models.schemas import Stage1Output
from event_horizon.data_pipeline.stage_2.orchestrator.stage_2_orchestrator import Stage2Orchestrator
from event_horizon.data_pipeline.stage_3.orchestrator.stage_3_orchestrator import Stage3Orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents-crud"])


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(request: CreateAgentRequest):
    """Create a new specialized agent with a custom system prompt."""
    agent = store.create(
        name=request.name,
        description=request.description,
        agent_type=request.type,
        source=request.source,
        system_prompt=request.system_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )
    return AgentResponse(**agent)


@router.get("", response_model=list[AgentResponse])
async def list_agents():
    """List all created agents (built-in + user)."""
    return [AgentResponse(**a) for a in store.list_all()]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get details of a specific agent."""
    agent = store.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return AgentResponse(**agent)


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent. Rejects deletion of built-in agents."""
    try:
        if not store.delete(agent_id):
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return {"status": "deleted", "agent_id": agent_id}


@router.post("/{agent_id}/analyze", response_model=AnalysisResponse)
async def analyze_with_agent(agent_id: str, request: AnalysisRequest):
    """Unified dispatch: data agents return data_source spec, analysis agents run LLM."""
    agent = store.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    # Data agents — fetch data and run full Stage 1→2→3 pipeline
    if agent.get("type") == "data":
        stocks = request.stocks or []
        agent_name = agent["name"].lower()
        agent_source = agent.get("source", "custom")

        builtin_names = {"candlestick", "earnings", "news", "technical", "fundamentals"}

        # Map built-in agent names to Stage1Output field names
        AGENT_TO_STAGE1_FIELD = {
            "candlestick": "chart_data",
            "earnings": "earnings_data",
            "news": "news_data",
            "technical": "technical_data",
            "fundamentals": "fundamentals_data",
        }
        # Map agent names to the key in the result dict that holds per-symbol data
        AGENT_TO_RESULT_KEY = {
            "candlestick": "chart_data_by_symbol",
            "earnings": "earnings_data_by_symbol",
            "news": "news_data_by_symbol",
            "technical": "technical_data_by_symbol",
            "fundamentals": "fundamentals_data_by_symbol",
        }

        portfolio_id = f"portfolio_{'-'.join(stocks)}"
        stage1 = Stage1Output(portfolio_id=portfolio_id, symbols=stocks)

        if agent_source == "built-in" and agent_name in builtin_names:
            result = await execute_tool(agent_name, stocks)
            if "error" in result:
                return AnalysisResponse(
                    status="error", agent_id=agent_id, agent_name=agent["name"],
                    analysis=json.dumps(result, default=str), reasoning=None,
                    model=LLM_MODEL, provider="eh-multi-agent",
                )
            result_key = AGENT_TO_RESULT_KEY[agent_name]
            stage1_field = AGENT_TO_STAGE1_FIELD[agent_name]
            if result_key in result:
                setattr(stage1, stage1_field, result[result_key])

        elif agent_source == "web_search":
            from services.web_search import search_for_stocks

            topic = agent.get("description", "") or agent.get("system_prompt", "general")
            result = await search_for_stocks(stocks, topic)
            if result.get("web_search_data_by_symbol"):
                stage1.web_search_data = result["web_search_data_by_symbol"]

        else:
            # Custom data agent — return spec (no built-in executor)
            data_source_spec = {
                "agent": agent_name, "source": "custom",
                "description": agent.get("description", ""), "symbols": stocks,
            }
            return AnalysisResponse(
                status="data_source", agent_id=agent_id, agent_name=agent["name"],
                analysis=None, reasoning=None, model=LLM_MODEL,
                provider="eh-multi-agent", data_source=data_source_spec,
            )

        # Stage 2: Normalize
        s2 = Stage2Orchestrator()
        s2_result = await asyncio.to_thread(s2.execute, stage1)

        # Stage 3: LLM feature extraction
        s3 = Stage3Orchestrator(config={"enable_opik": False})
        s3_result = await asyncio.to_thread(s3.execute, s2_result["stage2_output"])

        stage3_output = s3_result["stage3_output"]
        features_dict = {sym: f.to_dict() for sym, f in stage3_output.symbol_features.items()}

        return AnalysisResponse(
            status="success", agent_id=agent_id, agent_name=agent["name"],
            analysis=json.dumps(features_dict, default=str), reasoning=None,
            model=LLM_MODEL, provider="eh-multi-agent",
        )

    # Analysis agents run LLM
    user_prompt = build_user_prompt(
        task=request.task,
        financial_data=request.financial_data,
        earnings_data=request.earnings_data,
        news_data=request.news_data,
        additional_context=request.additional_context,
        stocks=request.stocks,
        metadata=request.metadata,
    )

    messages = [
        {"role": "system", "content": agent["system_prompt"]},
        {"role": "user", "content": user_prompt},
    ]

    temperature = request.temperature if request.temperature is not None else agent["temperature"]
    max_tokens = request.max_tokens if request.max_tokens is not None else agent["max_tokens"]

    try:
        result = await call_llm_full(messages, temperature=temperature, max_tokens=max_tokens)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

    return AnalysisResponse(
        agent_id=agent_id, agent_name=agent["name"],
        reasoning=result["reasoning"], analysis=result["content"],
        model=result["model"], status="success",
        provider="eh-multi-agent", usage=result["usage"],
    )
