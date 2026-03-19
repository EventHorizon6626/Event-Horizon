"""
Analyzer System

Makes intelligent trading decisions from Stage 3 feature vectors.

Available Analyzers:
- Bull-Bear Analyzer: Coupled debate between bull and bear perspectives
- (More analyzers can be added: Risk Manager, Sentiment Analyzer, etc.)

Input: Stage3Output (feature vectors)
Output: Trading decisions and execution plans

Status: IN DEVELOPMENT
"""

# Currently implemented analyzers
from event_horizon.analyzer_system.bull_bear_analyzer import (
    BullBearAnalysisOutput,
    BullBearAnalyzer,
)

__all__ = [
    "BullBearAnalyzer",
    "BullBearAnalysisOutput",
]
