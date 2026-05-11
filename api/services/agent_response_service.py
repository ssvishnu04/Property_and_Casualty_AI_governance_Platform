"""
agent_response_service.py

Purpose:
Centralized governed agent orchestration service.

Uses agent registry lookup instead of hardcoded agent ID ordering.
This prevents incorrect routing when agent IDs change.
"""

from api.services.agent_service import get_agent_by_id

from agents.policy_agent import run_policy_agent
from agents.claims_agent import run_claims_agent
from agents.underwriting_agent import run_underwriting_agent
from agents.reinsurance_agent import run_reinsurance_agent
from agents.cat_agent import run_cat_agent
from agents.governance_agent import run_governance_agent


def normalize_agent_name(agent_name: str) -> str:
    return agent_name.lower().strip()


def resolve_agent_function(agent_name: str):
    """
    Routes by agent name instead of hardcoded AGT IDs.
    """

    name = normalize_agent_name(agent_name)

    if "policy" in name or "coverage" in name:
        return run_policy_agent

    if "claim" in name:
        return run_claims_agent

    if "underwriting" in name:
        return run_underwriting_agent

    if "reinsurance" in name or "treaty" in name:
        return run_reinsurance_agent

    if "cat" in name or "catastrophe" in name:
        return run_cat_agent

    if "governance" in name or "oversight" in name:
        return run_governance_agent

    return None


def generate_agent_response(
    agent_id: str,
    prompt: str,
) -> dict:
    """
    Executes governed AI agent workflow.

    Returns:
    {
        "response": str,
        "rag_metadata": dict
    }
    """

    agent = get_agent_by_id(agent_id)

    if agent is None:
        return {
            "response": f"Unknown agent ID: {agent_id}",
            "rag_metadata": {},
        }

    agent_name = agent.get("agent_name", "")

    agent_function = resolve_agent_function(agent_name)

    if agent_function is None:
        return {
            "response": (
                f"No agent function is configured for agent: {agent_name}"
            ),
            "rag_metadata": {},
        }

    result = agent_function(prompt)

    if isinstance(result, str):
        return {
            "response": result,
            "rag_metadata": {},
        }

    if isinstance(result, dict):
        return {
            "response": result.get(
                "response",
                "No response generated.",
            ),
            "rag_metadata": result.get(
                "rag_metadata",
                {},
            ),
        }

    return {
        "response": "Unexpected agent response format.",
        "rag_metadata": {},
    }