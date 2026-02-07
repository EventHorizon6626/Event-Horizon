"""
Bull-Bear Analyzer

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

from event_horizon.analyzer_system.bull_bear_analyzer.models.schemas import (
    BearArgument,
    BullArgument,
    BullBearAnalysisOutput,
    InvestmentThesis,
)
from event_horizon.analyzer_system.bull_bear_analyzer.orchestrator.bull_bear_orchestrator import BullBearAnalyzer

__all__ = ["BullBearAnalyzer", "BullBearAnalysisOutput", "InvestmentThesis", "BullArgument", "BearArgument"]
