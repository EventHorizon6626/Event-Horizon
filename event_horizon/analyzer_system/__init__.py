"""
Analyzer System

Makes intelligent trading decisions from Stage 3 feature vectors.

Available Agents (flexible, can add more):
- Bull Researcher: Arguments for long positions, growth opportunities
- Bear Researcher: Arguments for short positions, risk analysis
- Research Manager: Synthesizes bull/bear debate into thesis
- (More agents can be added: Risk Analyzer, Sentiment Analyzer, etc.)

Input: Stage3Output (feature vectors)
Output: Trading decisions and execution plans

Status: IN DEVELOPMENT
"""

# Currently implemented agents
from event_horizon.analyzer_system.team_2_researchers import (
    BullResearcher,
    BearResearcher,
    ResearchManager,
    Team2Orchestrator,
)

__all__ = [
    "BullResearcher",
    "BearResearcher",
    "ResearchManager",
    "Team2Orchestrator",
]
