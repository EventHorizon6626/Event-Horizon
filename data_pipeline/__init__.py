"""
Data Processing Pipeline

Transforms raw market data into feature vectors through 3 sequential stages:
- Stage 1: Data Retrieval (heterogeneous data collection) [IMPLEMENTED]
- Stage 2: Normalization (unified "DNA" schema) [PLANNED]
- Stage 3: Feature Extraction (LLM/Neural AI) [PLANNED]

Output: Feature vectors ready for the Decision-Making System
"""

from data_pipeline.stage_1 import Stage1Orchestrator

__all__ = ["Stage1Orchestrator"]
