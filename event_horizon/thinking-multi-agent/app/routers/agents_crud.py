"""Agent CRUD + unified analyze dispatch."""

import logging

from fastapi import APIRouter, HTTPException

from agents import store
from models import AgentResponse, AnalysisRequest, AnalysisResponse, CreateAgentRequest
from prompts import build_user_prompt
from services.llm import LLM_MODEL, call_llm_full

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

    # Data agents don't run LLM — return a data_source spec
    if agent.get("type") == "data":
        stocks = request.stocks or []
        agent_name = agent["name"].lower()
        agent_source = agent.get("source", "custom")

        builtin_specs = {
            "candlestick": {"output_key": "chart_data_by_symbol", "provides": "OHLCV price data"},
            "earnings": {"output_key": "earnings_data_by_symbol", "provides": "quarterly earnings and financials"},
            "news": {"output_key": "news_data_by_symbol", "provides": "recent news articles"},
            "technical": {"output_key": "technical_data_by_symbol", "provides": "technical indicators (RSI, MACD, SMA)"},
            "fundamentals": {"output_key": "fundamentals_data_by_symbol", "provides": "fundamental metrics (P/E, ROE, debt)"},
        }

        if agent_source == "built-in" and agent_name in builtin_specs:
            spec = builtin_specs[agent_name]
            data_source_spec = {
                "agent": agent_name, "source": "built-in", "pipeline": "stage_1",
                "output_key": spec["output_key"], "provides": spec["provides"], "symbols": stocks,
            }
        else:
            data_source_spec = {
                "agent": agent_name, "source": "custom",
                "description": agent.get("description", ""), "symbols": stocks,
            }

        return AnalysisResponse(
            status="data_source", agent_id=agent_id, agent_name=agent["name"],
            analysis=None, reasoning=None, model=LLM_MODEL,
            provider="eh-multi-agent", data_source=data_source_spec,
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
