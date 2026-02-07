"""
Bull Researcher Agent

Argues for buying/long positions. Focuses on growth opportunities,
positive catalysts, and upside potential.

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

from event_horizon.analyzer_system.bull_bear_analyzer.models.schemas import BullArgument
from event_horizon.data_pipeline.stage_3.models.schemas import SymbolFeatures


class BullResearcher:
    """
    Bull Researcher - Bullish Investment Arguments

    Role: Advocate for long positions
    Focus: Growth opportunities, positive catalysts, upside scenarios

    🎯 OPIK: All arguments traced for quality evaluation
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Bull Researcher

        Args:
            config: Configuration with:
                - llm_model: Model to use
                - temperature: LLM temperature (higher = more creative)
                - enable_opik: Enable Opik tracking
        """
        self.config = config or {}
        self.logger = logging.getLogger("analyzer.bull_bear.bull")

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

        self.logger.info(f"Bull Researcher initialized: model={self.llm_model}, opik={self.enable_opik}")

    @track(name="bull_research_argument", project_name="event-horizon")
    def generate_argument(
        self,
        symbol: str,
        features: SymbolFeatures,
    ) -> BullArgument:
        """
        Generate bullish argument for a symbol

        This is traced by Opik to see:
        - Input features used
        - Generated bull argument
        - Token usage
        - Latency

        Args:
            symbol: Stock symbol
            features: LLM-extracted features from Stage 3

        Returns:
            BullArgument with bullish thesis
        """
        self.logger.info(f"🐂 Bull researcher analyzing {symbol}")

        argument = BullArgument(symbol=symbol)

        if not self.openai_client:
            argument.thesis = "OpenAI client not available"
            return argument

        try:
            # Prepare context from features
            context = self._prepare_context(features)

            # Generate bull argument
            result = self._call_llm_for_argument(symbol, context)

            # Parse response
            argument = self._parse_response(argument, result)
            argument.tokens_used = result.get("total_tokens", 0)

            if self.enable_opik:
                argument.opik_trace_id = "auto-tracked"

            self.logger.info(
                f"🐂 {symbol}: {argument.recommendation} "
                f"(confidence: {argument.confidence:.2f}, "
                f"tokens: {argument.tokens_used})"
            )

        except Exception as e:
            self.logger.error(f"🐂 {symbol}: Bull research failed - {e}")
            argument.thesis = f"Error: {str(e)}"

        return argument

    def _prepare_context(self, features: SymbolFeatures) -> str:
        """Prepare feature context for bull researcher"""
        parts = []

        parts.append(f"**Market Sentiment**: {features.market_sentiment} ({features.sentiment_confidence:.2f})")
        parts.append(f"**Technical Signal**: {features.technical_signal} ({features.technical_confidence:.2f})")
        parts.append(f"**Fundamental Health**: {features.fundamental_health} ({features.fundamental_confidence:.2f})")

        if features.sentiment_reasoning:
            parts.append(f"**Sentiment Reasoning**: {features.sentiment_reasoning}")

        if features.technical_reasoning:
            parts.append(f"**Technical Reasoning**: {features.technical_reasoning}")

        if features.opportunities:
            parts.append(f"**Opportunities**: {', '.join(features.opportunities)}")

        if features.key_patterns:
            parts.append(f"**Key Patterns**: {', '.join(features.key_patterns)}")

        if features.news_summary:
            parts.append(f"**News**: {features.news_summary}")

        return "\n".join(parts)

    @track(name="bull_llm_call")
    def _call_llm_for_argument(self, symbol: str, context: str) -> Dict[str, Any]:
        """Call LLM to generate bull argument"""
        prompt = f"""You are a BULLISH investment researcher. Your job is to argue WHY {symbol} will GO UP.

MARKET DATA:
{context}

Generate a STRONG BULLISH argument for buying {symbol}. Be optimistic and focus on:
- Growth opportunities and catalysts
- Positive trends and momentum
- Undervalued potential
- Competitive advantages
- Favorable market conditions

Return JSON:
{{
    "recommendation": "BUY|STRONG_BUY",
    "confidence": 0.0-1.0,
    "target_price": optional_number,
    "time_horizon": "1 week|1 month|3 months",
    "thesis": "Main bullish thesis (2-3 sentences)",
    "key_catalysts": ["catalyst1", "catalyst2", "catalyst3"],
    "supporting_evidence": ["evidence1", "evidence2"],
    "risk_acknowledgment": ["risk1", "risk2"]
}}

Be BULLISH! This is your role in the debate."""

        response = self.openai_client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": "You are an optimistic bull researcher who argues for buying stocks."},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )

        return {
            "content": response.choices[0].message.content,
            "total_tokens": response.usage.total_tokens,
        }

    def _parse_response(self, argument: BullArgument, result: Dict[str, Any]) -> BullArgument:
        """Parse LLM response into BullArgument"""
        try:
            data = json.loads(result["content"])

            argument.recommendation = data.get("recommendation", "BUY")
            argument.confidence = data.get("confidence", 0.0)
            argument.target_price = data.get("target_price")
            argument.time_horizon = data.get("time_horizon", "")
            argument.thesis = data.get("thesis", "")
            argument.key_catalysts = data.get("key_catalysts", [])
            argument.supporting_evidence = data.get("supporting_evidence", [])
            argument.risk_acknowledgment = data.get("risk_acknowledgment", [])

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse bull response: {e}")
            argument.thesis = "Error parsing response"

        return argument
