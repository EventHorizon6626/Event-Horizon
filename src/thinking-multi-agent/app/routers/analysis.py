"""Default /analyze and /analyze/stream endpoints."""

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models import AnalysisRequest, AnalysisResponse
from prompts import SYSTEM_PROMPT, build_user_prompt
from services.llm import LLM_MODEL, call_llm_full, stream_llm

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """Analyze using the default financial analyst prompt.

    If stocks are provided but no data is available, returns a needs_data
    response listing the EH Stage 1 agents that should be run first.
    """
    logger.info("Analyze request: stocks=%s, task=%s", request.stocks, request.task[:80] if request.task else None)
    has_data = bool(request.financial_data) or bool(request.earnings_data) or bool(request.news_data)
    if not has_data and request.metadata and isinstance(request.metadata, dict):
        has_data = any(bool(v) for v in request.metadata.values())

    if request.stocks and not has_data:
        symbols_str = ", ".join(request.stocks)
        return AnalysisResponse(
            status="needs_data", analysis=None, reasoning=None,
            model=LLM_MODEL, provider="eh-multi-agent",
            required_agents=[
                {"type": "earnings", "description": f"Need quarterly earnings data for {symbols_str}"},
                {"type": "candlestick", "description": f"Need OHLCV price data for {symbols_str}"},
                {"type": "news", "description": f"Need recent news for {symbols_str}"},
                {"type": "technical", "description": f"Need technical indicators for {symbols_str}"},
                {"type": "fundamentals", "description": f"Need fundamental metrics for {symbols_str}"},
            ],
        )

    system_prompt = request.system_prompt if request.system_prompt else SYSTEM_PROMPT

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
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    temperature = request.temperature if request.temperature is not None else 1.0
    max_tokens = request.max_tokens if request.max_tokens is not None else 4096

    try:
        result = await call_llm_full(messages, temperature=temperature, max_tokens=max_tokens)
    except Exception as e:
        logger.error("Analyze failed: %s", e)
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

    logger.info("Analyze complete: stocks=%s, status=success", request.stocks)
    return AnalysisResponse(
        reasoning=result["reasoning"], analysis=result["content"],
        model=result["model"], status="success",
        provider="eh-multi-agent", usage=result["usage"],
    )


@router.post("/analyze/stream")
async def analyze_stream(request: AnalysisRequest):
    """Stream the analysis response as server-sent events."""
    logger.info("Analyze stream request: stocks=%s", request.stocks)
    system_prompt = request.system_prompt if request.system_prompt else SYSTEM_PROMPT

    user_prompt = build_user_prompt(
        task=request.task,
        financial_data=request.financial_data,
        earnings_data=request.earnings_data,
        news_data=request.news_data,
        additional_context=request.additional_context,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    temperature = request.temperature if request.temperature is not None else 1.0
    max_tokens = request.max_tokens if request.max_tokens is not None else 4096

    logger.debug("Analyze stream: starting SSE response")
    return StreamingResponse(
        stream_llm(messages, temperature=temperature, max_tokens=max_tokens),
        media_type="text/event-stream",
    )
