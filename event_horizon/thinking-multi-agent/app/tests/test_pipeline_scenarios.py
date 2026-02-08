"""Integration tests for EH pipeline scenarios.

Four scenarios:
1. Create data agent -> run it -> get SymbolFeatures (web_search + built-in)
2. Create custom analysis agent -> run LLM analysis
3. Portfolio flow: data agent -> analyzer agent -> end-to-end
4. Thinking agent discovers data needs -> creates data agent -> full pipeline
"""

import json

import pytest

from tests.conftest import (
    make_earnings_result,
    make_llm_full_response,
    make_stage2_result,
    make_stage3_result,
    make_web_search_result,
)

# ──────────────────────────────────────────────────────────────────────
# Scenario 1: Data agent -> pipeline -> SymbolFeatures
# ──────────────────────────────────────────────────────────────────────


class TestDataAgentPipeline:
    """Create a data agent, run /analyze, assert SymbolFeatures output."""

    def test_web_search_data_agent(
        self, client, mock_search_for_stocks, mock_stage2, mock_stage3
    ):
        """POST /agents (web_search) -> POST /agents/{id}/analyze -> SymbolFeatures."""
        # Arrange: create a web_search data agent
        create_resp = client.post(
            "/agents",
            json={
                "name": "earnings-web-search",
                "description": "Search web for AAPL earnings",
                "type": "data",
                "source": "web_search",
                "system_prompt": "Search for earnings data on the web.",
            },
        )
        assert create_resp.status_code == 201
        agent = create_resp.json()
        assert agent["type"] == "data"
        assert agent["source"] == "web_search"
        agent_id = agent["agent_id"]

        # Mock web search
        mock_search_for_stocks.return_value = make_web_search_result(["AAPL"])

        # Act: run the agent
        analyze_resp = client.post(
            f"/agents/{agent_id}/analyze",
            json={"task": "analyze earnings", "stocks": ["AAPL"]},
        )

        # Assert
        assert analyze_resp.status_code == 200
        body = analyze_resp.json()
        assert body["status"] == "success"
        assert body["agent_id"] == agent_id

        # Parse the SymbolFeatures JSON
        features = json.loads(body["analysis"])
        assert "AAPL" in features
        aapl = features["AAPL"]
        assert "market_sentiment" in aapl
        assert "technical_signal" in aapl
        assert "fundamental_health" in aapl

    def test_builtin_earnings_agent(
        self, client, mock_execute_tool, mock_stage2, mock_stage3
    ):
        """Built-in 'earnings' agent -> pipeline -> SymbolFeatures."""
        # The "earnings" agent is pre-seeded by conftest
        mock_execute_tool.return_value = make_earnings_result(["AAPL"])

        analyze_resp = client.post(
            "/agents/earnings/analyze",
            json={"task": "analyze earnings", "stocks": ["AAPL"]},
        )

        assert analyze_resp.status_code == 200
        body = analyze_resp.json()
        assert body["status"] == "success"

        features = json.loads(body["analysis"])
        assert "AAPL" in features
        assert "market_sentiment" in features["AAPL"]
        assert "technical_signal" in features["AAPL"]


# ──────────────────────────────────────────────────────────────────────
# Scenario 2: Custom analysis agent -> LLM analysis
# ──────────────────────────────────────────────────────────────────────


class TestCustomAnalysisAgent:
    """Create an analysis agent with a custom prompt, run LLM analysis."""

    def test_create_and_run_analysis_agent(self, client, mock_call_llm_full):
        """POST /agents (analysis) -> POST /agents/{id}/analyze -> LLM output."""
        # Arrange: create analysis agent
        create_resp = client.post(
            "/agents",
            json={
                "name": "my-bull-analyst",
                "description": "Bullish perspective analyst",
                "type": "analysis",
                "system_prompt": "You are a bullish stock analyst. Always look for upside.",
            },
        )
        assert create_resp.status_code == 201
        agent = create_resp.json()
        assert agent["type"] == "analysis"
        agent_id = agent["agent_id"]

        # Mock LLM
        mock_call_llm_full.return_value = make_llm_full_response(
            content="AAPL shows strong upside potential with 15% growth expected.",
            reasoning="Revenue beat estimates by 8%, services segment accelerating.",
        )

        # Act
        analyze_resp = client.post(
            f"/agents/{agent_id}/analyze",
            json={
                "task": "Provide bullish analysis",
                "stocks": ["AAPL"],
                "financial_data": [{"metric": "EPS", "value": 6.42}],
            },
        )

        # Assert
        assert analyze_resp.status_code == 200
        body = analyze_resp.json()
        assert body["status"] == "success"
        assert "upside" in body["analysis"].lower()
        assert body["reasoning"] is not None
        assert body["usage"]["total_tokens"] == 100


# ──────────────────────────────────────────────────────────────────────
# Scenario 3: Portfolio flow — data agent then analyzer
# ──────────────────────────────────────────────────────────────────────


