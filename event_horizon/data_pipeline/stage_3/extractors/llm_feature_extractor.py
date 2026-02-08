"""
LLM Feature Extractor with Opik Integration

Uses LLM to extract patterns, insights, and features from normalized data.
Full Opik tracing for observability and optimization.
"""

import logging
import time
import json
import os
from typing import Any, Dict, Optional

try:
    import opik
    from opik import track
    from opik.integrations.openai import track_openai
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    track = lambda **kw: lambda fn: fn  # no-op decorator
    logging.warning("Opik not available. Install with: pip install opik")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available. Install with: pip install openai")

from event_horizon.data_pipeline.stage_2.models.schemas import NormalizedSymbolData
from event_horizon.data_pipeline.stage_3.models.schemas import SymbolFeatures


class LLMFeatureExtractor:
    """
    LLM Feature Extractor - Intelligent Pattern Recognition

    Uses LLM to analyze normalized market data and extract:
    - Market sentiment and confidence
    - Technical signals
    - Fundamental health assessment
    - Key patterns and risks
    - News sentiment

    🎯 OPIK INTEGRATION:
    - Every LLM call is traced
    - Prompts and responses logged
    - Token usage tracked
    - Latency monitored
    - Evaluation ready
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize LLM Feature Extractor

        Args:
            config: Configuration with:
                - llm_model: Model to use (default: from LLM_MODEL env)
                - temperature: LLM temperature (default: 0.3)
                - opik_project: Opik project name (default: event-horizon)
                - enable_opik: Enable Opik tracking (default: True)
        """
        self.config = config or {}
        self.logger = logging.getLogger("data_pipeline.stage_3.extractor")

        self.llm_model = self.config.get("llm_model", os.getenv("LLM_MODEL", "mistralai/Ministral-3-14B-Reasoning-2512"))
        self.temperature = self.config.get("temperature", 0.3)
        self.opik_project = self.config.get("opik_project", "event-horizon")
        self.enable_opik = self.config.get("enable_opik", True) and OPIK_AVAILABLE

        # Initialize LLM client (OpenAI-compatible, pointed at local vLLM)
        if OPENAI_AVAILABLE:
            self.llm_client = OpenAI(
                base_url=os.getenv("LLM_BASE_URL", "http://localhost:8000") + "/v1",
                api_key=os.getenv("LLM_API_KEY") or "not-needed",
            )

            # Track with Opik
            if self.enable_opik:
                self.llm_client = track_openai(self.llm_client)
                self.logger.info("✓ Opik tracking enabled for LLM client")
        else:
            self.llm_client = None
            self.logger.warning("LLM client not available")

        # Initialize Opik
        if self.enable_opik:
            try:
                opik.configure(project_name=self.opik_project)
                self.logger.info(f"✓ Opik initialized: project={self.opik_project}")
            except Exception as e:
                self.logger.warning(f"Opik initialization failed: {e}")
                self.enable_opik = False

        self.logger.info(
            f"LLM Feature Extractor initialized: "
            f"model={self.llm_model}, opik={self.enable_opik}"
        )

    @track(name="extract_features", project_name="event-horizon")
    def extract_features(
        self,
        symbol: str,
        normalized_data: NormalizedSymbolData,
    ) -> SymbolFeatures:
        """
        Extract features from normalized symbol data using LLM

        This function is tracked by Opik:
        - Full trace of inputs/outputs
        - Token counting
        - Latency measurement

        Args:
            symbol: Stock symbol
            normalized_data: Normalized data for the symbol

        Returns:
            SymbolFeatures with LLM-extracted insights
        """
        start_time = time.time()
        self.logger.info(f"Extracting features for {symbol} using {self.llm_model}")

        features = SymbolFeatures(
            symbol=symbol,
            llm_model_used=self.llm_model,
        )

        if not self.llm_client:
            features.has_errors = True
            features.errors.append("LLM client not available")
            return features

        try:
            # Prepare context from normalized data
            context = self._prepare_context(normalized_data)

            # Call LLM for feature extraction
            extraction_result = self._call_llm_for_extraction(symbol, context)

            # Parse LLM response
            features = self._parse_llm_response(features, extraction_result)

            # Track metrics
            features.extraction_time_seconds = time.time() - start_time
            features.total_tokens = extraction_result.get("total_tokens", 0)

            # Get Opik trace ID if available
            if self.enable_opik:
                # Opik automatically tracks the trace
                features.opik_trace_id = "auto-tracked"

            self.logger.info(
                f"{symbol}: Features extracted "
                f"(sentiment={features.market_sentiment}, "
                f"technical={features.technical_signal}, "
                f"tokens={features.total_tokens})"
            )

        except Exception as e:
            self.logger.error(f"{symbol}: Feature extraction failed - {e}")
            features.has_errors = True
            features.errors.append(str(e))
            features.extraction_time_seconds = time.time() - start_time

        return features

    def _prepare_context(self, normalized_data: NormalizedSymbolData) -> str:
        """Prepare context string for LLM from normalized data"""
        context_parts = []

        # Price data
        if normalized_data.price_data:
            price_info = normalized_data.price_data
            if not price_info.get("error"):
                latest_price = price_info.get("latest_price")
                price_change = price_info.get("price_change_pct")
                if latest_price:
                    context_parts.append(f"**Price**: ${latest_price:.2f}")
                if price_change is not None:
                    context_parts.append(f"**Change**: {price_change:+.2f}%")

        # Technical indicators
        if normalized_data.technical_indicators:
            tech_info = normalized_data.technical_indicators
            if not tech_info.get("error"):
                indicators = tech_info.get("indicators", {})
                if indicators:
                    tech_text = []
                    for ind_name, ind_data in indicators.items():
                        tech_text.append(f"- {ind_name}: {ind_data.get('text', '')}")
                    context_parts.append(f"**Technical Indicators**:\n" + "\n".join(tech_text))

        # Fundamentals
        if normalized_data.fundamentals:
            fund_info = normalized_data.fundamentals
            if not fund_info.get("error"):
                text_summary = fund_info.get("text_summary", "")
                if text_summary:
                    context_parts.append(f"**Fundamentals**: {text_summary}")

        # News
        if normalized_data.news:
            news_info = normalized_data.news
            if not news_info.get("error"):
                articles = news_info.get("articles", [])
                if articles:
                    news_summaries = []
                    for article in articles[:5]:  # Top 5 articles
                        title = article.get("title", "")
                        if title:
                            news_summaries.append(f"- {title}")
                    if news_summaries:
                        context_parts.append(
                            f"**Recent News ({len(articles)} articles)**:\n" + "\n".join(news_summaries)
                        )

        # Web search
        if normalized_data.web_search:
            ws_info = normalized_data.web_search
            if not ws_info.get("error"):
                parts = []
                if ws_info.get("answer"):
                    parts.append(f"Summary: {ws_info['answer']}")
                articles = ws_info.get("articles", [])
                for article in articles[:5]:
                    title = article.get("title", "")
                    content = article.get("content", "")[:200]
                    if title or content:
                        parts.append(f"- {title}: {content}")
                if parts:
                    query = ws_info.get("query", "")
                    context_parts.append(
                        f"**Web Research ({query})**:\n" + "\n".join(parts)
                    )

        return "\n\n".join(context_parts) if context_parts else "No data available"

    @track(name="llm_extraction_call")
    def _call_llm_for_extraction(self, symbol: str, context: str) -> Dict[str, Any]:
        """
        Call LLM to extract features

        This function is also tracked by Opik as a sub-span
        """
        prompt = f"""You are a financial analyst AI. Analyze the following market data for {symbol} and extract key insights.

DATA:
{context}

Please provide your analysis in the following JSON format:
{{
    "market_sentiment": "bullish|bearish|neutral",
    "sentiment_confidence": 0.0-1.0,
    "sentiment_reasoning": "brief explanation",
    "technical_signal": "buy|sell|hold",
    "technical_confidence": 0.0-1.0,
    "technical_reasoning": "brief explanation",
    "fundamental_health": "strong|moderate|weak",
    "fundamental_confidence": 0.0-1.0,
    "fundamental_reasoning": "brief explanation",
    "key_patterns": ["pattern1", "pattern2"],
    "risk_factors": ["risk1", "risk2"],
    "opportunities": ["opp1", "opp2"],
    "news_sentiment": "positive|negative|neutral",
    "news_summary": "brief summary of news"
}}

Return ONLY the JSON, no additional text."""

        response = self.llm_client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": "You are a financial analysis expert."},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
        )

        # Extract response
        content = response.choices[0].message.content
        total_tokens = response.usage.total_tokens

        return {
            "content": content,
            "total_tokens": total_tokens,
        }

    def _parse_llm_response(
        self, features: SymbolFeatures, extraction_result: Dict[str, Any]
    ) -> SymbolFeatures:
        """Parse LLM JSON response into SymbolFeatures"""
        try:
            response_data = json.loads(extraction_result["content"])

            features.market_sentiment = response_data.get("market_sentiment", "")
            features.sentiment_confidence = response_data.get("sentiment_confidence", 0.0)
            features.sentiment_reasoning = response_data.get("sentiment_reasoning", "")

            features.technical_signal = response_data.get("technical_signal", "")
            features.technical_confidence = response_data.get("technical_confidence", 0.0)
            features.technical_reasoning = response_data.get("technical_reasoning", "")

            features.fundamental_health = response_data.get("fundamental_health", "")
            features.fundamental_confidence = response_data.get("fundamental_confidence", 0.0)
            features.fundamental_reasoning = response_data.get("fundamental_reasoning", "")

            features.key_patterns = response_data.get("key_patterns", [])
            features.risk_factors = response_data.get("risk_factors", [])
            features.opportunities = response_data.get("opportunities", [])

            features.news_sentiment = response_data.get("news_sentiment", "")
            features.news_summary = response_data.get("news_summary", "")

        except json.JSONDecodeError as e:
            features.has_errors = True
            features.errors.append(f"Failed to parse LLM response: {e}")

        return features
