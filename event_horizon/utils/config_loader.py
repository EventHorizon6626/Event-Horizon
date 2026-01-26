"""Configuration Loader for Event Horizon"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigLoader:
    """Load and manage agent configuration"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration loader

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file

        Returns:
            Configuration dictionary
        """
        config_file = Path(self.config_path)

        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please create config.yaml in the project root."
            )

        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        # Replace environment variables
        config = self._replace_env_vars(config)

        return config

    def _replace_env_vars(self, config: Any) -> Any:
        """
        Replace ${ENV_VAR} placeholders with environment variables

        Args:
            config: Configuration object (dict, list, or value)

        Returns:
            Configuration with environment variables replaced
        """
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif (
            isinstance(config, str) and config.startswith("${") and config.endswith("}")
        ):
            env_var = config[2:-1]
            return os.getenv(env_var, "")
        else:
            return config

    def is_agent_enabled(self, agent_name: str) -> bool:
        """
        Check if an agent is enabled

        Args:
            agent_name: Name of the agent (e.g., 'news_agent', 'report_agent')

        Returns:
            True if agent is enabled, False otherwise
        """
        agents = self.config.get("agents", {})
        agent_config = agents.get(agent_name, {})
        return agent_config.get("enabled", False)

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific agent

        Args:
            agent_name: Name of the agent

        Returns:
            Agent configuration dictionary
        """
        agents = self.config.get("agents", {})
        agent_config = agents.get(agent_name, {})
        return agent_config.get("config", {})

    def get_enabled_agents(self) -> list:
        """
        Get list of enabled agent names

        Returns:
            List of enabled agent names
        """
        agents = self.config.get("agents", {})
        return [
            agent_name
            for agent_name, agent_config in agents.items()
            if agent_config.get("enabled", False)
        ]

    def get_api_key(self, key_name: str) -> str:
        """
        Get API key from configuration

        Args:
            key_name: Name of the API key

        Returns:
            API key value
        """
        api_keys = self.config.get("api_keys", {})
        return api_keys.get(key_name, "")

    def get_data_source_config(self, source_name: str) -> Dict[str, Any]:
        """
        Get data source configuration

        Args:
            source_name: Name of data source (e.g., 'yfinance', 'sec_edgar')

        Returns:
            Data source configuration
        """
        data_sources = self.config.get("data_sources", {})
        return data_sources.get(source_name, {})

    def is_data_source_enabled(self, source_name: str) -> bool:
        """
        Check if a data source is enabled

        Args:
            source_name: Name of data source

        Returns:
            True if enabled, False otherwise
        """
        source_config = self.get_data_source_config(source_name)
        return source_config.get("enabled", False)

    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration

        Returns:
            Logging configuration dictionary
        """
        return self.config.get("logging", {})

    def get_output_config(self) -> Dict[str, Any]:
        """
        Get output configuration

        Returns:
            Output configuration dictionary
        """
        return self.config.get("output", {})

    def get_full_config(self) -> Dict[str, Any]:
        """
        Get full configuration

        Returns:
            Complete configuration dictionary
        """
        return self.config

    def print_agent_status(self):
        """Print status of all agents"""
        print("\n" + "=" * 70)
        print(" AGENT CONFIGURATION STATUS")
        print("=" * 70)

        agents = self.config.get("agents", {})
        for agent_name, agent_config in agents.items():
            enabled = agent_config.get("enabled", False)
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            print(f"{agent_name:20s}: {status}")

        print("\nEnabled Agents:", ", ".join(self.get_enabled_agents()) or "None")
        print("=" * 70 + "\n")
