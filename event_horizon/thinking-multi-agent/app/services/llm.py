"""Unified LLM client — works with local vLLM or any OpenAI-compatible API."""

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


async def call_llm(prompt: str, system_prompt: str = None) -> str:
    """Simple prompt→text helper. Replaces call_gemini()."""
    messages: List[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4096,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        resp = await client.post(_endpoint(), json=payload, headers=_headers())
        resp.raise_for_status()
        result = resp.json()

    return result["choices"][0]["message"].get("content", "")


async def call_llm_full(
    messages: List[Dict[str, str]],
    temperature: float = 1.0,
    max_tokens: int = 4096,
) -> Dict[str, Any]:
    """Full chat completion with reasoning extraction. Replaces _run_analysis()."""
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        resp = await client.post(_endpoint(), json=payload, headers=_headers())
        resp.raise_for_status()
        result = resp.json()

    choice = result["choices"][0]["message"]

    return {
        "reasoning": choice.get("reasoning_content"),
        "content": choice.get("content", ""),
        "usage": result.get("usage"),
        "model": result.get("model", LLM_MODEL),
    }


async def stream_llm(
    messages: List[Dict[str, str]],
    temperature: float = 1.0,
    max_tokens: int = 4096,
) -> AsyncGenerator[str, None]:
    """Stream SSE lines from the LLM backend."""
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        async with client.stream(
            "POST", _endpoint(), json=payload, headers=_headers()
        ) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    yield line + "\n\n"


async def check_health() -> str:
    """Check LLM backend health. Returns status string."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{LLM_BASE_URL.rstrip('/')}/health", headers=_headers()
            )
            return "healthy" if resp.status_code == 200 else f"unhealthy ({resp.status_code})"
    except Exception as e:
        return f"unreachable: {e}"


async def list_models() -> dict:
    """List models available on the LLM backend."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{LLM_BASE_URL.rstrip('/')}/v1/models", headers=_headers()
        )
        resp.raise_for_status()
        return resp.json()
