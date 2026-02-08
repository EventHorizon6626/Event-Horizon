"""Pre-register built-in agents on startup."""

import logging

from agents import AgentStore

logger = logging.getLogger(__name__)

BUILTIN_AGENTS = [
    # ── Data agents (type=data, source=built-in) ──
    {
        "agent_id": "candlestick",
        "name": "candlestick",
        "description": "OHLCV price data",
        "agent_type": "data",
        "source": "built-in",
        "system_prompt": "Fetch OHLCV candlestick price data for the given stocks.",
        "deletable": False,
    },
    {
        "agent_id": "earnings",
        "name": "earnings",
        "description": "Financial reports & earnings",
        "agent_type": "data",
        "source": "built-in",
        "system_prompt": "Fetch quarterly earnings, revenue, and financial reports for the given stocks.",
        "deletable": False,
    },
    {
        "agent_id": "news",
        "name": "news",
        "description": "News articles & headlines",
        "agent_type": "data",
        "source": "built-in",
        "system_prompt": "Fetch recent news articles and headlines for the given stocks.",
        "deletable": False,
    },
    # ── Analysis agents (type=analysis) ──
    {
        "agent_id": "bull-bear-analyzer",
        "name": "bull-bear-analyzer",
        "description": "Coupled bull/bear debate — builds bullish case, bearish counter-argument, then synthesizes thesis",
        "agent_type": "analysis",
        "source": "built-in",
        "system_prompt": (
            "You are a Bull-Bear Analyzer. Conduct an internal debate:\n"
            "1. Build the strongest BULLISH case — growth opportunities, positive catalysts, competitive advantages, upside potential.\n"
            "2. Build the strongest BEARISH counter-argument — risks, competitive threats, overvaluation, negative trends.\n"
            "3. Synthesize both sides into a final balanced investment thesis.\n\n"
            "Return JSON with: recommendation (STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL), confidence (0-1), "
            "bull_case, bear_case, synthesis, key_catalysts, key_risks, decisive_factors."
        ),
        "deletable": False,
    },
    {
        "agent_id": "risk-manager",
        "name": "risk-manager",
        "description": "Evaluates portfolio risk, volatility, and liquidity before approving transactions",
        "agent_type": "analysis",
        "source": "built-in",
        "system_prompt": (
            "You are a Risk Manager. Evaluate portfolio risk, volatility, and liquidity before approving transactions.\n"
            "Focus on: VaR, drawdown limits, position limits, liquidity risk.\n\n"
            "Provide analysis in JSON:\n"
            "{\n"
            '    "risk_assessment": "APPROVED" | "REJECTED" | "CONDITIONAL",\n'
            '    "risk_score": 1-10,\n'
            '    "key_risks": ["risk1", "risk2"],\n'
            '    "var_impact": "estimated VaR change",\n'
            '    "conditions": ["condition if conditional approval"],\n'
            '    "risk_mitigation": ["mitigation1", "mitigation2"]\n'
            "}"
        ),
        "deletable": False,
    },
]


def seed_builtin_agents(store: AgentStore) -> None:
    """Register all built-in agents. Idempotent — skips existing IDs."""
    for defn in BUILTIN_AGENTS:
        agent = store.create(
            name=defn["name"],
            description=defn["description"],
            system_prompt=defn["system_prompt"],
            agent_type=defn["agent_type"],
            source=defn.get("source"),
            agent_id=defn["agent_id"],
            deletable=defn.get("deletable", False),
        )
        logger.info(f"Seeded built-in agent: {agent['agent_id']} ({agent['name']})")
    logger.info(f"Built-in agents seeded: {len(BUILTIN_AGENTS)} total")
