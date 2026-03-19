"""Agent registry — stores and manages agent configurations."""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

logger = logging.getLogger(__name__)

AGENTS_FILE = os.getenv("AGENTS_FILE", "/data/agents.json")

# EH Stage 1 data agent names — these fetch data, not run LLM
DATA_AGENT_NAMES = {"candlestick", "earnings", "news", "technical", "fundamentals"}


class AgentStore:
    def __init__(self):
        self.agents: Dict[str, dict] = {}
        self._load()

    def _load(self):
        """Load agents from disk if available."""
        if os.path.exists(AGENTS_FILE):
            with open(AGENTS_FILE, "r") as f:
                self.agents = json.load(f)
            logger.info("Loaded %d agents from %s", len(self.agents), AGENTS_FILE)
        else:
            logger.info("No agents file found at %s, starting empty", AGENTS_FILE)

    def _save(self):
        """Persist agents to disk."""
        os.makedirs(os.path.dirname(AGENTS_FILE), exist_ok=True)
        with open(AGENTS_FILE, "w") as f:
            json.dump(self.agents, f, indent=2)
        logger.debug("Saved %d agents to %s", len(self.agents), AGENTS_FILE)

    def create(
        self,
        name: str,
        description: str = "",
        system_prompt: str = "",
        agent_type: str = "analysis",
        source: str = None,
        temperature: float = 1.0,
        max_tokens: int = 4096,
        agent_id: str = None,
        deletable: bool = True,
    ) -> dict:
        # Auto-detect data agents by name if caller didn't explicitly set type
        if agent_type == "analysis" and name.lower() in DATA_AGENT_NAMES:
            agent_type = "data"

        # For data agents, auto-detect source if not provided
        if agent_type == "data" and source is None:
            source = "built-in" if name.lower() in DATA_AGENT_NAMES else "custom"

        # Use provided ID (for seed agents) or generate one
        if agent_id is None:
            agent_id = str(uuid.uuid4())[:8]

        # Skip if agent_id already exists (idempotent seeding)
        if agent_id in self.agents:
            logger.debug("create: skipped existing agent_id=%s name=%s", agent_id, name)
            return self.agents[agent_id]

        agent = {
            "agent_id": agent_id,
            "name": name,
            "description": description,
            "type": agent_type,
            "source": source,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "deletable": deletable,
        }
        self.agents[agent_id] = agent
        self._save()
        logger.info("Created agent: id=%s, name=%s, type=%s", agent_id, name, agent_type)
        return agent

    def get(self, agent_id: str) -> Optional[dict]:
        logger.debug("get: agent_id=%s, found=%s", agent_id, agent_id in self.agents)
        return self.agents.get(agent_id)

    def get_by_name(self, name: str) -> Optional[dict]:
        """Look up agent by name (case-insensitive)."""
        name_lower = name.lower()
        for agent in self.agents.values():
            if agent["name"].lower() == name_lower:
                return agent
        return None

    def list_all(self) -> list:
        return list(self.agents.values())

    def delete(self, agent_id: str) -> bool:
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        if not agent.get("deletable", True):
            logger.warning("Attempted delete of non-deletable agent: id=%s, name=%s", agent_id, agent["name"])
            raise ValueError(f"Cannot delete built-in agent '{agent['name']}'")
        del self.agents[agent_id]
        self._save()
        logger.info("Deleted agent: id=%s, name=%s", agent_id, agent["name"])
        return True

    def update(self, agent_id: str, **kwargs) -> Optional[dict]:
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        updated_fields = [k for k, v in kwargs.items() if v is not None and k in agent]
        for key, value in kwargs.items():
            if value is not None and key in agent:
                agent[key] = value
        self._save()
        logger.info("Updated agent: id=%s, fields=%s", agent_id, updated_fields)
        return agent


store = AgentStore()
