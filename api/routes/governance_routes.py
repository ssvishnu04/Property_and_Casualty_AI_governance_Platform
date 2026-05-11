"""
governance_routes.py

Purpose:
API route for governed AI request evaluation.
"""

from datetime import datetime
from fastapi import APIRouter

from api.models.governance_models import (
    GovernanceEvaluationRequest,
    GovernanceEvaluationResponse,
)
from api.services.guardrail_service import evaluate_governance_request
from api.services.agent_response_service import generate_agent_response
from api.services.event_service import load_events, save_event
from api.services.agent_service import get_agent_by_id


router = APIRouter(
    prefix="/governance",
    tags=["Governance"],
)


@router.post(
    "/evaluate",
    response_model=GovernanceEvaluationResponse,
)
def evaluate_request(
    request: GovernanceEvaluationRequest,
):
    """
    Evaluates request, generates governed agent response,
    and saves runtime audit event with RAG metadata.
    """

    result = evaluate_governance_request(request)

    agent = get_agent_by_id(request.agent_id)

    if agent is None:
        agent_name = request.agent_id
    else:
        agent_name = agent.get(
            "agent_name",
            request.agent_id,
        )

    rag_metadata = {}

    if result.decision == "Blocked":
        agent_response_text = (
            "No AI response generated because the request was blocked "
            "by enterprise governance controls."
        )

    else:
        agent_result = generate_agent_response(
            agent_id=request.agent_id,
            prompt=request.prompt,
        )

        agent_response_text = agent_result.get(
            "response",
            "No agent response generated.",
        )

        rag_metadata = agent_result.get(
            "rag_metadata",
            {},
        )

    result.agent_response = agent_response_text

    existing_events = load_events()
    next_event_number = len(existing_events) + 1
    now = datetime.now().isoformat()

    new_event = {
        "request_id": f"REQ-{next_event_number:07d}",
        "user_id": result.user_id,
        "agent_id": result.agent_id,
        "agent_name": agent_name,
        "tool_used": result.tool_name,
        "prompt": result.prompt,
        "decision": result.decision,
        "risk_score": result.risk_score,
        "risk_level": result.risk_level,
        "hallucination_risk_score": 0.10
        if result.decision == "Allowed"
        else 0.75,
        "latency_ms": 500,
        "tokens_used": 250,
        "model_name": "enterprise-governance-agent",
        "triggered_rules": result.triggered_rules,
        "agent_response": agent_response_text,
        "rag_domain": rag_metadata.get("rag_domain"),
        "retrieved_chunk_count": rag_metadata.get(
            "retrieved_chunk_count",
            0,
        ),
        "retrieval_latency_seconds": rag_metadata.get(
            "retrieval_latency_seconds",
            0,
        ),
        "retrieved_sources": rag_metadata.get(
            "retrieved_sources",
            [],
        ),
        "event_timestamp": now,
        "response_timestamp": now,
        "source_system": "enterprise_ai_gateway",
    }

    save_event(new_event)

    return result