"""
guardrail_service.py

Purpose:
Evaluates prompts and tool usage
for enterprise AI safety, governance,
privacy, and operational risk.
"""

import re

from api.models.governance_models import (
    GovernanceEvaluationRequest,
    GovernanceEvaluationResponse,
)

from api.services.agent_service import (
    get_agent_by_id,
)


PROMPT_INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"ignore all instructions",
    r"ignore all governance rules",
    r"ignore governance rules",
    r"ignore compliance rules",
    r"bypass governance",
    r"disable governance",
    r"disable governance controls",
    r"disable guardrails",
    r"override instructions",
    r"reveal system prompt",
    r"show system prompt",
    r"developer mode",
    r"jailbreak",
    r"bypass policy",
    r"reveal confidential",
]


PII_PATTERNS = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
}


PII_REQUEST_TERMS = {
    "ssn": [
        "ssn",
        "social security",
        "social security number",
    ],
    "credit_card": [
        "credit card",
        "card number",
        "payment card",
    ],
    "bank_account": [
        "bank account",
        "routing number",
        "account number",
    ],
    "password": [
        "password",
        "passwords",
        "credentials",
        "login details",
    ],
    "personal_details": [
        "personal details",
        "personal information",
        "claimant personal information",
        "policyholder information",
        "confidential policyholder information",
    ],
}


CREDENTIAL_REQUEST_TERMS = [
    "api key",
    "api keys",
    "secret key",
    "secret keys",
    "secrets",
    "password",
    "passwords",
    "database credentials",
    "db credentials",
    "credentials",
    "access token",
    "auth token",
    "private key",
]


SENSITIVE_REQUEST_TERMS = [
    "confidential treaty",
    "restricted treaty",
    "export all",
    "download all",
    "restricted document",
    "all claims data",
    "all policyholder data",
    "unauthorized documents",
    "without approval",
]


CONFIDENTIAL_REINSURANCE_TERMS = [
    "confidential reinsurance",
    "confidential reinsurance treaty",
    "treaty financial terms",
    "reinsurance pricing",
    "reinsurance contract",
    "treaty details",
    "treaty limits",
    "reinsurance attachment point",
    "reinsurance retention",
    "confidential treaty financial terms",
]


INTERNAL_MODEL_EXPOSURE_TERMS = [
    "underwriting pricing models",
    "internal underwriting models",
    "internal underwriting pricing models",
    "pricing algorithm",
    "risk scoring model",
    "underwriting formula",
    "internal pricing logic",
    "proprietary underwriting",
    "internal underwriting pricing",
]


REVIEW_REQUIRED_KEYWORDS = [
    "reserve amount",
    "reserve adequacy",
    "litigation exposure",
    "large loss",
    "cat loss",
    "catastrophe exposure",
    "maximum recovery",
    "maximum cat recovery",
    "financial exposure",
    "pricing adequacy",
    "underwriting projection",
    "bankruptcy risk",
    "severity projection",
    "claims escalation",
    "reinsurance recovery",
    "exhaustion scenario",
    "treaty exhaustion",
    "loss forecast",
    "claim severity forecast",
    "cat recovery exposure",
]


def add_rule_once(
    triggered_rules: list,
    rule_name: str,
) -> None:
    """
    Adds governance rule only once.
    """

    if rule_name not in triggered_rules:
        triggered_rules.append(rule_name)


