"""Convert raw data-agent outputs into Stage 3 SymbolFeatures via the EH pipeline."""

import dataclasses
import logging
import os
from typing import Any, Dict, List

from event_horizon.data_pipeline.stage_1.models.schemas import (
    ChartData,
    EarningsData,
    FundamentalsData,
    NewsData,
    Stage1Output,
    TechnicalData,
)
from event_horizon.data_pipeline.stage_2.orchestrator.stage_2_orchestrator import Stage2Orchestrator
from event_horizon.data_pipeline.stage_3.models.schemas import SymbolFeatures
from event_horizon.data_pipeline.stage_3.orchestrator.stage_3_orchestrator import Stage3Orchestrator

logger = logging.getLogger(__name__)

# Map display names / aliases → canonical tool name used by Stage1Output fields
_NAME_ALIASES: Dict[str, str] = {
    "candlestick": "candlestick",
    "Candlestick": "candlestick",
    "chart": "candlestick",
    "earnings": "earnings",
    "Earnings": "earnings",
    "news": "news",
    "News": "news",
    "technical": "technical",
    "Technical": "technical",
    "fundamentals": "fundamentals",
    "Fundamentals": "fundamentals",
}

# Map canonical tool name → (Stage1Output field name, dataclass type, per-symbol key in raw output)
_TOOL_TO_STAGE1 = {
    "candlestick": ("chart_data", ChartData, "chart_data_by_symbol"),
    "earnings": ("earnings_data", EarningsData, "earnings_data_by_symbol"),
    "news": ("news_data", NewsData, "news_data_by_symbol"),
    "technical": ("technical_data", TechnicalData, "technical_data_by_symbol"),
    "fundamentals": ("fundamentals_data", FundamentalsData, "fundamentals_data_by_symbol"),
}


def _safe_construct(cls, data: dict):
    """Construct a dataclass instance, filtering to valid fields only."""
    valid = {f.name for f in dataclasses.fields(cls)}
    filtered = {k: v for k, v in data.items() if k in valid}
    return cls(**filtered)


def _normalize_raw_key(key: str) -> str:
    """Resolve a raw_data key to a canonical tool name."""
    return _NAME_ALIASES.get(key, key.lower())


def process_raw_to_features(stocks: List[str], raw_data: dict) -> Dict[str, SymbolFeatures]:
    """Process raw data-agent outputs through Stage 1 → 2 → 3 pipeline.

    Args:
        stocks: List of stock symbols (e.g. ["AAPL", "MSFT"]).
        raw_data: Dict keyed by agent name/display-name, each value is
                  the raw JSON output from that data agent endpoint.

    Returns:
        Dict mapping symbol → SymbolFeatures ready for the analyzer.
    """
    logger.info("process_raw_to_features: stocks=%s, raw_data keys=%s", stocks, list(raw_data.keys()))

    portfolio_id = f"portfolio_{'-'.join(stocks)}"

    # Build Stage1Output from raw agent outputs
    stage1 = Stage1Output(portfolio_id=portfolio_id, symbols=stocks)

    for raw_key, agent_output in raw_data.items():
        canonical = _normalize_raw_key(raw_key)
        mapping = _TOOL_TO_STAGE1.get(canonical)
        if not mapping:
            logger.warning("process_raw_to_features: unknown agent key '%s' (canonical='%s'), skipping", raw_key, canonical)
            continue

        field_name, dataclass_cls, per_symbol_key = mapping

        # agent_output is the full response dict from the data endpoint
        if not isinstance(agent_output, dict):
            logger.warning("process_raw_to_features: agent '%s' output is not a dict, skipping", raw_key)
            continue

        # The per-symbol data lives under a known key (e.g. "chart_data_by_symbol")
        by_symbol = agent_output.get(per_symbol_key, {})
        if not by_symbol:
            logger.warning("process_raw_to_features: no '%s' in agent '%s' output, skipping", per_symbol_key, raw_key)
            continue

        stage1_field = getattr(stage1, field_name)
        for sym, sym_data in by_symbol.items():
            if isinstance(sym_data, dict):
                sym_data.setdefault("symbol", sym)
                stage1_field[sym] = _safe_construct(dataclass_cls, sym_data)
            else:
                stage1_field[sym] = sym_data

        stage1.agents_executed.append(canonical)
        logger.info("process_raw_to_features: reconstructed %d symbols for '%s'", len(by_symbol), canonical)

    # Run Stage 2 (normalization)
    logger.info("process_raw_to_features: running Stage 2 normalization")
    stage2_result = Stage2Orchestrator().execute(stage1)
    stage2_output = stage2_result["stage2_output"]
    logger.info("process_raw_to_features: Stage 2 status=%s, quality=%.2f", stage2_result["status"], stage2_result.get("overall_quality_score", 0))

    # Run Stage 3 (LLM feature extraction)
    stage3_config = {
        "llm_model": os.getenv("LLM_MODEL", "mistralai/Ministral-3-14B-Reasoning-2512"),
        "temperature": 0.3,
        "enable_opik": False,
    }
    llm_base = os.getenv("LLM_BASE_URL")
    if llm_base:
        stage3_config["llm_base_url"] = llm_base
    llm_key = os.getenv("LLM_API_KEY")
    if llm_key:
        stage3_config["llm_api_key"] = llm_key

    logger.info("process_raw_to_features: running Stage 3 feature extraction")
    stage3_result = Stage3Orchestrator(config=stage3_config).execute(stage2_output)
    stage3_output = stage3_result["stage3_output"]
    logger.info(
        "process_raw_to_features: Stage 3 status=%s, llm_calls=%d, tokens=%d",
        stage3_result["status"],
        stage3_result.get("total_llm_calls", 0),
        stage3_result.get("total_tokens_used", 0),
    )

    return stage3_output.symbol_features
