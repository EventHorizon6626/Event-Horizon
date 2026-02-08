"""Health, root, and model listing endpoints."""

from datetime import datetime

from fastapi import APIRouter, HTTPException

from agents import store
from models import HealthResponse
from services.llm import LLM_MODEL, check_health, list_models

router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="ok",
        model=LLM_MODEL,
        agents_count=len(store.agents),
        timestamp=datetime.now().isoformat(),
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    backend_status = await check_health()
    return HealthResponse(
        status="ok",
        model=LLM_MODEL,
        agents_count=len(store.agents),
        llm_backend_status=backend_status,
        timestamp=datetime.now().isoformat(),
    )


@router.get("/models")
async def get_models():
    try:
        return await list_models()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to list models: {e}")
