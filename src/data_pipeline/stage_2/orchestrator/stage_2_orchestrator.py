"""
Stage 2 Orchestrator

Coordinates the normalization of Stage 1 heterogeneous data.
"""

import logging
import time
from typing import Any, Dict, List

from event_horizon.data_pipeline.stage_1.models.schemas import Stage1Output
from event_horizon.data_pipeline.stage_2.models.schemas import Stage2Output
from event_horizon.data_pipeline.stage_2.normalizer import DataNormalizer


class Stage2Orchestrator:
    """
    Stage 2 Orchestrator - Data Normalization Coordination

    Responsibilities:
    - Normalizes heterogeneous Stage 1 data
    - Creates unified data structure per symbol
    - Calculates quality metrics
    - Produces Stage 2 output ready for LLM processing

    Architecture Pattern: Sequential (Symbol-by-Symbol)
    - Processes each symbol independently
    - Aggregates into unified Stage2Output
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Stage 2 Orchestrator

        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or {}
        self.logger = logging.getLogger("data_pipeline.stage_2.orchestrator")
        self.normalizer = DataNormalizer()

        self.logger.info("Stage 2 Orchestrator initialized")

    def execute(self, stage1_output: Stage1Output) -> Dict[str, Any]:
        """
        Execute Stage 2 normalization

        Args:
            stage1_output: Complete Stage 1 output with heterogeneous data

        Returns:
            Dict containing Stage2Output with normalized data
        """
        start_time = time.time()

        self.logger.info(
            f"Starting Stage 2 normalization for portfolio {stage1_output.portfolio_id}"
        )
        self.logger.info(f"Symbols: {stage1_output.symbols}")

        # Initialize Stage2Output
        stage2_output = Stage2Output(
            portfolio_id=stage1_output.portfolio_id,
            symbols=stage1_output.symbols,
        )

        # Normalize data for each symbol
        all_errors = []
        symbols_with_complete_data = []
        symbols_with_partial_data = []
        symbols_with_errors = []

        for symbol in stage1_output.symbols:
            try:
                normalized_data = self.normalizer.normalize_symbol_data(
                    symbol, stage1_output
                )

                stage2_output.normalized_data[symbol] = normalized_data

                # Categorize symbol based on quality
                if normalized_data.data_quality_score >= 0.9:
                    symbols_with_complete_data.append(symbol)
                elif normalized_data.data_quality_score >= 0.5:
                    symbols_with_partial_data.append(symbol)
                else:
                    symbols_with_errors.append(symbol)

                if normalized_data.has_errors:
                    for error in normalized_data.errors:
                        all_errors.append({"symbol": symbol, "error": error})

            except Exception as e:
                self.logger.error(f"Failed to normalize {symbol}: {str(e)}")
                all_errors.append(
                    {"symbol": symbol, "error": f"Normalization failed: {str(e)}"}
                )
                symbols_with_errors.append(symbol)

        # Calculate overall quality score
        if stage2_output.normalized_data:
            total_quality = sum(
                data.data_quality_score
                for data in stage2_output.normalized_data.values()
            )
            stage2_output.overall_quality_score = total_quality / len(
                stage2_output.normalized_data
            )
        else:
            stage2_output.overall_quality_score = 0.0

        # Update metadata
        stage2_output.execution_time_seconds = time.time() - start_time
        stage2_output.errors = all_errors
        stage2_output.symbols_with_complete_data = symbols_with_complete_data
        stage2_output.symbols_with_partial_data = symbols_with_partial_data
        stage2_output.symbols_with_errors = symbols_with_errors

        # Determine overall status
        if not stage2_output.normalized_data:
            stage2_output.status = "failed"
        elif symbols_with_errors:
            stage2_output.status = "partial_success"
        else:
            stage2_output.status = "success"

        self.logger.info(
            f"Stage 2 normalization completed in {stage2_output.execution_time_seconds:.2f}s"
        )
        self.logger.info(f"Status: {stage2_output.status}")
        self.logger.info(
            f"Quality score: {stage2_output.overall_quality_score:.2f}"
        )
        self.logger.info(
            f"Complete data: {len(symbols_with_complete_data)}, "
            f"Partial: {len(symbols_with_partial_data)}, "
            f"Errors: {len(symbols_with_errors)}"
        )

        return {
            "status": stage2_output.status,
            "stage2_output": stage2_output,
            "execution_time_seconds": stage2_output.execution_time_seconds,
            "overall_quality_score": stage2_output.overall_quality_score,
            "errors": all_errors,
        }
