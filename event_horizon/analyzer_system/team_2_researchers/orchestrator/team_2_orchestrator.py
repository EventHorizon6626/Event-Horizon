"""
Team 2 Orchestrator - Bull/Bear Debate Coordinator

Orchestrates the research debate between bull and bear researchers,
then synthesizes final investment thesis.

🎯 OPIK INTEGRATION: Full debate flow traced for evaluation!
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

from event_horizon.data_pipeline.stage_3.models.schemas import Stage3Output
from event_horizon.analyzer_system.team_2_researchers.models.schemas import Team2Output
from event_horizon.analyzer_system.team_2_researchers.agents import (
    BullResearcher,
    BearResearcher,
    ResearchManager,
)


class Team2Orchestrator:
    """
    Team 2 Orchestrator - Bull/Bear Debate Coordination

    Debate Flow:
    1. Bull Researcher → Bullish argument
    2. Bear Researcher → Bearish counter-argument
    3. Research Manager → Synthesizes both into thesis

    🎯 OPIK VALUE:
    - Trace entire debate flow
    - Compare bull vs bear argument quality
    - Evaluate final thesis against outcomes
    - Optimize debate prompts
    - Monitor multi-agent token usage
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Team 2 Orchestrator

        Args:
            config: Configuration for agents
        """
        self.config = config or {}
        self.logger = logging.getLogger("analyzer.team2.orchestrator")

        # Initialize agents
        self.bull_researcher = BullResearcher(config=self.config)
        self.bear_researcher = BearResearcher(config=self.config)
        self.research_manager = ResearchManager(config=self.config)

        self.enable_opik = self.config.get("enable_opik", True) and OPIK_AVAILABLE

        if self.enable_opik:
            opik_project = self.config.get("opik_project", "event-horizon")
            try:
                opik.configure(project_name=opik_project)
                self.logger.info(f"✓ Team 2 Opik tracking enabled: {opik_project}")
            except Exception as e:
                self.logger.warning(f"Opik init failed: {e}")
                self.enable_opik = False

        self.logger.info("Team 2 Orchestrator initialized (Bull/Bear Debate)")

    @track(name="team2_debate_pipeline", project_name="event-horizon")
    def execute(self, stage3_output: Stage3Output) -> Dict[str, Any]:
        """
        Execute Team 2 bull/bear debate for portfolio

        This creates a hierarchical Opik trace:
        - Top level: Complete debate pipeline
          - Symbol 1: Bull → Bear → Manager
          - Symbol 2: Bull → Bear → Manager
          - Symbol 3: Bull → Bear → Manager

        Perfect for seeing:
        - How each debate unfolds
        - Token usage per symbol
        - Which arguments are stronger
        - Manager's decision reasoning

        Args:
            stage3_output: Stage 3 output with features

        Returns:
            Dict with Team2Output containing all debates
        """
        start_time = time.time()

        self.logger.info(
            f"Starting Team 2 debate for portfolio {stage3_output.portfolio_id}"
        )
        self.logger.info(f"Symbols: {stage3_output.symbols}")

        # Initialize output
        team2_output = Team2Output(
            portfolio_id=stage3_output.portfolio_id,
            symbols=stage3_output.symbols,
            opik_project_name=self.config.get("opik_project", "event-horizon"),
        )

        all_errors = []
        total_tokens = 0
        debate_count = 0

        # Run debate for each symbol
        for symbol in stage3_output.symbols:
            if symbol not in stage3_output.symbol_features:
                self.logger.warning(f"{symbol}: No features available, skipping")
                all_errors.append({"symbol": symbol, "error": "No features"})
                continue

            features = stage3_output.symbol_features[symbol]

            try:
                # Conduct debate (Opik traces each step)
                bull_arg, bear_arg, thesis = self._conduct_debate(symbol, features)

                # Store results
                team2_output.bull_arguments[symbol] = bull_arg
                team2_output.bear_arguments[symbol] = bear_arg
                team2_output.investment_theses[symbol] = thesis

                # Track metrics
                debate_count += 1
                total_tokens += (
                    bull_arg.tokens_used + bear_arg.tokens_used + thesis.tokens_used
                )

            except Exception as e:
                self.logger.error(f"{symbol}: Debate failed - {e}")
                all_errors.append({"symbol": symbol, "error": str(e)})

        # Update metadata
        team2_output.total_debates = debate_count
        team2_output.total_tokens_used = total_tokens
        team2_output.execution_time_seconds = time.time() - start_time
        team2_output.errors = all_errors

        # Determine status
        if debate_count == 0:
            team2_output.status = "failed"
        elif all_errors:
            team2_output.status = "partial_success"
        else:
            team2_output.status = "success"

        self.logger.info(
            f"Team 2 debates completed in {team2_output.execution_time_seconds:.2f}s"
        )
        self.logger.info(f"Status: {team2_output.status}")
        self.logger.info(
            f"Debates: {debate_count}, Tokens: {total_tokens}"
        )

        return {
            "status": team2_output.status,
            "team2_output": team2_output,
            "execution_time_seconds": team2_output.execution_time_seconds,
            "total_debates": debate_count,
            "total_tokens_used": total_tokens,
            "errors": all_errors,
        }

    @track(name="symbol_debate", project_name="event-horizon")
    def _conduct_debate(self, symbol: str, features):
        """
        Conduct bull/bear debate for a single symbol

        This creates a sub-trace showing:
        1. Bull argument generation
        2. Bear argument generation (with rebuttal)
        3. Manager synthesis

        Args:
            symbol: Stock symbol
            features: SymbolFeatures from Stage 3

        Returns:
            Tuple of (BullArgument, BearArgument, InvestmentThesis)
        """
        self.logger.info(f"🎭 Starting debate for {symbol}")

        # Step 1: Bull makes the case
        bull_argument = self.bull_researcher.generate_argument(symbol, features)

        # Step 2: Bear counters (with rebuttal to bull)
        bear_argument = self.bear_researcher.generate_argument(
            symbol, features, bull_argument
        )

        # Step 3: Manager synthesizes
        thesis = self.research_manager.synthesize_thesis(
            symbol, bull_argument, bear_argument
        )

        self.logger.info(
            f"🎭 {symbol} debate complete: "
            f"Bull={bull_argument.recommendation} ({bull_argument.confidence:.2f}), "
            f"Bear={bear_argument.recommendation} ({bear_argument.confidence:.2f}), "
            f"Final={thesis.recommendation} ({thesis.confidence:.2f})"
        )

        return bull_argument, bear_argument, thesis
