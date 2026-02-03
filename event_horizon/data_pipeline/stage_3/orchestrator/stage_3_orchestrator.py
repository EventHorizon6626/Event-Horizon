"""
Stage 3 Orchestrator

Coordinates LLM-based feature extraction with full Opik observability.
"""

import logging
import time
from typing import Any, Dict

try:
    import opik
    from opik import track
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False

from event_horizon.data_pipeline.stage_2.models.schemas import Stage2Output
from event_horizon.data_pipeline.stage_3.models.schemas import Stage3Output
from event_horizon.data_pipeline.stage_3.extractors import LLMFeatureExtractor


class Stage3Orchestrator:
    """
    Stage 3 Orchestrator - LLM Feature Extraction Coordination

    Responsibilities:
    - Extracts features from normalized Stage 2 data using LLM
    - Tracks all LLM calls with Opik
    - Aggregates features for all symbols
    - Produces Stage 3 output ready for analyzer system

    🎯 OPIK INTEGRATION:
    - Full tracing of LLM pipeline
    - Token usage monitoring
    - Performance metrics
    - Evaluation infrastructure
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Stage 3 Orchestrator

        Args:
            config: Configuration dictionary
                - llm_model: Model to use
                - temperature: LLM temperature
                - opik_project: Opik project name
                - enable_opik: Enable Opik tracking
        """
        self.config = config or {}
        self.logger = logging.getLogger("data_pipeline.stage_3.orchestrator")

        # Initialize feature extractor with Opik
        self.feature_extractor = LLMFeatureExtractor(config=self.config)

        self.enable_opik = self.config.get("enable_opik", True) and OPIK_AVAILABLE

        if self.enable_opik:
            opik_project = self.config.get("opik_project", "event-horizon")
            try:
                opik.configure(project_name=opik_project)
                self.logger.info(f"✓ Opik tracking enabled: {opik_project}")
            except Exception as e:
                self.logger.warning(f"Opik init failed: {e}")
                self.enable_opik = False

        self.logger.info("Stage 3 Orchestrator initialized")

    @track(name="stage3_pipeline", project_name="event-horizon")
    def execute(self, stage2_output: Stage2Output) -> Dict[str, Any]:
        """
        Execute Stage 3 feature extraction

        This entire pipeline is traced by Opik, allowing you to:
        - See all LLM calls in sequence
        - Track total token usage
        - Measure end-to-end performance
        - Evaluate feature quality

        Args:
            stage2_output: Complete Stage 2 normalized output

        Returns:
            Dict containing Stage3Output with LLM-extracted features
        """
        start_time = time.time()

        self.logger.info(
            f"Starting Stage 3 feature extraction for portfolio {stage2_output.portfolio_id}"
        )
        self.logger.info(f"Symbols: {stage2_output.symbols}")

        # Initialize Stage3Output
        stage3_output = Stage3Output(
            portfolio_id=stage2_output.portfolio_id,
            symbols=stage2_output.symbols,
            opik_project_name=self.config.get("opik_project", "event-horizon"),
        )

        # Extract features for each symbol
        all_errors = []
        total_tokens = 0
        total_extraction_time = 0.0
        llm_call_count = 0

        for symbol in stage2_output.symbols:
            if symbol not in stage2_output.normalized_data:
                self.logger.warning(f"{symbol}: No normalized data available, skipping")
                all_errors.append(
                    {"symbol": symbol, "error": "No normalized data"}
                )
                continue

            normalized_data = stage2_output.normalized_data[symbol]

            try:
                # Extract features using LLM (tracked by Opik)
                features = self.feature_extractor.extract_features(
                    symbol, normalized_data
                )

                stage3_output.symbol_features[symbol] = features
                llm_call_count += 1
                total_tokens += features.total_tokens
                total_extraction_time += features.extraction_time_seconds

                if features.has_errors:
                    for error in features.errors:
                        all_errors.append({"symbol": symbol, "error": error})

            except Exception as e:
                self.logger.error(f"{symbol}: Feature extraction failed - {e}")
                all_errors.append(
                    {"symbol": symbol, "error": f"Extraction failed: {str(e)}"}
                )

        # Update Opik tracking metadata
        stage3_output.total_llm_calls = llm_call_count
        stage3_output.total_tokens_used = total_tokens
        stage3_output.average_extraction_time = (
            total_extraction_time / llm_call_count if llm_call_count > 0 else 0.0
        )

        # Update metadata
        stage3_output.execution_time_seconds = time.time() - start_time
        stage3_output.errors = all_errors

        # Determine overall status
        if not stage3_output.symbol_features:
            stage3_output.status = "failed"
        elif all_errors:
            stage3_output.status = "partial_success"
        else:
            stage3_output.status = "success"

        self.logger.info(
            f"Stage 3 feature extraction completed in {stage3_output.execution_time_seconds:.2f}s"
        )
        self.logger.info(f"Status: {stage3_output.status}")
        self.logger.info(
            f"LLM calls: {stage3_output.total_llm_calls}, "
            f"Tokens: {stage3_output.total_tokens_used}, "
            f"Avg time: {stage3_output.average_extraction_time:.2f}s"
        )

        return {
            "status": stage3_output.status,
            "stage3_output": stage3_output,
            "execution_time_seconds": stage3_output.execution_time_seconds,
            "total_llm_calls": stage3_output.total_llm_calls,
            "total_tokens_used": stage3_output.total_tokens_used,
            "errors": all_errors,
        }
