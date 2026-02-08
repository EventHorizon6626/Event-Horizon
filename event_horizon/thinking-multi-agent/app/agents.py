"""Agent registry — stores and manages agent configurations."""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

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

    def _save(self):
        """Persist agents to disk."""
        os.makedirs(os.path.dirname(AGENTS_FILE), exist_ok=True)
        with open(AGENTS_FILE, "w") as f:
            json.dump(self.agents, f, indent=2)

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
        return agent

    def get(self, agent_id: str) -> Optional[dict]:
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
            raise ValueError(f"Cannot delete built-in agent '{agent['name']}'")
        del self.agents[agent_id]
        self._save()
        return True

    def update(self, agent_id: str, **kwargs) -> Optional[dict]:
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        for key, value in kwargs.items():
            if value is not None and key in agent:
                agent[key] = value
        self._save()
        return agent


store = AgentStore()
