"""Base Orchestrator Class for Event Horizon Multi-Layer System"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseOrchestrator(ABC):
    """
    Base class for all layer orchestrators

    Provides common orchestration framework for managing agents within a layer.
    Used by Layer 1, Layer 2, and Layer 3 orchestrators.
    """

    def __init__(self, layer_name: str, config: Dict[str, Any] = None):
        """
        Initialize base orchestrator

        Args:
            layer_name: Name of the layer (e.g., "layer_1", "layer_2")
            config: Optional configuration dictionary
        """
        self.layer_name = layer_name
        self.config = config or {}
        self.logger = logging.getLogger(f"orchestrator.{layer_name}")

        self.enabled_agents = self.config.get("enabled_agents", [])
        self.max_workers = self.config.get("max_workers", 5)
        self.agent_configs = self.config.get("agent_configs", {})

        self.logger.info(
            f"Initialized {layer_name} orchestrator: "
            f"enabled_agents={self.enabled_agents}, max_workers={self.max_workers}"
        )

    @abstractmethod
    def execute(self, input_data: Any) -> Dict[str, Any]:
        """
        Execute the layer's processing pipeline

        Args:
            input_data: Input data for the layer

        Returns:
            Dict containing layer output and metadata

        Raises:
            NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError("Subclass must implement execute()")

    def get_enabled_agents(self) -> List[str]:
        """
        Get list of enabled agents

        Returns:
            List of agent names that are enabled
        """
        return self.enabled_agents

    def set_enabled_agents(self, agents: List[str]):
        """
        Set which agents to enable

        Args:
            agents: List of agent names to enable

        Raises:
            ValueError: If any agent name is invalid for this layer
        """
        # Validation should be done in subclass
        self.enabled_agents = agents
        self.logger.info(f"Enabled agents updated: {self.enabled_agents}")

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with optional default

        Args:
            key: Configuration key to retrieve
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
