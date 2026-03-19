"""
Stage 2: Normalization & Standardization

Transforms heterogeneous Stage 1 data into a standardized "DNA" dataset.

Responsibilities:
- Time synchronization across data sources
- Symbol mapping and normalization
- Format standardization to tabular schema
- Data quality handling (missing values, outliers)

Input: Stage1Output (heterogeneous data)
Output: Stage2Output (normalized tabular data)

Status: IMPLEMENTED ✅
"""

from event_horizon.data_pipeline.stage_2.orchestrator import Stage2Orchestrator
from event_horizon.data_pipeline.stage_2.models.schemas import Stage2Output, NormalizedSymbolData

__all__ = ["Stage2Orchestrator", "Stage2Output", "NormalizedSymbolData"]
