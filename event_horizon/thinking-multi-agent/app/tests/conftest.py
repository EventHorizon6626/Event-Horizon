"""Shared fixtures for pipeline integration tests."""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure app package is on sys.path so bare imports (agents, models, …) resolve
APP_DIR = str(Path(__file__).resolve().parent.parent)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from event_horizon.data_pipeline.stage_1.models.schemas import (
    EarningsData,
    Stage1Output,
    WebSearchData,
)
from event_horizon.data_pipeline.stage_2.models.schemas import (
    NormalizedSymbolData,
    Stage2Output,
)
from event_horizon.data_pipeline.stage_3.models.schemas import (
    Stage3Output,
    SymbolFeatures,
)


# ---------------------------------------------------------------------------
# Mock-data factories
# ---------------------------------------------------------------------------


def make_symbol_features(symbol: str = "AAPL", sentiment: str = "bullish") -> SymbolFeatures:
    """Return a realistic SymbolFeatures with sensible defaults."""
    return SymbolFeatures(
        symbol=symbol,
        market_sentiment=sentiment,
        sentiment_confidence=0.85,
        sentiment_reasoning="Strong earnings beat expectations",
        technical_signal="buy",
        technical_confidence=0.78,
        technical_reasoning="RSI oversold, MACD crossover",
        fundamental_health="strong",
        fundamental_confidence=0.82,
        fundamental_reasoning="P/E below sector average, revenue growing",
        key_patterns=["bullish divergence", "volume spike"],
        risk_factors=["high valuation", "sector rotation risk"],
        opportunities=["earnings momentum", "market expansion"],
        news_sentiment="positive",
        news_summary="Recent product launch received positive reception",
    )


def make_stage3_result(symbols: list[str]) -> dict:
    """Return dict matching ``Stage3Orchestrator.execute()`` return shape."""
    stage3 = Stage3Output(
        portfolio_id=f"portfolio_{'-'.join(symbols)}",
        symbols=symbols,
        symbol_features={s: make_symbol_features(s) for s in symbols},
    )
    return {"stage3_output": stage3}


def make_stage2_result(symbols: list[str]) -> dict:
    """Return dict matching ``Stage2Orchestrator.execute()`` return shape."""
    stage2 = Stage2Output(
        portfolio_id=f"portfolio_{'-'.join(symbols)}",
        symbols=symbols,
        normalized_data={
            s: NormalizedSymbolData(symbol=s, data_quality_score=0.9)
            for s in symbols
        },
    )
    return {"stage2_output": stage2}


def make_earnings_result(symbols: list[str]) -> dict:
    """Return dict matching ``execute_tool("earnings", …)`` shape."""
    return {
        "earnings_data_by_symbol": {
            s: EarningsData(symbol=s, security_type="stock", name=f"{s} Inc")
            for s in symbols
        }
    }


def make_web_search_result(symbols: list[str]) -> dict:
    """Return dict matching ``search_for_stocks()`` shape."""
    return {
        "status": "success",
        "web_search_data_by_symbol": {
            s: WebSearchData(
                symbol=s,
                query=f"{s} earnings analysis",
                answer=f"{s} had strong earnings this quarter",
                results=[{"title": f"{s} beats estimates", "url": "https://example.com"}],
            )
            for s in symbols
        },
    }


def make_llm_full_response(
    content: str = "AAPL is bullish based on strong fundamentals.",
    reasoning: str = "Based on the earnings data...",
) -> dict:
    """Return dict matching ``call_llm_full()`` shape."""
    return {
        "content": content,
        "reasoning": reasoning,
        "model": "test-model",
        "usage": {"prompt_tokens": 50, "completion_tokens": 50, "total_tokens": 100},
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_agents_file(tmp_path):
    """Patch ``agents.AGENTS_FILE`` to a temp file and reset the global store."""
    agents_path = str(tmp_path / "agents.json")

    import agents as agents_mod

    orig_file = agents_mod.AGENTS_FILE
    agents_mod.AGENTS_FILE = agents_path

    # Reset the singleton store so it picks up the new path
    agents_mod.store.agents = {}

    from seed import seed_builtin_agents

    seed_builtin_agents(agents_mod.store)

    yield agents_path

    # Restore
    agents_mod.AGENTS_FILE = orig_file


@pytest.fixture()
def client(tmp_agents_file):
    """TestClient with patched agent store (built-in agents pre-seeded)."""
    from fastapi.testclient import TestClient

    # The store is already patched and seeded by tmp_agents_file.
    # We need to prevent the lifespan from re-seeding to an old path,
    # so we import app AFTER the store is patched.
    from main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def mock_stage2():
    """Patch Stage2Orchestrator.execute to return canned data."""
    with patch("routers.agents_crud.Stage2Orchestrator") as mock_cls:
        instance = MagicMock()
        instance.execute.side_effect = lambda s1: make_stage2_result(s1.symbols)
        mock_cls.return_value = instance
        yield instance


@pytest.fixture()
def mock_stage3():
    """Patch Stage3Orchestrator.execute to return canned data."""
    with patch("routers.agents_crud.Stage3Orchestrator") as mock_cls:
        instance = MagicMock()
        instance.execute.side_effect = lambda s2: make_stage3_result(s2.symbols)
        mock_cls.return_value = instance
        yield instance


@pytest.fixture()
def mock_execute_tool():
    """Patch execute_tool everywhere it's imported."""
    mock = AsyncMock()
    with (
        patch("routers.agents_crud.execute_tool", mock),
        patch("services.thinking_engine.execute_tool", mock),
        patch("routers.agents_named.execute_tool", mock),
    ):
        yield mock


@pytest.fixture()
def mock_search_for_stocks():
    """Patch search_for_stocks where it's imported (lazy import inside agents_crud)."""
    with patch("services.web_search.search_for_stocks", new_callable=AsyncMock) as m:
        yield m


@pytest.fixture()
def mock_call_llm():
    """Patch call_llm everywhere it's imported."""
    mock = AsyncMock()
    with (
        patch("services.thinking_engine.call_llm", mock),
        patch("routers.agents_named.call_llm", mock),
    ):
        yield mock


@pytest.fixture()
def mock_call_llm_full():
    """Patch call_llm_full everywhere it's imported."""
    mock = AsyncMock()
    with (
        patch("routers.agents_crud.call_llm_full", mock),
        patch("routers.agents_named.call_llm_full", mock),
    ):
        yield mock
