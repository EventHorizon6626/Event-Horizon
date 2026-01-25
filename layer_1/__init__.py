"""
Layer 1: Data Retrieval Layer

This layer is responsible for collecting heterogeneous data from various sources.
Each agent specializes in ONE data source and operates independently.

Architecture:
- agents/: Specialized data retrieval agents (News, Earnings, Charts, etc.)
- models/: Data schemas and output models
- orchestrator/: Parallel execution and coordination logic

Output: Raw, heterogeneous data in agent-specific formats
"""

from layer_1.orchestrator.layer_1_orchestrator import Layer1Orchestrator

__all__ = ["Layer1Orchestrator"]
