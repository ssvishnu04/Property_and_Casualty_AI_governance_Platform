"""
governance_models.py

Purpose:
Defines request and response schemas for governance evaluation.
"""

from pydantic import BaseModel
from typing import List, Optional


class GovernanceEvaluationRequest(BaseModel):
    user_id: str
    agent_id: str
    tool_name: str
    prompt: str


class GovernanceEvaluationResponse(BaseModel):
    user_id: str
    agent_id: str
    tool_name: str
    prompt: str
    decision: str
    risk_score: float
    risk_level: str
    triggered_rules: List[str]
    explanation: str
    agent_response: Optional[str] = None