def evaluate_governance_request(
    request: GovernanceEvaluationRequest,
) -> GovernanceEvaluationResponse:
    """
    Evaluates enterprise AI governance risk
    before agent execution.
    """

    triggered_rules = []
    risk_score = 0.0
    prompt_lower = request.prompt.lower()

    agent = get_agent_by_id(
        request.agent_id
    )

    # ---------------------------------------------------------
    # Agent validation
    # ---------------------------------------------------------

    if agent is None:
        add_rule_once(
            triggered_rules,
            "unregistered_agent",
        )
        risk_score += 0.60

    # ---------------------------------------------------------
    # Tool authorization validation
    # ---------------------------------------------------------

    if agent is not None:

        approved_tools = agent.get(
            "approved_tools",
            []
        )

        if request.tool_name not in approved_tools:

            add_rule_once(
                triggered_rules,
                "unauthorized_tool_access",
            )

            risk_score += 0.45

    # ---------------------------------------------------------
    # Prompt injection detection
    # ---------------------------------------------------------

    for pattern in PROMPT_INJECTION_PATTERNS:

        if re.search(
            pattern,
            prompt_lower,
        ):

            add_rule_once(
                triggered_rules,
                "prompt_injection",
            )

            risk_score = max(
                risk_score,
                0.90,
            )

            break

    # ---------------------------------------------------------
    # Direct PII pattern detection
    # ---------------------------------------------------------

    for pii_type, pattern in PII_PATTERNS.items():

        if re.search(
            pattern,
            request.prompt,
        ):

            add_rule_once(
                triggered_rules,
                f"pii_detected_{pii_type}",
            )

            risk_score = max(
                risk_score,
                0.80,
            )

    # ---------------------------------------------------------
    # PII request intent detection
    # ---------------------------------------------------------

    for pii_type, terms in PII_REQUEST_TERMS.items():

        for term in terms:

            if term in prompt_lower:

                add_rule_once(
                    triggered_rules,
                    f"pii_request_{pii_type}",
                )

                risk_score = max(
                    risk_score,
                    0.85,
                )

                break

    # ---------------------------------------------------------
    # Credential extraction detection
    # ---------------------------------------------------------

    credential_triggered = any(
        term in prompt_lower
        for term in CREDENTIAL_REQUEST_TERMS
    )

    if credential_triggered:

        add_rule_once(
            triggered_rules,
            "credential_extraction_request",
        )

        risk_score = max(
            risk_score,
            0.95,
        )

    # ---------------------------------------------------------
    # Sensitive enterprise data detection
    # ---------------------------------------------------------

    for term in SENSITIVE_REQUEST_TERMS:

        if term in prompt_lower:

            add_rule_once(
                triggered_rules,
                "sensitive_data_request",
            )

            risk_score = max(
                risk_score,
                0.85,
            )

            break

    # ---------------------------------------------------------
    # Confidential reinsurance information detection
    # ---------------------------------------------------------

    confidential_reinsurance_triggered = any(
        term in prompt_lower
        for term in CONFIDENTIAL_REINSURANCE_TERMS
    )

    if confidential_reinsurance_triggered:

        add_rule_once(
            triggered_rules,
            "confidential_reinsurance_request",
        )

        risk_score = max(
            risk_score,
            0.90,
        )

    # ---------------------------------------------------------
    # Internal underwriting model exposure detection
    # ---------------------------------------------------------

    internal_model_triggered = any(
        term in prompt_lower
        for term in INTERNAL_MODEL_EXPOSURE_TERMS
    )

    if internal_model_triggered:

        add_rule_once(
            triggered_rules,
            "internal_model_exposure",
        )

        risk_score = max(
            risk_score,
            0.85,
        )

    # ---------------------------------------------------------
    # Governance review requests
    # ---------------------------------------------------------

    review_triggered = any(
        keyword in prompt_lower
        for keyword in REVIEW_REQUIRED_KEYWORDS
    )

    if (
        review_triggered
        and risk_score < 0.70
    ):

        add_rule_once(
            triggered_rules,
            "financial_or_risk_sensitive_review",
        )

        risk_score = max(
            risk_score,
            0.55,
        )

    # ---------------------------------------------------------
    # Final normalization
    # ---------------------------------------------------------

    risk_score = min(
        round(risk_score, 2),
        1.0,
    )

    # ---------------------------------------------------------
    # Final decision
    # ---------------------------------------------------------

    if risk_score >= 0.70:

        decision = "Blocked"
        risk_level = "High"

        explanation = (
            "Request blocked because it violates "
            "enterprise AI governance, security, "
            "privacy, or safety controls."
        )

    elif risk_score >= 0.40:

        decision = "Allowed with Review"
        risk_level = "Medium"

        explanation = (
            "Request allowed but flagged for "
            "governance review due to moderate "
            "financial, operational, privacy, "
            "or model-risk sensitivity."
        )

    else:

        decision = "Allowed"
        risk_level = "Low"

        explanation = (
            "Request passed current "
            "enterprise AI governance checks."
        )

    return GovernanceEvaluationResponse(
        user_id=request.user_id,
        agent_id=request.agent_id,
        tool_name=request.tool_name,
        prompt=request.prompt,
        decision=decision,
        risk_score=risk_score,
        risk_level=risk_level,
        triggered_rules=triggered_rules,
        explanation=explanation,
    )