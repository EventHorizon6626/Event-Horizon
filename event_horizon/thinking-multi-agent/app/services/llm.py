"""Unified LLM client — works with local vLLM or any OpenAI-compatible API."""

import json
import logging
import os
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8000")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "mistralai/Ministral-3-14B-Reasoning-2512")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "300"))


def _headers() -> dict:
    h = {"Content-Type": "application/json"}
    if LLM_API_KEY:
        h["Authorization"] = f"Bearer {LLM_API_KEY}"
    return h


def _endpoint() -> str:
    base = LLM_BASE_URL.rstrip("/")
    if base.endswith("/v1"):
        return f"{base}/chat/completions"
    return f"{base}/v1/chat/completions"


async def call_llm(
    prompt: str,
    system_prompt: str = None,
    temperature: float = 0.7,
    max_tokens: int = 3072,
) -> str:
    """Simple prompt->text helper. Replaces call_gemini()."""
    messages: List[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    logger.info(
        "call_llm: endpoint=%s, model=%s, prompt_len=%d, has_system_prompt=%s, messages=%d, temperature=%.2f, max_tokens=%d",
        _endpoint(), LLM_MODEL, len(prompt), system_prompt is not None, len(messages), temperature, max_tokens,
    )
    logger.debug("call_llm: full prompt:\n%s", prompt)

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            resp = await client.post(_endpoint(), json=payload, headers=_headers())
            resp.raise_for_status()
            result = resp.json()
    except httpx.HTTPStatusError as e:
        logger.error("call_llm HTTP error: status=%d, response=%s", e.response.status_code, e.response.text[:1000])
        raise
    except Exception as e:
        logger.error("call_llm failed: %s", e)
        raise

    content = result["choices"][0]["message"].get("content", "")
    usage = result.get("usage", {})
    logger.info(
        "call_llm complete: model=%s, response_len=%d, usage=%s",
        LLM_MODEL, len(content), usage,
    )
    logger.info("call_llm response:\n%s", content)
    return content


async def call_llm_full(
    messages: List[Dict[str, str]],
    temperature: float = 1.0,
    max_tokens: int = 3072,
) -> Dict[str, Any]:
    """Full chat completion with reasoning extraction. Replaces _run_analysis()."""
    logger.info(
        "call_llm_full: endpoint=%s, model=%s, messages=%d, temperature=%.2f, max_tokens=%d",
        _endpoint(), LLM_MODEL, len(messages), temperature, max_tokens,
    )
    for i, msg in enumerate(messages):
        logger.info("call_llm_full: message[%d] role=%s, content_len=%d", i, msg.get("role"), len(msg.get("content", "")))
        logger.debug("call_llm_full: message[%d] content:\n%s", i, msg.get("content", ""))

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            resp = await client.post(_endpoint(), json=payload, headers=_headers())
            resp.raise_for_status()
            result = resp.json()
    except httpx.HTTPStatusError as e:
        logger.error("call_llm_full HTTP error: status=%d, response=%s", e.response.status_code, e.response.text[:1000])
        raise
    except Exception as e:
        logger.error("call_llm_full failed: %s", e)
        raise

    choice = result["choices"][0]["message"]
    usage = result.get("usage")
    model = result.get("model", LLM_MODEL)
    has_reasoning = choice.get("reasoning_content") is not None
    content = choice.get("content", "")
    reasoning = choice.get("reasoning_content")

    logger.info(
        "call_llm_full complete: model=%s, has_reasoning=%s, content_len=%d, reasoning_len=%d, usage=%s",
        model, has_reasoning, len(content), len(reasoning) if reasoning else 0, usage,
    )
    logger.info("call_llm_full response content:\n%s", content)
    if reasoning:
        logger.info("call_llm_full reasoning:\n%s", reasoning)

    return {
        "reasoning": reasoning,
        "content": content,
        "usage": usage,
        "model": model,
    }


async def stream_llm(
    messages: List[Dict[str, str]],
    temperature: float = 1.0,
    max_tokens: int = 3072,
) -> AsyncGenerator[str, None]:
    """Stream SSE lines from the LLM backend."""
    logger.info("stream_llm: starting, messages=%d, temperature=%.2f, model=%s", len(messages), temperature, LLM_MODEL)
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    try:
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            async with client.stream(
                "POST", _endpoint(), json=payload, headers=_headers()
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        yield line + "\n\n"
        logger.info("stream_llm complete")
    except Exception as e:
        logger.error("stream_llm failed: %s", e)
        raise


async def check_health() -> str:
    """Check LLM backend health. Returns status string."""
    logger.debug("check_health: checking LLM backend at %s", LLM_BASE_URL)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{LLM_BASE_URL.rstrip('/')}/health", headers=_headers()
            )
            status = "healthy" if resp.status_code == 200 else f"unhealthy ({resp.status_code})"
            logger.info("check_health: %s", status)
            return status
    except Exception as e:
        logger.warning("check_health: unreachable: %s", e)
        return f"unreachable: {e}"


async def list_models() -> dict:
    """List models available on the LLM backend."""
    logger.debug("list_models: fetching from %s", LLM_BASE_URL)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{LLM_BASE_URL.rstrip('/')}/v1/models", headers=_headers()
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info("list_models: found %d models", len(data.get("data", [])))
            return data
    except Exception as e:
        logger.error("list_models failed: %s", e)
        raise
