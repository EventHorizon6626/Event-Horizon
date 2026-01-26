"""
Stage 1 Orchestrator

Coordinates parallel execution of Stage 1 data retrieval agents.
Implements the data collection pipeline for heterogeneous data sources.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from data_pipeline.stage_1.agents.candlestick_agent import CandlestickAgent
from data_pipeline.stage_1.agents.earnings_agent import EarningsAgent
from data_pipeline.stage_1.agents.news_agent import NewsAgent
from data_pipeline.stage_1.agents.technical_agent import TechnicalAgent
from data_pipeline.stage_1.agents.fundamentals_agent import FundamentalsAgent
from data_pipeline.stage_1.models.schemas import Stage1Output


class Stage1Orchestrator:
    """
    Stage 1 Orchestrator - Data Retrieval Coordination

    Responsibilities:
    - Manages parallel execution of data retrieval agents
    - Aggregates results from all agents
    - Handles errors and partial failures
    - Produces unified Stage 1 output

    Architecture Pattern: Parallel (Independent Agents)
    - All Stage 1 agents run simultaneously
    - No dependencies between agents
    - Maximum throughput and efficiency
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Stage 1 Orchestrator

        Args:
            config: Configuration dictionary with keys:
                - enabled_agents: List of agent names to enable
                - agent_configs: Dict of agent-specific configs
                - max_workers: Max parallel workers (default: 5)
        """
        self.config = config or {}
        self.logger = logging.getLogger("data_pipeline.stage_1.orchestrator")

        # Determine which agents to enable
        self.enabled_agents = self.config.get(
            "enabled_agents", ["candlestick", "earnings", "news", "technical", "fundamentals"]
        )

        # Max parallel workers
        self.max_workers = self.config.get("max_workers", 5)

        # Agent configurations
        self.agent_configs = self.config.get("agent_configs", {})

        self.logger.info(
            f"Stage 1 Orchestrator initialized: "
            f"enabled_agents={self.enabled_agents}, "
            f"max_workers={self.max_workers}"
        )

    def execute(
        self, portfolio: Union[Dict[str, Any], List[str]]
    ) -> Dict[str, Any]:
        """
        Execute Stage 1 data retrieval for a portfolio

        Args:
            portfolio: Either:
                - Dict with "portfolio" key containing symbols
                - List of symbols directly

        Returns:
            Dict containing Stage1Output with all retrieved data
        """
        start_time = time.time()

        # Parse portfolio
        if isinstance(portfolio, dict):
            symbols = portfolio.get("portfolio", portfolio.get("symbols", []))
            portfolio_id = portfolio.get("portfolio_id", "unknown")
        elif isinstance(portfolio, list):
            symbols = portfolio
            portfolio_id = "unknown"
        else:
            raise ValueError("Portfolio must be dict or list")

        if not symbols:
            raise ValueError("No symbols provided in portfolio")

        self.logger.info(
            f"Starting Stage 1 data retrieval for portfolio {portfolio_id}"
        )
        self.logger.info(f"Symbols: {symbols}")
        self.logger.info(f"Enabled agents: {self.enabled_agents}")

        # Initialize Stage1Output
        stage1_output = Stage1Output(
            portfolio_id=portfolio_id,
            symbols=symbols,
            timestamp=datetime.now().isoformat(),
        )

        # Execute agents in parallel
        results = self._execute_agents_parallel(
            {"portfolio": symbols, "portfolio_id": portfolio_id}
        )

        # Aggregate results into Stage1Output
        agents_executed = []
        all_errors = []

        for agent_name, result in results.items():
            if result.get("status") == "failed":
                all_errors.append(
                    {
                        "agent": agent_name,
                        "error": result.get("error", "Unknown error"),
                    }
                )
                continue

            agents_executed.append(agent_name)

            # Map agent results to Stage1Output fields
            if agent_name == "candlestick":
                stage1_output.chart_data = result.get("chart_data_by_symbol", {})
                if result.get("errors"):
                    all_errors.extend(
                        [{"agent": "candlestick", **err} for err in result["errors"]]
                    )

            elif agent_name == "earnings":
                stage1_output.earnings_data = result.get("earnings_data_by_symbol", {})
                if result.get("errors"):
                    all_errors.extend(
                        [{"agent": "earnings", **err} for err in result["errors"]]
                    )

            elif agent_name == "news":
                stage1_output.news_data = result.get("news_data_by_symbol", {})
                if result.get("errors"):
                    all_errors.extend(
                        [{"agent": "news", **err} for err in result["errors"]]
                    )

            elif agent_name == "technical":
                stage1_output.technical_data = result.get("technical_data_by_symbol", {})
                if result.get("errors"):
                    all_errors.extend(
                        [{"agent": "technical", **err} for err in result["errors"]]
                    )

            elif agent_name == "fundamentals":
                stage1_output.fundamentals_data = result.get("fundamentals_data_by_symbol", {})
                if result.get("errors"):
                    all_errors.extend(
                        [{"agent": "fundamentals", **err} for err in result["errors"]]
                    )

        # Update metadata
        stage1_output.agents_executed = agents_executed
        stage1_output.errors = all_errors
        stage1_output.execution_time_seconds = time.time() - start_time

        # Determine overall status
        if len(agents_executed) == 0:
            stage1_output.status = "failed"
        elif len(agents_executed) < len(self.enabled_agents):
            stage1_output.status = "partial_success"
        else:
            stage1_output.status = "success"

        self.logger.info(
            f"Stage 1 execution completed in {stage1_output.execution_time_seconds:.2f}s"
        )
        self.logger.info(f"Status: {stage1_output.status}")
        self.logger.info(f"Agents executed: {agents_executed}")

        return {
            "status": stage1_output.status,
            "stage1_output": stage1_output,
            "execution_time_seconds": stage1_output.execution_time_seconds,
            "agents_executed": agents_executed,
            "errors": all_errors,
        }

    def _execute_agents_parallel(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all enabled agents in parallel

        Args:
            input_data: Input data for agents

        Returns:
            Dict mapping agent_name -> agent_result
        """
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all agent tasks
            future_to_agent = {}

            for agent_name in self.enabled_agents:
                future = executor.submit(
                    self._execute_single_agent, agent_name, input_data
                )
                future_to_agent[future] = agent_name

            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    result = future.result()
                    results[agent_name] = result
                    self.logger.info(f"✓ {agent_name} completed: {result.get('status')}")
                except Exception as e:
                    self.logger.error(f"✗ {agent_name} failed: {str(e)}")
                    results[agent_name] = {"status": "failed", "error": str(e)}

        return results

    def _execute_single_agent(
        self, agent_name: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single agent

        Args:
            agent_name: Name of agent to execute
            input_data: Input data for agent

        Returns:
            Agent execution result
        """
        self.logger.info(f"Starting {agent_name}...")

        try:
            # Get agent config
            agent_config = self.agent_configs.get(agent_name, {})

            # Initialize and execute agent
            if agent_name == "candlestick":
                agent = CandlestickAgent(config=agent_config)
            elif agent_name == "earnings":
                agent = EarningsAgent(config=agent_config)
            elif agent_name == "news":
                agent = NewsAgent(config=agent_config)
            elif agent_name == "technical":
                agent = TechnicalAgent(config=agent_config)
            elif agent_name == "fundamentals":
                agent = FundamentalsAgent(config=agent_config)
            else:
                raise ValueError(f"Unknown agent: {agent_name}")

            # Execute agent
            result = agent.execute(input_data)

            # Return the internal result
            return result.get("result", {})

        except Exception as e:
            self.logger.error(f"Agent {agent_name} execution failed: {str(e)}")
            raise

    def get_enabled_agents(self) -> List[str]:
        """Get list of enabled agents"""
        return self.enabled_agents

    def set_enabled_agents(self, agents: List[str]):
        """Set which agents to enable"""
        valid_agents = ["candlestick", "earnings", "news", "technical", "fundamentals"]
        invalid = [a for a in agents if a not in valid_agents]
        if invalid:
            raise ValueError(f"Invalid agents: {invalid}. Valid: {valid_agents}")
        self.enabled_agents = agents
        self.logger.info(f"Enabled agents updated: {self.enabled_agents}")
