"""
Stage 1: Data Retrieval

Collects heterogeneous data from multiple external sources.
Each agent specializes in ONE data source and operates independently.

Architecture:
- agents/: Specialized data retrieval agents (News, Earnings, Charts, Technical, Fundamentals)
- services/: Low-level API clients for external data sources
- models/: Data schemas and output models
- orchestrator/: Parallel execution and coordination logic

Output: Raw, heterogeneous data in agent-specific formats
Next: Stage 2 will normalize this data into unified "DNA" format
"""

from data_pipeline.stage_1.orchestrator.stage_1_orchestrator import Stage1Orchestrator

__all__ = ["Stage1Orchestrator"]
