"""
Stage 3: Feature Extraction & Pattern Recognition

Uses LLM to extract non-obvious patterns and generate predictive features.

Responsibilities:
- Pattern recognition in market data
- Sentiment analysis from news
- Technical signal interpretation
- Fundamental health assessment
- Feature vector generation

🎯 OPIK INTEGRATION:
- Full LLM tracing and observability
- Token usage and cost tracking
- Performance monitoring
- Evaluation infrastructure

Input: Stage2Output (normalized data)
Output: Stage3Output (feature vectors + insights)

Status: IMPLEMENTED ✅ (with Opik!)
"""

from event_horizon.data_pipeline.stage_3.orchestrator import Stage3Orchestrator
from event_horizon.data_pipeline.stage_3.models.schemas import Stage3Output, SymbolFeatures

__all__ = ["Stage3Orchestrator", "Stage3Output", "SymbolFeatures"]
