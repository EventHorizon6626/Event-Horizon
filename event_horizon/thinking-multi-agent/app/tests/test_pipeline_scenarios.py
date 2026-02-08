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


# ──────────────────────────────────────────────────────────────────────
# Scenario 5: create_data_agent flow — thinking loop + BE→FE contract
# ──────────────────────────────────────────────────────────────────────


class TestCreateDataAgentFlow:
    """Verify the thinking loop correctly discovers standard tools, then
    creates an exotic data agent, and the /agents/custom endpoint returns
    the right needs_data response for the frontend.
    """

    def test_discover_multiple_tools_then_exotic_agent(self, client, mock_call_llm):
        """Discovery: LLM picks earnings, news, then create_data_agent for SEC filings.

        Expected: needs_data with 2 standard + 1 exotic required_agents.
        The FE uses required_agents to create canvas nodes + wire edges.
        """
        mock_call_llm.side_effect = [
            # Iter 1: discover earnings
            json.dumps({
                "action": "call_tool",
                "tool": "earnings",
                "reasoning": "Need quarterly earnings data",
            }),
            # Iter 2: discover news
            json.dumps({
                "action": "call_tool",
                "tool": "news",
                "reasoning": "Need recent news coverage",
            }),
            # Iter 3: create exotic agent (remaining standard tools empty or LLM wants specialized data)
            json.dumps({
                "action": "create_data_agent",
                "agent_name": "sec-filings",
                "agent_description": "Fetch SEC 10-K and 10-Q filings for AAPL",
                "data_type": "SEC filings",
                "reasoning": "Need SEC filing data not available in standard tools",
            }),
        ]

        resp = client.post(
            "/agents/custom",
            json={
                "stocks": ["AAPL"],
                "system_prompt": "Deep analysis of AAPL including SEC filings",
            },
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "needs_data"
        agents = body["required_agents"]
        assert len(agents) == 3  # 2 standard + 1 exotic

        # First two: standard EH pipeline agents
        standard = [a for a in agents if a["source"] == "eh_pipeline"]
        assert len(standard) == 2
        standard_names = {a["name"] for a in standard}
        assert standard_names == {"earnings", "news"}
        for a in standard:
            assert a["type"] == "data"
            assert "description" in a

        # Third: exotic agent
        exotic = [a for a in agents if a["source"] == "web_search"]
        assert len(exotic) == 1
        assert exotic[0]["name"] == "sec-filings"
        assert exotic[0]["type"] == "data"
        assert exotic[0]["system_prompt"]  # non-empty
        assert "SEC" in exotic[0]["system_prompt"] or "filings" in exotic[0]["system_prompt"].lower()

    def test_exotic_agent_on_first_iteration(self, client, mock_call_llm):
        """LLM immediately requests create_data_agent without standard tools.

        Expected: needs_data with 0 standard + 1 exotic required_agents.
        """
        mock_call_llm.return_value = json.dumps({
            "action": "create_data_agent",
            "agent_name": "options-chain",
            "agent_description": "Fetch options chain data with greeks",
            "data_type": "options chain",
            "reasoning": "Standard tools don't provide options data",
        })

        resp = client.post(
            "/agents/custom",
            json={
                "stocks": ["TSLA"],
                "system_prompt": "Analyze TSLA options activity",
            },
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "needs_data"
        agents = body["required_agents"]
        assert len(agents) == 1  # only the exotic agent
        assert agents[0]["name"] == "options-chain"
        assert agents[0]["source"] == "web_search"
        assert agents[0]["type"] == "data"
        assert agents[0]["system_prompt"]  # non-empty

    def test_needs_data_response_has_all_fe_required_fields(self, client, mock_call_llm):
        """Validate every required_agents entry has the fields the FE needs.

        FE reads: name, type, source, description
        FE reads (exotic only): system_prompt, temperature, max_tokens
        """
        mock_call_llm.side_effect = [
            # Discover one standard tool
            json.dumps({
                "action": "call_tool",
                "tool": "fundamentals",
                "reasoning": "Need fundamental metrics",
            }),
            # Then create exotic agent
            json.dumps({
                "action": "create_data_agent",
                "agent_name": "insider-trades",
                "agent_description": "Fetch insider trading transactions",
                "data_type": "insider trading",
                "reasoning": "Need insider transaction data",
            }),
        ]

        resp = client.post(
            "/agents/custom",
            json={
                "stocks": ["AAPL"],
                "system_prompt": "Analyze insider activity for AAPL",
            },
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "needs_data"
        agents = body["required_agents"]

        # Standard agent: FE needs name, type, source, description
        std = next(a for a in agents if a["source"] == "eh_pipeline")
        assert "name" in std
        assert "type" in std
        assert "source" in std
        assert "description" in std

        # Exotic agent: FE needs all standard fields + system_prompt, temperature, max_tokens
        exo = next(a for a in agents if a["source"] == "web_search")
        assert "name" in exo
        assert "type" in exo
        assert "source" in exo
        assert "description" in exo
        assert "system_prompt" in exo
        assert "temperature" in exo
        assert "max_tokens" in exo

    def test_fetch_mode_exhausts_tools_returns_success(
        self, client, mock_call_llm, mock_execute_tool
    ):
        """execution_mode=fetch_data: tools exhaust → forced final response (not needs_data).

        When FE executes an exotic data agent, it sends execution_mode=fetch_data.
        The backend must NOT return needs_data — it should execute tools and return success.
        """
        mock_call_llm.side_effect = [
            # Iter 1: call web_search
            json.dumps({
                "action": "call_tool",
                "tool": "web_search",
                "reasoning": "Search for insider trading data",
            }),
            # Iter 2: all tools exhausted (allow_agent_creation=False), loop forces final
            # This call is for generate_final_response
            json.dumps({
                "summary": "Found insider trading data for AAPL",
                "recommendations": ["Monitor insider buying trends"],
                "confidence": 0.7,
                "key_insights": ["CEO purchased shares"],
                "risks": ["Limited data availability"],
            }),
        ]
        mock_execute_tool.return_value = {
            "web_search_data": {"AAPL": {"results": [{"title": "Insider buys"}]}}
        }

        resp = client.post(
            "/agents/custom",
            json={
                "stocks": ["AAPL"],
                "system_prompt": "Fetch insider trading data",
                "execution_mode": "fetch_data",
            },
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body.get("required_agents") is None  # NOT needs_data
        assert body["analysis"] is not None

    def test_multiple_standard_tools_discovered_no_exotic(self, client, mock_call_llm):
        """Discovery finds 3 standard tools, LLM generates response — no exotic agent.

        Expected: needs_data with 3 standard required_agents (all source=eh_pipeline).
        """
        mock_call_llm.side_effect = [
            # Iter 1: discover earnings
            json.dumps({
                "action": "call_tool",
                "tool": "earnings",
                "reasoning": "Need earnings data",
            }),
            # Iter 2: discover technical
            json.dumps({
                "action": "call_tool",
                "tool": "technical",
                "reasoning": "Need technical indicators",
            }),
            # Iter 3: discover fundamentals (max_iterations=3 for /agents/custom)
            json.dumps({
                "action": "call_tool",
                "tool": "fundamentals",
                "reasoning": "Need fundamental metrics",
            }),
        ]

        resp = client.post(
            "/agents/custom",
            json={
                "stocks": ["MSFT"],
                "system_prompt": "Comprehensive analysis of MSFT",
            },
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "needs_data"
        agents = body["required_agents"]
        assert len(agents) == 3
        # All standard — no exotic
        assert all(a["source"] == "eh_pipeline" for a in agents)
        names = [a["name"] for a in agents]
        assert "earnings" in names
        assert "technical" in names
        assert "fundamentals" in names


class TestNeedsDataCreateAndExecute:
    """End-to-end: needs_data → CREATE agents → EXECUTE them → get data → analyze.

    Simulates the full FE canvas flow:
    [1] POST /agents/custom (no input_data) → needs_data + required_agents
    [2] POST /agents (CREATE each data agent from required_agents spec)
    [3] POST /agents/{id}/analyze (EXECUTE created agent → pipeline → SymbolFeatures)
    [4] POST /agents/custom (input_data = collected SymbolFeatures) → final analysis
    """

    def test_create_standard_agent_get_data_then_analyze(
        self,
        client, mock_call_llm, mock_execute_tool,
        mock_stage2, mock_stage3, mock_call_llm_full,
    ):
        """Full flow: needs_data → create earnings agent → run pipeline → analyze.

        [1] POST /agents/custom → needs_data with [earnings]
        [2] POST /agents (create earnings data agent from required_agents spec)
        [3] POST /agents/{id}/analyze → SymbolFeatures via pipeline
        [4] POST /agents/custom (input_data=SymbolFeatures) → final analysis
        """
        # ── Step 1: Discovery → needs_data ──
        mock_call_llm.return_value = json.dumps({
            "action": "call_tool", "tool": "earnings",
            "reasoning": "Need earnings data to analyze",
        })

        step1 = client.post("/agents/custom", json={
            "stocks": ["AAPL"],
            "system_prompt": "Analyze AAPL earnings outlook",
        })
        assert step1.status_code == 200
        step1_body = step1.json()
        assert step1_body["status"] == "needs_data"
        required_agents = step1_body["required_agents"]
        assert len(required_agents) >= 1
        earnings_spec = next(a for a in required_agents if a["name"] == "earnings")
        assert earnings_spec["type"] == "data"
        assert earnings_spec["source"] == "eh_pipeline"

        # ── Step 2: CREATE the data agent from required_agents spec ──
        create_resp = client.post("/agents", json={
            "name": earnings_spec["name"],
            "description": earnings_spec["description"],
            "type": earnings_spec["type"],
            "source": "built-in",  # FE maps eh_pipeline → built-in for CRUD
            "system_prompt": f"Fetch {earnings_spec['name']} data for given stocks.",
        })
        assert create_resp.status_code == 201
        created_agent = create_resp.json()
        agent_id = created_agent["agent_id"]
        assert created_agent["type"] == "data"
        assert created_agent["name"] == "earnings"

        # ── Step 3: EXECUTE created agent → pipeline → SymbolFeatures ──
        mock_execute_tool.return_value = make_earnings_result(["AAPL"])

        analyze_resp = client.post(
            f"/agents/{agent_id}/analyze",
            json={"task": "collect earnings data", "stocks": ["AAPL"]},
        )
        assert analyze_resp.status_code == 200
        data_body = analyze_resp.json()
        assert data_body["status"] == "success"
        assert data_body["agent_id"] == agent_id

        # Parse SymbolFeatures from pipeline output
        symbol_features = json.loads(data_body["analysis"])
        assert "AAPL" in symbol_features
        assert "market_sentiment" in symbol_features["AAPL"]
        assert "technical_signal" in symbol_features["AAPL"]
        assert "fundamental_health" in symbol_features["AAPL"]

        # ── Step 4: Re-run custom agent with collected SymbolFeatures ──
        mock_call_llm_full.return_value = make_llm_full_response(
            content="AAPL earnings are strong. EPS beat estimates. Buy recommendation.",
            reasoning="SymbolFeatures show bullish sentiment with high confidence.",
        )

        step4 = client.post("/agents/custom", json={
            "stocks": ["AAPL"],
            "system_prompt": "Analyze AAPL earnings outlook",
            "input_data": {"earnings": symbol_features},
        })
        assert step4.status_code == 200
        step4_body = step4.json()
        assert step4_body["status"] == "success"
        assert step4_body["analysis"] is not None
        assert "AAPL" in step4_body["analysis"]
        assert step4_body.get("required_agents") is None  # Done — no more needs_data

    def test_create_exotic_agent_get_data_then_analyze(
        self,
        client, mock_call_llm, mock_execute_tool,
        mock_search_for_stocks, mock_stage2, mock_stage3,
        mock_call_llm_full,
    ):
        """Full flow: needs_data → create exotic web_search agent → pipeline → analyze.

        [1] POST /agents/custom → needs_data with [{exotic: SEC filings}]
        [2] POST /agents (create web_search data agent from required_agents spec)
        [3] POST /agents/{id}/analyze → web_search → pipeline → SymbolFeatures
        [4] POST /agents/custom (input_data=SymbolFeatures) → final analysis
        """
        # ── Step 1: Discovery → exotic agent needed ──
        mock_call_llm.return_value = json.dumps({
            "action": "create_data_agent",
            "agent_name": "sec-filings",
            "agent_description": "Fetch SEC 10-K filings for AAPL",
            "data_type": "SEC filings",
            "reasoning": "Standard tools don't provide SEC filing data",
        })

        step1 = client.post("/agents/custom", json={
            "stocks": ["AAPL"],
            "system_prompt": "Analyze AAPL SEC filings for risk factors",
        })
        assert step1.status_code == 200
        step1_body = step1.json()
        assert step1_body["status"] == "needs_data"
        required_agents = step1_body["required_agents"]

        exotic_spec = next(a for a in required_agents if a["source"] == "web_search")
        assert exotic_spec["name"] == "sec-filings"
        assert exotic_spec["system_prompt"]  # Has generated system prompt

        # ── Step 2: CREATE the exotic agent using spec from required_agents ──
        create_resp = client.post("/agents", json={
            "name": exotic_spec["name"],
            "description": exotic_spec["description"],
            "type": exotic_spec["type"],
            "source": "web_search",
            "system_prompt": exotic_spec["system_prompt"],
        })
        assert create_resp.status_code == 201
        created_agent = create_resp.json()
        agent_id = created_agent["agent_id"]
        assert created_agent["type"] == "data"
        assert created_agent["source"] == "web_search"

        # ── Step 3: EXECUTE exotic agent → web_search → pipeline → SymbolFeatures ──
        mock_search_for_stocks.return_value = make_web_search_result(["AAPL"])

        analyze_resp = client.post(
            f"/agents/{agent_id}/analyze",
            json={"task": "fetch SEC filings", "stocks": ["AAPL"]},
        )
        assert analyze_resp.status_code == 200
        data_body = analyze_resp.json()
        assert data_body["status"] == "success"
        assert data_body["agent_id"] == agent_id

        # Parse SymbolFeatures from pipeline output
        symbol_features = json.loads(data_body["analysis"])
        assert "AAPL" in symbol_features
        assert "market_sentiment" in symbol_features["AAPL"]

        # ── Step 4: Re-run custom agent with collected data ──
        mock_call_llm_full.return_value = make_llm_full_response(
            content="AAPL SEC filings reveal strong revenue growth but increased litigation risk.",
            reasoning="10-K risk factors section highlights ongoing patent disputes.",
        )

        step4 = client.post("/agents/custom", json={
            "stocks": ["AAPL"],
            "system_prompt": "Analyze AAPL SEC filings for risk factors",
            "input_data": {"sec-filings": symbol_features},
        })
        assert step4.status_code == 200
        step4_body = step4.json()
        assert step4_body["status"] == "success"
        assert step4_body["analysis"] is not None
        assert step4_body.get("required_agents") is None

    def test_mixed_standard_and_exotic_create_execute_analyze(
        self,
        client, mock_call_llm, mock_execute_tool,
        mock_search_for_stocks, mock_stage2, mock_stage3,
        mock_call_llm_full,
    ):
        """Full flow with BOTH standard + exotic: create all → execute all → analyze.

        [1] POST /agents/custom → needs_data with [earnings, {exotic: insider-trades}]
        [2] POST /agents × 2 (create both agents)
        [3] POST /agents/{id}/analyze × 2 (execute both → SymbolFeatures each)
        [4] POST /agents/custom (input_data = merged data from both) → final analysis
        """
        # ── Step 1: Discovery → mixed needs_data ──
        mock_call_llm.side_effect = [
            json.dumps({
                "action": "call_tool", "tool": "earnings",
                "reasoning": "Need quarterly earnings",
            }),
            json.dumps({
                "action": "create_data_agent",
                "agent_name": "insider-trades",
                "agent_description": "Fetch insider trading transactions from SEC",
                "data_type": "insider trading",
                "reasoning": "Need insider trade data not in standard tools",
            }),
        ]

        step1 = client.post("/agents/custom", json={
            "stocks": ["AAPL"],
            "system_prompt": "Analyze AAPL earnings + insider trading activity",
        })
        assert step1.status_code == 200
        step1_body = step1.json()
        assert step1_body["status"] == "needs_data"
        required_agents = step1_body["required_agents"]
        assert len(required_agents) == 2

        standard_specs = [a for a in required_agents if a["source"] == "eh_pipeline"]
        exotic_specs = [a for a in required_agents if a["source"] == "web_search"]
        assert len(standard_specs) == 1
        assert len(exotic_specs) == 1

        # ── Step 2: CREATE both agents ──
        # Standard agent
        create1 = client.post("/agents", json={
            "name": standard_specs[0]["name"],
            "description": standard_specs[0]["description"],
            "type": "data",
            "source": "built-in",
            "system_prompt": f"Fetch {standard_specs[0]['name']} data.",
        })
        assert create1.status_code == 201
        std_agent_id = create1.json()["agent_id"]

        # Exotic agent
        create2 = client.post("/agents", json={
            "name": exotic_specs[0]["name"],
            "description": exotic_specs[0]["description"],
            "type": "data",
            "source": "web_search",
            "system_prompt": exotic_specs[0]["system_prompt"],
        })
        assert create2.status_code == 201
        exotic_agent_id = create2.json()["agent_id"]

        # ── Step 3: EXECUTE both agents → collect SymbolFeatures ──
        collected_data = {}

        # Execute standard earnings agent
        mock_execute_tool.return_value = make_earnings_result(["AAPL"])
        run1 = client.post(
            f"/agents/{std_agent_id}/analyze",
            json={"task": "collect earnings", "stocks": ["AAPL"]},
        )
        assert run1.status_code == 200
        assert run1.json()["status"] == "success"
        collected_data["earnings"] = json.loads(run1.json()["analysis"])

        # Execute exotic insider-trades agent (web_search path)
        mock_search_for_stocks.return_value = make_web_search_result(["AAPL"])
        run2 = client.post(
            f"/agents/{exotic_agent_id}/analyze",
            json={"task": "fetch insider trades", "stocks": ["AAPL"]},
        )
        assert run2.status_code == 200
        assert run2.json()["status"] == "success"
        collected_data["insider-trades"] = json.loads(run2.json()["analysis"])

        # Both have SymbolFeatures
        assert "AAPL" in collected_data["earnings"]
        assert "AAPL" in collected_data["insider-trades"]

        # ── Step 4: Re-run custom agent with ALL collected data ──
        mock_call_llm_full.return_value = make_llm_full_response(
            content="AAPL: Strong earnings + significant insider buying signals confidence.",
            reasoning="Cross-referenced earnings beat with recent insider purchases.",
        )

        step4 = client.post("/agents/custom", json={
            "stocks": ["AAPL"],
            "system_prompt": "Analyze AAPL earnings + insider trading activity",
            "input_data": collected_data,
        })
        assert step4.status_code == 200
        step4_body = step4.json()
        assert step4_body["status"] == "success"
        assert step4_body["analysis"] is not None
        assert "AAPL" in step4_body["analysis"]
        assert step4_body.get("required_agents") is None
        # Verify Path A was taken (LLM got the collected data)
        assert mock_call_llm_full.called


class TestThinkingLoopToolFiltering:
    """Unit-level tests for the remaining_tools filtering fix in run_thinking_loop.

    These test via /agents/think which directly exposes thinking loop results.
    """

    def test_remaining_tools_shrink_prevents_repeat(
        self, client, mock_call_llm, mock_execute_tool
    ):
        """LLM picks earnings then news — should NOT repeat earnings.

        The fix filters already-collected tools from available_tools before each
        think_step call, so the LLM never sees an already-used tool.
        """
        mock_call_llm.side_effect = [
            # Iter 1: call earnings
            json.dumps({
                "action": "call_tool",
                "tool": "earnings",
                "reasoning": "Need earnings data",
            }),
            # Iter 2: call news (earnings no longer in available list)
            json.dumps({
                "action": "call_tool",
                "tool": "news",
                "reasoning": "Need news coverage",
            }),
            # Iter 3: ready to answer
            json.dumps({
                "action": "generate_response",
                "reasoning": "Have sufficient data",
            }),
            # generate_final_response
            json.dumps({
                "summary": "Analysis complete",
                "recommendations": ["Hold"],
                "confidence": 0.75,
                "key_insights": ["Stable earnings"],
                "risks": ["Market volatility"],
            }),
        ]
        mock_execute_tool.return_value = {"data": "mock"}

        resp = client.post(
            "/agents/think",
            json={
                "stocks": ["AAPL"],
                "system_prompt": "Analyze AAPL",
                "max_iterations": 5,
                "available_tools": ["earnings", "news"],
            },
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        # Both tools used — no repeats
        assert set(body["tools_used"]) == {"earnings", "news"}
        # No skip steps — the fix prevents the LLM from even seeing used tools
        actions = [s["action"] for s in body["thinking_steps"]]
        assert "skip" not in actions

    def test_create_data_agent_after_all_tools_exhausted(
        self, client, mock_call_llm, mock_execute_tool
    ):
        """When all standard tools exhausted, LLM sees empty tools list and creates exotic agent.

        This is the key scenario that was broken before the fix:
        Iter 1: earnings → collected
        Iter 2: remaining=[] + allow_agent_creation=True → LLM gets "(No additional standard tools)"
        LLM responds with create_data_agent → status=paused
        """
        mock_call_llm.side_effect = [
            # Iter 1: call the only available tool
            json.dumps({
                "action": "call_tool",
                "tool": "earnings",
                "reasoning": "Need earnings data",
            }),
            # Iter 2: remaining_tools=[], but allow_agent_creation=True
            # LLM sees "(No additional standard tools available)" → creates exotic agent
            json.dumps({
                "action": "create_data_agent",
                "agent_name": "sec-filings",
                "agent_description": "Fetch SEC filings for the company",
                "data_type": "SEC filings",
                "reasoning": "All standard tools used, need SEC filing data",
            }),
        ]
        mock_execute_tool.return_value = {"earnings_data": {"AAPL": {}}}

        resp = client.post(
            "/agents/think",
            json={
                "stocks": ["AAPL"],
                "system_prompt": "Analyze AAPL including SEC filings",
                "max_iterations": 5,
                "available_tools": ["earnings"],  # Only one tool
            },
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "paused"
        assert body["reason"] == "need_data_agent"
        assert body["suggested_data_agent"]["name"] == "sec-filings"
        assert body["suggested_data_agent"]["data_type"] == "SEC filings"
        assert "suggested_system_prompt" in body["suggested_data_agent"]
        assert "earnings" in body["tools_used"]
        assert body["iterations_used"] == 2

    def test_empty_tools_no_agent_creation_forces_response(
        self, client, mock_call_llm, mock_execute_tool
    ):
        """When remaining_tools=[] and allow_agent_creation=False → forced final response.

        No LLM call wasted — the loop short-circuits directly to generate_final_response.
        This tests the fetch_data path via /agents/think with explicit params.
        """
        mock_call_llm.side_effect = [
            # Iter 1: call the only available tool
            json.dumps({
                "action": "call_tool",
                "tool": "web_search",
                "reasoning": "Search for data",
            }),
            # Iter 2: remaining_tools=[], allow_agent_creation=False → forced final response
            # This call is for generate_final_response (NOT think_step)
            json.dumps({
                "summary": "Data collected via web search",
                "recommendations": ["Review findings"],
                "confidence": 0.6,
                "key_insights": ["Found relevant data"],
                "risks": ["Limited sources"],
            }),
        ]
        mock_execute_tool.return_value = {"search_results": {"AAPL": {}}}

        # Import and call run_thinking_loop directly to test allow_agent_creation=False
        # (the /agents/think endpoint always allows agent creation)
        import asyncio
        from services.thinking_engine import run_thinking_loop

        result = asyncio.run(
            run_thinking_loop(
                stocks=["AAPL"],
                system_prompt="Fetch data for AAPL",
                max_iterations=5,
                available_tools=["web_search"],
                allow_agent_creation=False,
            )
        )

        assert result["status"] == "success"
        assert result["final_result"] is not None
        # Only 2 LLM calls: think_step (iter 1) + generate_final_response (iter 2)
        assert mock_call_llm.call_count == 2


# ──────────────────────────────────────────────────────────────────────
# Scenario 7: Full Canvas Flow — Portfolio → Analyzer → needs_data
#   → Execute data agents via named endpoints / custom fetch → Re-analyze
#
# Unlike TestNeedsDataCreateAndExecute which tests CRUD-based agent
# creation (POST /agents → POST /agents/{id}/analyze → SymbolFeatures),
# these tests mirror the ACTUAL FE canvas handleNeedsData() flow:
#   - Standard agents: POST /agents/{name} (named endpoints → raw tool data)
#   - Exotic agents:   POST /agents/custom + execution_mode=fetch_data
#   - Re-run analyzer: POST /agents/custom + input_data={collected data}
# ──────────────────────────────────────────────────────────────────────


class TestCanvasNeedsDataFlow:
    """Full canvas flow: portfolio → analyzer → needs_data → execute agents → re-analyze.

    Mirrors the FE useRunAgent.js handleNeedsData() implementation exactly:
    [1] POST /agents/custom (no input_data) → needs_data + required_agents
    [2] For each standard agent:  POST /agents/{name} → raw tool data
        For each exotic agent:    POST /agents/custom + execution_mode=fetch_data → LLM data
    [3] POST /agents/custom (input_data = all collected data) → final analysis
    """

    def test_portfolio_to_analyzer_standard_agents_canvas_flow(
        self,
        client, mock_call_llm, mock_execute_tool, mock_call_llm_full,
    ):
        """Full canvas flow with standard agents only.

        POST /agents/custom (no input_data)    → needs_data [earnings, news]
        POST /agents/earnings                   → raw earnings data
        POST /agents/news                       → raw news data
        POST /agents/custom (input_data={both}) → success + analysis
        """
        # ── Step 1: Discovery → needs_data ──
        mock_call_llm.side_effect = [
            json.dumps({
                "action": "call_tool", "tool": "earnings",
                "reasoning": "Need quarterly earnings data",
            }),
            json.dumps({
                "action": "call_tool", "tool": "news",
                "reasoning": "Need recent news coverage",
            }),
        ]

        step1 = client.post("/agents/custom", json={
            "stocks": ["AAPL"],
            "system_prompt": "Analyze AAPL earnings and news sentiment",
        })
        assert step1.status_code == 200
        step1_body = step1.json()
        assert step1_body["status"] == "needs_data"
        agents = step1_body["required_agents"]
        assert len(agents) == 2

        # Verify all FE-required fields on standard agents
        for agent in agents:
            assert agent["source"] == "eh_pipeline"
            assert agent["type"] == "data"
            assert "name" in agent
            assert "description" in agent

        agent_names = {a["name"] for a in agents}
        assert agent_names == {"earnings", "news"}

        # ── Step 2: Execute standard agents via named endpoints ──
        collected_data = {}

        # POST /agents/earnings → raw tool data
        earnings_raw = {"earnings_data_by_symbol": {"AAPL": {"eps": 6.42, "revenue": "94.8B"}}}
        mock_execute_tool.return_value = earnings_raw
        earnings_resp = client.post("/agents/earnings", json={"stocks": ["AAPL"]})
        assert earnings_resp.status_code == 200
        collected_data["earnings"] = earnings_resp.json()

        # POST /agents/news → raw tool data
        news_raw = {"news_data_by_symbol": {"AAPL": {"headlines": ["AAPL beats estimates"]}}}
        mock_execute_tool.return_value = news_raw
        news_resp = client.post("/agents/news", json={"stocks": ["AAPL"]})
        assert news_resp.status_code == 200
        collected_data["news"] = news_resp.json()

        # ── Step 3: Re-run analyzer with collected data ──
        mock_call_llm_full.return_value = make_llm_full_response(
            content="AAPL: Strong earnings beat + positive news sentiment. Buy recommendation.",
            reasoning="EPS of 6.42 beat estimates, news coverage overwhelmingly positive.",
        )

        step3 = client.post("/agents/custom", json={
            "stocks": ["AAPL"],
            "system_prompt": "Analyze AAPL earnings and news sentiment",
            "input_data": collected_data,
        })
        assert step3.status_code == 200
        step3_body = step3.json()
        assert step3_body["status"] == "success"
        assert step3_body["analysis"] is not None
        assert "AAPL" in step3_body["analysis"]
        assert step3_body.get("required_agents") is None  # Not needs_data again
        assert mock_call_llm_full.called  # Path A was taken

    def test_portfolio_to_analyzer_with_exotic_agent_canvas_flow(
        self,
        client, mock_call_llm, mock_execute_tool, mock_call_llm_full,
    ):
        """Full canvas flow with mixed standard + exotic agents.

        POST /agents/custom (no input_data)                                    → needs_data [earnings, {sec-filings}]
        POST /agents/earnings                                                   → raw earnings data
        POST /agents/custom (system_prompt=exotic, execution_mode=fetch_data)   → exotic data
        POST /agents/custom (input_data={all collected})                        → success + analysis
        """
        # ── Step 1: Discovery → needs_data (standard + exotic) ──
        mock_call_llm.side_effect = [
            json.dumps({
                "action": "call_tool", "tool": "earnings",
                "reasoning": "Need quarterly earnings data",
            }),
            json.dumps({
                "action": "create_data_agent",
                "agent_name": "sec-filings",
                "agent_description": "Fetch SEC 10-K and 10-Q filings",
                "data_type": "SEC filings",
                "reasoning": "Standard tools don't provide SEC filing data",
            }),
        ]

        step1 = client.post("/agents/custom", json={
            "stocks": ["AAPL"],
            "system_prompt": "Deep analysis of AAPL including SEC filings",
        })
        assert step1.status_code == 200
        step1_body = step1.json()
        assert step1_body["status"] == "needs_data"
        agents = step1_body["required_agents"]
        assert len(agents) == 2

        standard = [a for a in agents if a["source"] == "eh_pipeline"]
        exotic = [a for a in agents if a["source"] == "web_search"]
        assert len(standard) == 1
        assert len(exotic) == 1
        assert standard[0]["name"] == "earnings"
        assert exotic[0]["name"] == "sec-filings"
        # Exotic agent must have system_prompt for FE to use in fetch call
        exotic_system_prompt = exotic[0]["system_prompt"]
        assert exotic_system_prompt  # non-empty

        # ── Step 2a: Execute standard agent via named endpoint ──
        collected_data = {}
        earnings_raw = {"earnings_data_by_symbol": {"AAPL": {"eps": 6.42}}}
        mock_execute_tool.return_value = earnings_raw
        earnings_resp = client.post("/agents/earnings", json={"stocks": ["AAPL"]})
        assert earnings_resp.status_code == 200
        collected_data["earnings"] = earnings_resp.json()

        # ── Step 2b: Execute exotic agent via /agents/custom + fetch_data ──
        # Reset mock_call_llm for the exotic agent's fetch_data thinking loop
        mock_call_llm.side_effect = [
            # Iter 1: call web_search
            json.dumps({
                "action": "call_tool", "tool": "web_search",
                "reasoning": "Search for SEC filing data",
            }),
            # Iter 2: generate final response (tools exhausted or fetch complete)
            json.dumps({
                "summary": "Found SEC 10-K data for AAPL",
                "recommendations": ["Review risk factors section"],
                "confidence": 0.7,
                "key_insights": ["Revenue growth 15% YoY"],
                "risks": ["Patent litigation pending"],
            }),
        ]
        mock_execute_tool.return_value = {
            "web_search_data": {"AAPL": {"results": [{"title": "AAPL 10-K Filing"}]}}
        }

        exotic_resp = client.post("/agents/custom", json={
            "stocks": ["AAPL"],
            "system_prompt": exotic_system_prompt,
            "execution_mode": "fetch_data",
        })
        assert exotic_resp.status_code == 200
        exotic_body = exotic_resp.json()
        assert exotic_body["status"] == "success"
        assert exotic_body.get("required_agents") is None  # Not needs_data
        collected_data["sec-filings"] = exotic_body["analysis"]

        # ── Step 3: Re-run analyzer with ALL collected data ──
        mock_call_llm_full.return_value = make_llm_full_response(
            content="AAPL: Strong earnings + SEC filings show solid fundamentals. Buy.",
            reasoning="EPS beat + 10-K shows revenue growth and manageable risk factors.",
        )

        step3 = client.post("/agents/custom", json={
            "stocks": ["AAPL"],
            "system_prompt": "Deep analysis of AAPL including SEC filings",
            "input_data": collected_data,
        })
        assert step3.status_code == 200
        step3_body = step3.json()
        assert step3_body["status"] == "success"
        assert step3_body["analysis"] is not None
        assert "AAPL" in step3_body["analysis"]
        assert step3_body.get("required_agents") is None
        assert mock_call_llm_full.called

    def test_portfolio_to_analyzer_exotic_only_canvas_flow(
        self,
        client, mock_call_llm, mock_execute_tool, mock_call_llm_full,
    ):
        """Canvas flow where LLM immediately requests exotic agent (no standard tools).

        POST /agents/custom (no input_data)                                    → needs_data [{options-chain}]
        POST /agents/custom (system_prompt=exotic, execution_mode=fetch_data)   → exotic data
        POST /agents/custom (input_data={collected})                            → success + analysis
        """
        # ── Step 1: Discovery → needs_data (exotic only) ──
        mock_call_llm.return_value = json.dumps({
            "action": "create_data_agent",
            "agent_name": "options-chain",
            "agent_description": "Fetch options chain data with greeks",
            "data_type": "options chain",
            "reasoning": "Standard tools don't provide options data",
        })

        step1 = client.post("/agents/custom", json={
            "stocks": ["TSLA"],
            "system_prompt": "Analyze TSLA options activity and implied volatility",
        })
        assert step1.status_code == 200
        step1_body = step1.json()
        assert step1_body["status"] == "needs_data"
        agents = step1_body["required_agents"]
        assert len(agents) == 1
        assert agents[0]["name"] == "options-chain"
        assert agents[0]["source"] == "web_search"
        assert agents[0]["type"] == "data"
        exotic_system_prompt = agents[0]["system_prompt"]
        assert exotic_system_prompt  # non-empty, usable for fetch call

        # Verify exotic agent has all FE-required fields
        assert "description" in agents[0]
        assert "temperature" in agents[0]
        assert "max_tokens" in agents[0]

        # ── Step 2: Execute exotic agent via /agents/custom + fetch_data ──
        collected_data = {}
        mock_call_llm.side_effect = [
            json.dumps({
                "action": "call_tool", "tool": "web_search",
                "reasoning": "Search for options chain data",
            }),
            json.dumps({
                "summary": "Found options chain data for TSLA",
                "recommendations": ["High IV suggests upcoming move"],
                "confidence": 0.65,
                "key_insights": ["Put/call ratio at 0.8", "IV rank 85th percentile"],
                "risks": ["Earnings announcement approaching"],
            }),
        ]
        mock_execute_tool.return_value = {
            "web_search_data": {"TSLA": {"results": [{"title": "TSLA Options Chain"}]}}
        }

        exotic_resp = client.post("/agents/custom", json={
            "stocks": ["TSLA"],
            "system_prompt": exotic_system_prompt,
            "execution_mode": "fetch_data",
        })
        assert exotic_resp.status_code == 200
        exotic_body = exotic_resp.json()
        assert exotic_body["status"] == "success"
        assert exotic_body.get("required_agents") is None
        collected_data["options-chain"] = exotic_body["analysis"]

        # ── Step 3: Re-run analyzer with collected data ──
        mock_call_llm_full.return_value = make_llm_full_response(
            content="TSLA: High implied volatility with bullish options flow. Consider straddle.",
            reasoning="Put/call ratio and IV rank suggest significant move expected.",
        )

        step3 = client.post("/agents/custom", json={
            "stocks": ["TSLA"],
            "system_prompt": "Analyze TSLA options activity and implied volatility",
            "input_data": collected_data,
        })
        assert step3.status_code == 200
        step3_body = step3.json()
        assert step3_body["status"] == "success"
        assert step3_body["analysis"] is not None
        assert step3_body.get("required_agents") is None  # Done — no more needs_data
        assert mock_call_llm_full.called  # Path A was taken
