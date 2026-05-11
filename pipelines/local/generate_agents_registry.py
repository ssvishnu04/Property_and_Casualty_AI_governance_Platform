"""
generate_agents_registry.py

Purpose:
Creates AI agent registry data.

This represents SEMI-STRUCTURED AI governance data.

Output:
data/semi_structured/agents.json
"""

from pathlib import Path
import json
from datetime import datetime, timedelta
import random


OUTPUT_DIR = Path("data/semi_structured")
OUTPUT_FILE = OUTPUT_DIR / "agents.json"


AGENTS = [
    {
        "agent_name": "Claims Summary Agent",
        "business_unit": "Claims",
        "risk_tier": "Medium",
        "approved_tools": [
            "claims_lookup",
            "document_search",
        ],
    },
    {
        "agent_name": "FNOL Intake Agent",
        "business_unit": "Claims",
        "risk_tier": "Medium",
        "approved_tools": [
            "fnol_event_lookup",
            "claims_lookup",
        ],
    },
    {
        "agent_name": "Policy Coverage Agent",
        "business_unit": "Policy Services",
        "risk_tier": "High",
        "approved_tools": [
            "policy_document_search",
            "coverage_lookup",
        ],
    },
    {
        "agent_name": "Underwriting Copilot",
        "business_unit": "Underwriting",
        "risk_tier": "High",
        "approved_tools": [
            "underwriting_guideline_search",
            "submission_lookup",
        ],
    },
    {
        "agent_name": "CAT Event Intelligence Agent",
        "business_unit": "CAT Analytics",
        "risk_tier": "High",
        "approved_tools": [
            "cat_event_lookup",
            "exposure_analysis_tool",
        ],
    },
    {
        "agent_name": "Reinsurance Treaty Agent",
        "business_unit": "Reinsurance",
        "risk_tier": "High",
        "approved_tools": [
            "treaty_search",
            "document_search",
        ],
    },
    {
        "agent_name": "Governance Oversight Agent",
        "business_unit": "AI Governance",
        "risk_tier": "Critical",
        "approved_tools": [
            "audit_log_reader",
            "risk_dashboard_lookup",
        ],
    },
    {
        "agent_name": "Document Extraction Agent",
        "business_unit": "Operations",
        "risk_tier": "Medium",
        "approved_tools": [
            "document_parser",
            "ocr_tool",
        ],
    },
    {
        "agent_name": "Broker Submission Agent",
        "business_unit": "Underwriting",
        "risk_tier": "Medium",
        "approved_tools": [
            "submission_lookup",
            "broker_document_search",
        ],
    },
]


SOURCE_SYSTEMS = [
    "ai_registry_platform",
    "governance_admin_portal",
]


def generate_agent_registry():
    """
    Generates AI agent registry records.
    """

    records = []

    for i, agent in enumerate(AGENTS, start=1):

        created_timestamp = (
            datetime.now()
            - timedelta(days=random.randint(30, 365))
        )

        reviewed_timestamp = (
            created_timestamp
            + timedelta(days=random.randint(10, 90))
        )

        record = {
            "agent_id": f"AGT-{i:04d}",
            "agent_name": agent["agent_name"],
            "business_unit": agent["business_unit"],
            "owner_team": f"{agent['business_unit']} AI Team",
            "risk_tier": agent["risk_tier"],
            "approved_tools": agent["approved_tools"],
            "allowed_data_types": [
                "structured",
                "semi_structured",
                "unstructured",
            ],
            "status": random.choice(
                ["Active", "Pilot", "Active"]
            ),
            "model_name": random.choice(
                [
                    "llama-3.1-8b",
                    "gpt-4",
                    "mixtral-8x7b",
                ]
            ),
            "data_sensitivity": random.choice(
                [
                    "internal",
                    "confidential",
                    "restricted",
                ]
            ),
            "source_system": random.choice(
                SOURCE_SYSTEMS
            ),
            "created_timestamp": (
                created_timestamp.isoformat()
            ),
            "last_reviewed_timestamp": (
                reviewed_timestamp.isoformat()
            ),
            "created_by": "ai_platform_admin",
        }

        records.append(record)

    return records


def save_agent_registry(records):
    """
    Saves agent registry into JSON.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(records, f, indent=4)

    print(
        f"Agent registry generated successfully: {OUTPUT_FILE}"
    )

    print(f"Total agents: {len(records)}")


if __name__ == "__main__":

    agent_registry = generate_agent_registry()

    save_agent_registry(agent_registry)