"""
Research Manager Agent

Synthesizes bull and bear arguments into a balanced investment thesis.
Acts as the moderator and decision-maker in the debate.

🎯 OPIK INTEGRATION: Synthesis process is fully traced.
"""

import json
import logging
import os
from typing import Any, Dict

try:
    from opik import track
    from opik.integrations.openai import track_openai

    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from event_horizon.analyzer_system.bull_bear_analyzer.models.schemas import (
    BearArgument,
    BullArgument,
    InvestmentThesis,
)


class ResearchManager:
    """
    Research Manager - Investment Thesis Synthesis

    Role: Moderate the bull/bear debate and create balanced thesis
    Focus: Probability-weighted scenarios, risk/reward analysis

    🎯 OPIK: Synthesis process traced to evaluate decision quality
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Research Manager

        Args:
            config: Configuration with:
                - llm_model: Model to use
                - temperature: LLM temperature (lower = more analytical)
                - enable_opik: Enable Opik tracking
        """
        self.config = config or {}
        self.logger = logging.getLogger("analyzer.bull_bear.manager")

        self.llm_model = self.config.get("llm_model", "gpt-4o-mini")
        self.temperature = self.config.get("temperature", 0.4)  # Lower for balanced analysis
        self.enable_opik = self.config.get("enable_opik", True) and OPIK_AVAILABLE

        # Initialize OpenAI
        if OPENAI_AVAILABLE:
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            if self.enable_opik:
                self.openai_client = track_openai(self.openai_client)
        else:
            self.openai_client = None

        self.logger.info(f"Research Manager initialized: model={self.llm_model}, opik={self.enable_opik}")

    @track(name="synthesize_thesis", project_name="event-horizon")
    def synthesize_thesis(
        self,
        symbol: str,
        bull_argument: BullArgument,
        bear_argument: BearArgument,
    ) -> InvestmentThesis:
        """
        Synthesize bull and bear arguments into investment thesis

        This is the KEY DECISION POINT in the debate!

        Opik traces:
        - Both input arguments (bull + bear)
        - Synthesis reasoning
        - Final recommendation
        - Token usage
        - Decision quality metrics

        Args:
            symbol: Stock symbol
            bull_argument: Bull researcher's argument
            bear_argument: Bear researcher's argument

        Returns:
            InvestmentThesis with balanced recommendation
        """
        self.logger.info(f"⚖️  Research Manager synthesizing {symbol}")

        thesis = InvestmentThesis(symbol=symbol)

        if not self.openai_client:
            thesis.thesis_summary = "OpenAI client not available"
            return thesis

        try:
            # Prepare debate context
            debate_context = self._prepare_debate_context(bull_argument, bear_argument)

            # Synthesize thesis
            result = self._call_llm_for_synthesis(symbol, debate_context)

            # Parse response
            thesis = self._parse_response(thesis, result)
            thesis.tokens_used = result.get("total_tokens", 0)

            if self.enable_opik:
                thesis.opik_trace_id = "auto-tracked"

            self.logger.info(
                f"⚖️  {symbol}: {thesis.recommendation} "
                f"(confidence: {thesis.confidence:.2f}, "
                f"bull prob: {thesis.bull_probability:.2f}, "
                f"tokens: {thesis.tokens_used})"
            )

        except Exception as e:
            self.logger.error(f"⚖️  {symbol}: Thesis synthesis failed - {e}")
            thesis.thesis_summary = f"Error: {str(e)}"

        return thesis

    def _prepare_debate_context(self, bull_argument: BullArgument, bear_argument: BearArgument) -> str:
        """Prepare debate context for synthesis"""
        context = f"""BULL CASE:
Recommendation: {bull_argument.recommendation} (confidence: {bull_argument.confidence:.2f})
Thesis: {bull_argument.thesis}
Catalysts: {', '.join(bull_argument.key_catalysts)}
Evidence: {', '.join(bull_argument.supporting_evidence)}

BEAR CASE:
Recommendation: {bear_argument.recommendation} (confidence: {bear_argument.confidence:.2f})
Thesis: {bear_argument.thesis}
Risks: {', '.join(bear_argument.key_risks)}
Evidence: {', '.join(bear_argument.supporting_evidence)}
Rebuttals: {', '.join(bear_argument.bull_case_rebuttal)}
"""
        return context

    @track(name="manager_llm_call")
    def _call_llm_for_synthesis(self, symbol: str, debate_context: str) -> Dict[str, Any]:
        """Call LLM to synthesize investment thesis"""
        prompt = f"""You are a RESEARCH MANAGER. You've heard arguments from both bull and bear researchers about {symbol}.

DEBATE:
{debate_context}

Your job is to:
1. Evaluate BOTH arguments objectively
2. Assign probabilities to bull vs bear scenarios
3. Make a BALANCED final recommendation (BUY, HOLD, or SELL)
4. Consider risk/reward and position sizing

Return JSON:
{{
    "recommendation": "BUY|HOLD|SELL",
    "confidence": 0.0-1.0,
    "position_size": "small|medium|large",
    "thesis_summary": "Balanced 2-3 sentence summary",
    "bull_case_summary": "Key bull points",
    "bear_case_summary": "Key bear points",
    "bull_probability": 0.0-1.0,
    "bear_probability": 0.0-1.0,
    "base_case": "Most likely outcome",
    "bull_case": "Best case scenario",
    "bear_case": "Worst case scenario"
}}

Be OBJECTIVE and BALANCED. Consider both sides fairly."""

        response = self.openai_client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an objective research manager who synthesizes bull and bear arguments into balanced investment theses.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )

        return {
            "content": response.choices[0].message.content,
            "total_tokens": response.usage.total_tokens,
        }

    def _parse_response(self, thesis: InvestmentThesis, result: Dict[str, Any]) -> InvestmentThesis:
        """Parse LLM response into InvestmentThesis"""
        try:
            data = json.loads(result["content"])

            thesis.recommendation = data.get("recommendation", "HOLD")
            thesis.confidence = data.get("confidence", 0.0)
            thesis.position_size = data.get("position_size", "small")
            thesis.thesis_summary = data.get("thesis_summary", "")
            thesis.bull_case_summary = data.get("bull_case_summary", "")
            thesis.bear_case_summary = data.get("bear_case_summary", "")
            thesis.bull_probability = data.get("bull_probability", 0.5)
            thesis.bear_probability = data.get("bear_probability", 0.5)
            thesis.base_case = data.get("base_case", "")
            thesis.bull_case = data.get("bull_case", "")
            thesis.bear_case = data.get("bear_case", "")

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse manager response: {e}")
            thesis.thesis_summary = "Error parsing response"

        return thesis
