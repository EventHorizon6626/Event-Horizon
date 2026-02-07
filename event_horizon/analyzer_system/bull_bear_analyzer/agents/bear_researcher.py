"""
Bear Researcher Agent

Argues for selling/short positions. Focuses on risks, overvaluation,
and downside potential.

🎯 OPIK INTEGRATION: Every argument is traced for evaluation.
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

from event_horizon.analyzer_system.bull_bear_analyzer.models.schemas import BearArgument, BullArgument
from event_horizon.data_pipeline.stage_3.models.schemas import SymbolFeatures


class BearResearcher:
    """
    Bear Researcher - Bearish Investment Arguments

    Role: Advocate for short positions / selling
    Focus: Risks, overvaluation, negative catalysts, downside scenarios

    🎯 OPIK: All arguments traced for quality evaluation
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Bear Researcher

        Args:
            config: Configuration with:
                - llm_model: Model to use
                - temperature: LLM temperature (higher = more creative)
                - enable_opik: Enable Opik tracking
        """
        self.config = config or {}
        self.logger = logging.getLogger("analyzer.bull_bear.bear")

        self.llm_model = self.config.get("llm_model", "gpt-4o-mini")
        self.temperature = self.config.get("temperature", 0.7)  # Higher for creative arguments
        self.enable_opik = self.config.get("enable_opik", True) and OPIK_AVAILABLE

        # Initialize OpenAI
        if OPENAI_AVAILABLE:
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            if self.enable_opik:
                self.openai_client = track_openai(self.openai_client)
        else:
            self.openai_client = None

        self.logger.info(f"Bear Researcher initialized: model={self.llm_model}, opik={self.enable_opik}")

    @track(name="bear_research_argument", project_name="event-horizon")
    def generate_argument(
        self,
        symbol: str,
        features: SymbolFeatures,
        bull_argument: BullArgument = None,
    ) -> BearArgument:
        """
        Generate bearish argument for a symbol

        Can optionally counter the bull argument for a true debate!

        This is traced by Opik to see:
        - Input features used
        - Bull argument (if provided)
        - Generated bear counter-argument
        - Token usage
        - Latency

        Args:
            symbol: Stock symbol
            features: LLM-extracted features from Stage 3
            bull_argument: Optional bull argument to counter

        Returns:
            BearArgument with bearish thesis
        """
        self.logger.info(f"🐻 Bear researcher analyzing {symbol}")

        argument = BearArgument(symbol=symbol)

        if not self.openai_client:
            argument.thesis = "OpenAI client not available"
            return argument

        try:
            # Prepare context from features
            context = self._prepare_context(features)

            # Add bull argument if provided (for rebuttal)
            bull_context = ""
            if bull_argument:
                bull_context = f"\n\nBULL ARGUMENT TO COUNTER:\n{bull_argument.thesis}\nCatalysts: {', '.join(bull_argument.key_catalysts)}"

            # Generate bear argument
            result = self._call_llm_for_argument(symbol, context, bull_context)

            # Parse response
            argument = self._parse_response(argument, result)
            argument.tokens_used = result.get("total_tokens", 0)

            if self.enable_opik:
                argument.opik_trace_id = "auto-tracked"

            self.logger.info(
                f"🐻 {symbol}: {argument.recommendation} "
                f"(confidence: {argument.confidence:.2f}, "
                f"tokens: {argument.tokens_used})"
            )

        except Exception as e:
            self.logger.error(f"🐻 {symbol}: Bear research failed - {e}")
            argument.thesis = f"Error: {str(e)}"

        return argument

    def _prepare_context(self, features: SymbolFeatures) -> str:
        """Prepare feature context for bear researcher"""
        parts = []

        parts.append(f"**Market Sentiment**: {features.market_sentiment} ({features.sentiment_confidence:.2f})")
        parts.append(f"**Technical Signal**: {features.technical_signal} ({features.technical_confidence:.2f})")
        parts.append(f"**Fundamental Health**: {features.fundamental_health} ({features.fundamental_confidence:.2f})")

        if features.sentiment_reasoning:
            parts.append(f"**Sentiment Reasoning**: {features.sentiment_reasoning}")

        if features.technical_reasoning:
            parts.append(f"**Technical Reasoning**: {features.technical_reasoning}")

        if features.risk_factors:
            parts.append(f"**Risk Factors**: {', '.join(features.risk_factors)}")

        if features.key_patterns:
            parts.append(f"**Key Patterns**: {', '.join(features.key_patterns)}")

        if features.news_summary:
            parts.append(f"**News**: {features.news_summary}")

        return "\n".join(parts)

    @track(name="bear_llm_call")
    def _call_llm_for_argument(self, symbol: str, context: str, bull_context: str = "") -> Dict[str, Any]:
        """Call LLM to generate bear argument"""
        prompt = f"""You are a BEARISH investment researcher. Your job is to argue WHY {symbol} will GO DOWN.

MARKET DATA:
{context}
{bull_context}

Generate a STRONG BEARISH argument for selling/shorting {symbol}. Be skeptical and focus on:
- Downside risks and threats
- Overvaluation concerns
- Negative trends or deterioration
- Competitive disadvantages
- Unfavorable market conditions

{"COUNTER the bull's argument. Show why their thesis is wrong!" if bull_context else ""}

Return JSON:
{{
    "recommendation": "SELL|STRONG_SELL|SHORT",
    "confidence": 0.0-1.0,
    "target_price": optional_number,
    "time_horizon": "1 week|1 month|3 months",
    "thesis": "Main bearish thesis (2-3 sentences)",
    "key_risks": ["risk1", "risk2", "risk3"],
    "supporting_evidence": ["evidence1", "evidence2"],
    "bull_case_rebuttal": ["rebuttal1", "rebuttal2"]
}}

Be BEARISH! This is your role in the debate."""

        response = self.openai_client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": "You are a skeptical bear researcher who argues for selling stocks."},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )

        return {
            "content": response.choices[0].message.content,
            "total_tokens": response.usage.total_tokens,
        }

    def _parse_response(self, argument: BearArgument, result: Dict[str, Any]) -> BearArgument:
        """Parse LLM response into BearArgument"""
        try:
            data = json.loads(result["content"])

            argument.recommendation = data.get("recommendation", "SELL")
            argument.confidence = data.get("confidence", 0.0)
            argument.target_price = data.get("target_price")
            argument.time_horizon = data.get("time_horizon", "")
            argument.thesis = data.get("thesis", "")
            argument.key_risks = data.get("key_risks", [])
            argument.supporting_evidence = data.get("supporting_evidence", [])
            argument.bull_case_rebuttal = data.get("bull_case_rebuttal", [])

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse bear response: {e}")
            argument.thesis = "Error parsing response"

        return argument
