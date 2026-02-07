"""
Analyzer System (System 2)

Makes intelligent trading decisions from Stage 3 feature vectors.

Available Analyzers:
- Bull-Bear Analyzer: Coupled debate between bull and bear perspectives
  - Bull Researcher: Arguments for long positions, growth opportunities
  - Bear Researcher: Arguments for short positions, risk analysis
  - Research Manager: Synthesizes bull/bear debate into thesis
- (More analyzers can be added: Risk Manager, Sentiment Analyzer, etc.)

Input: Stage3Output (feature vectors)
Output: Trading decisions and execution plans

Status: IN DEVELOPMENT
"""

# Currently implemented analyzers
from event_horizon.analyzer_system.bull_bear_analyzer import (
    BearResearcher,
    BullBearAnalysisOutput,
    BullBearAnalyzer,
    BullResearcher,
    ResearchManager,
)

__all__ = [
    "BullBearAnalyzer",
    "BullBearAnalysisOutput",
    "BullResearcher",
    "BearResearcher",
    "ResearchManager",
]
