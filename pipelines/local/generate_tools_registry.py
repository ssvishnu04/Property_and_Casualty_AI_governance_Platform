"""
generate_tools_registry.py

Purpose:
Creates enterprise AI tool registry data.

This represents SEMI-STRUCTURED governance data.

Output:
data/semi_structured/tools.json
"""

from pathlib import Path
import json
from datetime import datetime, timedelta
import random


OUTPUT_DIR = Path("data/semi_structured")
OUTPUT_FILE = OUTPUT_DIR / "tools.json"


TOOLS = [
    {
        "tool_name": "claims_lookup",
        "tool_type": "database_query",
        "allowed_departments": ["Claims"],
        "sensitivity_level": "confidential",
        "pii_access": True,
    },
    {
        "tool_name": "policy_document_search",
        "tool_type": "document_search",
        "allowed_departments": [
            "Policy Services",
            "Underwriting",
        ],
        "sensitivity_level": "restricted",
        "pii_access": True,
    },
    {
        "tool_name": "coverage_lookup",
        "tool_type": "coverage_engine",
        "allowed_departments": [
            "Claims",
            "Policy Services",
        ],
        "sensitivity_level": "restricted",
        "pii_access": True,
    },
    {
        "tool_name": "submission_lookup",
        "tool_type": "underwriting_query",
        "allowed_departments": [
            "Underwriting"
        ],
        "sensitivity_level": "confidential",
        "pii_access": False,
    },
    {
        "tool_name": "underwriting_guideline_search",
        "tool_type": "document_search",
        "allowed_departments": [
            "Underwriting"
        ],
        "sensitivity_level": "internal",
        "pii_access": False,
    },
    {
        "tool_name": "cat_event_lookup",
        "tool_type": "event_query",
        "allowed_departments": [
            "CAT Analytics",
            "Reinsurance",
        ],
        "sensitivity_level": "internal",
        "pii_access": False,
    },
    {
        "tool_name": "exposure_analysis_tool",
        "tool_type": "analytics_engine",
        "allowed_departments": [
            "CAT Analytics",
            "Reinsurance",
        ],
        "sensitivity_level": "restricted",
        "pii_access": False,
    },
    {
        "tool_name": "treaty_search",
        "tool_type": "document_search",
        "allowed_departments": [
            "Reinsurance"
        ],
        "sensitivity_level": "restricted",
        "pii_access": False,
    },
    {
        "tool_name": "audit_log_reader",
        "tool_type": "audit_query",
        "allowed_departments": [
            "Audit",
            "Security",
            "AI Governance",
        ],
        "sensitivity_level": "critical",
        "pii_access": True,
    },
    {
        "tool_name": "risk_dashboard_lookup",
        "tool_type": "dashboard_query",
        "allowed_departments": [
            "AI Governance",
            "Security",
        ],
        "sensitivity_level": "confidential",
        "pii_access": False,
    },
    {
        "tool_name": "document_parser",
        "tool_type": "document_processing",
        "allowed_departments": [
            "Operations",
            "Claims",
        ],
        "sensitivity_level": "internal",
        "pii_access": True,
    },
    {
        "tool_name": "ocr_tool",
        "tool_type": "ocr_engine",
        "allowed_departments": [
            "Operations"
        ],
        "sensitivity_level": "internal",
        "pii_access": True,
    },
]


SOURCE_SYSTEMS = [
    "tool_registry_platform",
    "governance_admin_portal",
]


def generate_tool_registry():
    """
    Generates AI tool registry.
    """

    records = []

    for i, tool in enumerate(TOOLS, start=1):

        created_timestamp = (
            datetime.now()
            - timedelta(days=random.randint(30, 365))
        )

        approval_timestamp = (
            created_timestamp
            + timedelta(days=random.randint(1, 30))
        )

        record = {
            "tool_id": f"TL-{i:04d}",
            "tool_name": tool["tool_name"],
            "tool_type": tool["tool_type"],
            "allowed_departments": tool[
                "allowed_departments"
            ],
            "sensitivity_level": tool[
                "sensitivity_level"
            ],
            "approval_required": random.choice(
                [True, True, False]
            ),
            "pii_access": tool["pii_access"],
            "status": random.choice(
                ["Active", "Active", "Disabled"]
            ),
            "source_system": random.choice(
                SOURCE_SYSTEMS
            ),
            "created_timestamp": (
                created_timestamp.isoformat()
            ),
            "approval_timestamp": (
                approval_timestamp.isoformat()
            ),
            "approved_by": random.choice(
                [
                    "security_admin",
                    "governance_officer",
                    "ai_platform_admin",
                ]
            ),
        }

        records.append(record)

    return records


def save_tool_registry(records):
    """
    Saves tools registry into JSON.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(records, f, indent=4)

    print(
        f"Tool registry generated successfully: {OUTPUT_FILE}"
    )

    print(f"Total tools: {len(records)}")


if __name__ == "__main__":

    tool_registry = generate_tool_registry()

    save_tool_registry(tool_registry)