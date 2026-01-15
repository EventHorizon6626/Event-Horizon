"""Base Agent Class for Event Horizon Multi-Agent System"""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict


class BaseAgent(ABC):
    """Base class for all Event Horizon agents"""

    def __init__(self, agent_name: str, config: Dict[str, Any] = None):
        """
        Initialize base agent

        Args:
            agent_name: Name identifier for the agent
            config: Optional configuration dictionary
        """
        self.agent_name = agent_name
        self.config = config or {}
        self.logger = logging.getLogger(f"agents.{agent_name}")

        self.logger.info(f"Initialized {agent_name}")

    def execute(self, input_data: Any) -> Dict[str, Any]:
        """
        Execute agent with input data and return structured result

        Args:
            input_data: Input data for agent execution

        Returns:
            Dict containing execution results and metadata
        """
        execution_id = str(uuid.uuid4())
        start_time = datetime.now()

        self.logger.info(f"Starting execution {execution_id} for {self.agent_name}")

        try:
            # Call subclass implementation
            result = self._execute_internal(input_data)
            status = "success"
            error = None

            self.logger.info(f"Execution {execution_id} completed successfully")

        except Exception as e:
            self.logger.error(
                f"Execution {execution_id} failed: {str(e)}", exc_info=True
            )
            result = None
            status = "failed"
            error = str(e)

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        return {
            "execution_id": execution_id,
            "agent_name": self.agent_name,
            "status": status,
            "result": result,
            "error": error,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "execution_time_seconds": execution_time,
        }

    @abstractmethod
    def _execute_internal(self, input_data: Any) -> Any:
        """
        Internal execution logic - must be implemented by subclass

        Args:
            input_data: Input data for processing

        Returns:
            Agent-specific result

        Raises:
            NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError("Subclass must implement _execute_internal()")

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value with optional default"""
        return self.config.get(key, default)
