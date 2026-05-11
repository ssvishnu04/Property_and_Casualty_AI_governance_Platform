"""
agent_service.py

Purpose:
Handles AI agent registry operations.
"""

from pathlib import Path
import json


AGENTS_FILE = Path(
    "data/semi_structured/agents.json"
)


def load_agents():
    """
    Loads AI agent registry data.
    """

    with open(AGENTS_FILE, "r") as f:

        agents = json.load(f)

    return agents


def get_all_agents():
    """
    Returns all registered AI agents.
    """

    return load_agents()


def get_agent_by_id(agent_id: str):
    """
    Returns a single agent by ID.
    """

    agents = load_agents()

    for agent in agents:

        if agent["agent_id"] == agent_id:
            return agent

    return None