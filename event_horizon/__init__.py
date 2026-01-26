"""
Event Horizon AI - Multi-Agent Trading System

This package contains the core components of the Event Horizon trading system:
- data_pipeline: Multi-stage data collection and processing pipeline
- analyzer_system: Multi-agent analysis and decision-making system

Architecture:
    Stage 1 (Data Retrieval) → Stage 2 (Normalization) → Stage 3 (Feature Extraction)
                                        ↓
                            Analyzer System (Multi-Agent Decision Making)
"""

__version__ = "0.1.0"
__author__ = "Event Horizon AI"

# Make key components easily accessible
from event_horizon.data_pipeline import Stage1Orchestrator
from event_horizon.core import BaseAgent

__all__ = [
    "Stage1Orchestrator",
    "BaseAgent",
]
