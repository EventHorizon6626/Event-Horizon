"""Unified Event-Horizon Financial Analysis API."""

from dotenv import load_dotenv
load_dotenv()

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents import store
from seed import seed_builtin_agents

logging.basicConfig(level=os.getenv("LOG_LEVEL", "info").upper())
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_builtin_agents(store)
    logger.info(f"App ready — {len(store.agents)} agents loaded")
    yield


app = FastAPI(
    title="Event Horizon AI — Unified Financial Analysis API",
    description=(
        "Multi-agent financial analysis powered by any OpenAI-compatible LLM backend.\n\n"
        "**Create specialized agents** with custom system prompts, then use them to analyze data.\n\n"
        "Workflow: `POST /agents` → `POST /agents/{agent_id}/analyze`"
    ),
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers — order matters: named agents before CRUD (slug vs {agent_id})
from routers import agents_crud, agents_named, analysis, data_pipeline, health  # noqa: E402

app.include_router(health.router)
app.include_router(data_pipeline.router)
app.include_router(agents_named.router)
app.include_router(agents_crud.router)
app.include_router(analysis.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8030)
