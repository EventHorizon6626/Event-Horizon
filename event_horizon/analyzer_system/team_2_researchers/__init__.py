"""
Team 2: Researcher Team

Bull vs Bear debate for investment thesis development.

Agents:
- Bull Researcher: Advocate for long positions, growth opportunities
- Bear Researcher: Identify risks, overvaluation, downside scenarios
- Research Manager: Facilitate debate, synthesize perspectives

🎯 OPIK INTEGRATION:
- Full debate flow traced (Bull → Bear → Manager)
- Each agent's reasoning captured
- Token usage per debate tracked
- Evaluation infrastructure ready

Output: Investment thesis with bull/bear cases and probability-weighted scenarios

Status: IMPLEMENTED ✅ (with Opik!)
"""

from event_horizon.analyzer_system.team_2_researchers.orchestrator import Team2Orchestrator
from event_horizon.analyzer_system.team_2_researchers.models.schemas import (
    Team2Output,
    InvestmentThesis,
    BullArgument,
    BearArgument,
)

__all__ = ["Team2Orchestrator", "Team2Output", "InvestmentThesis", "BullArgument", "BearArgument"]