class TestPortfolioDataThenAnalyzer:
    """Data agent collects SymbolFeatures, then analysis agent consumes them."""

    def test_data_then_analyzer_pipeline(
        self,
        client,
        mock_search_for_stocks,
        mock_stage2,
        mock_stage3,
        mock_call_llm_full,
    ):
        """Full flow: data agent -> parse features -> analysis agent -> final."""
        # Step 1: Create web_search data agent
        data_agent_resp = client.post(
            "/agents",
            json={
                "name": "portfolio-data",
                "description": "Fetch data for portfolio analysis",
                "type": "data",
                "source": "web_search",
                "system_prompt": "Collect web data for the portfolio.",
            },
        )
        assert data_agent_resp.status_code == 201
        data_agent_id = data_agent_resp.json()["agent_id"]

        # Step 2: Run data agent -> get SymbolFeatures
        mock_search_for_stocks.return_value = make_web_search_result(["AAPL"])

        data_resp = client.post(
            f"/agents/{data_agent_id}/analyze",
            json={"task": "collect data", "stocks": ["AAPL"]},
        )
        assert data_resp.status_code == 200
        assert data_resp.json()["status"] == "success"

        # Step 3: Parse SymbolFeatures from the analysis JSON
        symbol_features = json.loads(data_resp.json()["analysis"])
        assert "AAPL" in symbol_features

        # Step 4: Create analysis agent
        analysis_agent_resp = client.post(
            "/agents",
            json={
                "name": "portfolio-advisor",
                "description": "Investment advisor using EH data",
                "type": "analysis",
                "system_prompt": "You are an investment advisor. Analyze EH-processed features.",
            },
        )
        assert analysis_agent_resp.status_code == 201
        analysis_agent_id = analysis_agent_resp.json()["agent_id"]

        # Step 5: Run analysis agent with SymbolFeatures as metadata
        mock_call_llm_full.return_value = make_llm_full_response(
            content="Based on EH data: AAPL is a strong buy. Sentiment bullish, technicals positive.",
            reasoning="SymbolFeatures show bullish sentiment with high confidence.",
        )

        final_resp = client.post(
            f"/agents/{analysis_agent_id}/analyze",
            json={
                "task": "Provide investment recommendation",
                "stocks": ["AAPL"],
                "metadata": symbol_features,
            },
        )

        # Assert
        assert final_resp.status_code == 200
        body = final_resp.json()
        assert body["status"] == "success"
        assert "AAPL" in body["analysis"]
        assert body["reasoning"] is not None


# ──────────────────────────────────────────────────────────────────────
# Scenario 4: Thinking agent — iterative tool use & data agent discovery
# ──────────────────────────────────────────────────────────────────────


class TestThinkingAgent:
    """Thinking agent uses ReAct loop: call_tool -> generate_response."""

    def test_thinking_loop_call_tool_then_respond(
        self, client, mock_call_llm, mock_execute_tool
    ):
        """POST /agents/think: LLM calls a tool, then generates response."""
        # Side effects: first call returns call_tool, second returns generate_response,
        # third is the final generation call
        mock_call_llm.side_effect = [
            # think_step iteration 1: call candlestick
            json.dumps({
                "action": "call_tool",
                "tool": "candlestick",
                "reasoning": "Need price data to analyze trend",
            }),
            # think_step iteration 2: ready to answer
            json.dumps({
                "action": "generate_response",
                "reasoning": "Have sufficient price data for analysis",
            }),
            # generate_final_response
            json.dumps({
                "summary": "AAPL shows bullish trend",
                "recommendations": ["Buy AAPL"],
                "confidence": 0.8,
                "key_insights": ["Price above SMA200"],
                "risks": ["High valuation"],
            }),
        ]

        mock_execute_tool.return_value = {
            "chart_data_by_symbol": {
                "AAPL": {"symbol": "AAPL", "candles": [{"close": 195.0}]}
            }
        }

        resp = client.post(
            "/agents/think",
            json={
                "stocks": ["AAPL"],
                "system_prompt": "Analyze the stock trend for AAPL",
                "max_iterations": 5,
                "available_tools": ["candlestick", "earnings"],
            },
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert "candlestick" in body["tools_used"]
        assert body["final_result"] is not None
        assert len(body["thinking_steps"]) >= 2

    def test_thinking_loop_create_data_agent_pauses(
        self, client, mock_call_llm, mock_execute_tool
    ):
        """POST /agents/think: LLM requests a custom data agent -> status=paused."""
        mock_call_llm.return_value = json.dumps({
            "action": "create_data_agent",
            "agent_name": "insider-trading",
            "agent_description": "Fetch insider trading data from SEC filings",
            "data_type": "insider trading",
            "reasoning": "Need insider trading data not available in existing tools",
        })

        resp = client.post(
            "/agents/think",
            json={
                "stocks": ["AAPL"],
                "system_prompt": "Check for insider trading activity",
                "max_iterations": 5,
                "available_tools": ["candlestick", "earnings"],
            },
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "paused"
        assert body["reason"] == "need_data_agent"
        assert body["suggested_data_agent"]["name"] == "insider-trading"
        assert "resume_context" in body


class TestCustomAgentDiscovery:
    """POST /agents/custom (no input_data) discovers needed tools."""

    def test_custom_agent_needs_data(self, client, mock_call_llm):
        """Custom agent without input_data -> think_step -> needs_data."""
        # think_step returns call_tool
        mock_call_llm.return_value = json.dumps({
            "action": "call_tool",
            "tool": "earnings",
            "reasoning": "Need earnings data to analyze",
        })

        resp = client.post(
            "/agents/custom",
            json={
                "stocks": ["AAPL"],
                "system_prompt": "Analyze AAPL financials in depth",
            },
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "needs_data"
        assert body["required_agents"] is not None
        assert len(body["required_agents"]) == 1
        assert body["required_agents"][0]["name"] == "earnings"
        assert body["required_agents"][0]["type"] == "data"
