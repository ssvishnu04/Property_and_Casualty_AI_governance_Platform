"""
agent_routes.py

Purpose:
API routes for AI agent registry.
"""

from fastapi import APIRouter

from api.services.agent_service import (
    get_all_agents,
    get_agent_by_id,
)


router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


@router.get("/")
def fetch_all_agents():
    """
    Returns all AI agents.
    """

    return get_all_agents()


@router.get("/{agent_id}")
def fetch_agent_by_id(agent_id: str):
    """
    Returns one AI agent by ID.
    """

    return get_agent_by_id(agent_id)