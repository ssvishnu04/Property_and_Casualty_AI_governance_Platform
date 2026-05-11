"""
generate_unstructured_docs.py

Purpose:
Creates synthetic unstructured insurance documents.

This represents UNSTRUCTURED enterprise insurance data.

Outputs:
data/unstructured/*.txt
data/unstructured/document_metadata.json
"""

from pathlib import Path
import json
from datetime import datetime
import random


OUTPUT_DIR = Path("data/unstructured")

METADATA_FILE = OUTPUT_DIR / "document_metadata.json"


DOCUMENTS = [
    {
        "document_id": "DOC-0001",
        "document_name": "commercial_property_policy_wording.txt",
        "document_type": "Policy Wording",
        "business_unit": "Policy Services",
        "data_sensitivity": "restricted",
        "source_system": "policy_document_repository",
        "content": """
COMMERCIAL PROPERTY POLICY WORDING

Coverage applies to direct physical loss or damage to covered property
caused by a covered peril during the policy period.

Covered property includes:
- Buildings
- Business personal property
- Equipment
- Inventory

Covered perils may include:
- Fire
- Windstorm
- Hail
- Theft
- Water damage

Exclusions:
- War
- Nuclear hazard
- Intentional acts
- Flood unless endorsed
- Earthquake unless endorsed

Deductibles and policy limits apply to all covered losses.
Claims must be reported within a reasonable timeframe following discovery.
        """,
    },

    {
        "document_id": "DOC-0002",
        "document_name": "claims_handling_manual.txt",
        "document_type": "Claims Manual",
        "business_unit": "Claims",
        "data_sensitivity": "confidential",
        "source_system": "claims_document_repository",
        "content": """
CLAIMS HANDLING MANUAL

All claim files must be reviewed for:
- Policy verification
- Coverage applicability
- Fraud indicators
- Reserve adequacy
- Documentation completeness

Adjusters must:
- Document all insured communications
- Update reserves promptly
- Escalate litigation claims
- Maintain regulatory compliance

Claims involving bodily injury or catastrophic loss
require management review.

Sensitive customer information must not be shared
outside authorized systems.
        """,
    },

    {
        "document_id": "DOC-0003",
        "document_name": "underwriting_guidelines.txt",
        "document_type": "Underwriting Guidelines",
        "business_unit": "Underwriting",
        "data_sensitivity": "restricted",
        "source_system": "underwriting_knowledge_base",
        "content": """
UNDERWRITING GUIDELINES

Underwriters should evaluate:
- Historical loss activity
- Catastrophe exposure
- Construction type
- Occupancy risk
- Financial stability
- Geographic concentration

High-risk industries include:
- Manufacturing
- Energy
- Chemical processing
- Heavy transportation

Risks with multiple prior losses
must undergo management review.

CAT exposed risks may require:
- Increased deductibles
- Coverage restrictions
- Reinsurance review
        """,
    },

    {
        "document_id": "DOC-0004",
        "document_name": "reinsurance_treaty_sample.txt",
        "document_type": "Reinsurance Treaty",
        "business_unit": "Reinsurance",
        "data_sensitivity": "restricted",
        "source_system": "treaty_management_platform",
        "content": """
REINSURANCE TREATY SAMPLE

This Catastrophe Excess of Loss treaty provides
protection for catastrophe losses exceeding
the attachment point.

Attachment Point:
$10,000,000

Treaty Limit:
$50,000,000

Covered Territories:
- Gulf Coast
- Southeast United States

Exclusions:
- War
- Nuclear incidents
- Cyber terrorism

The reinsurer shall indemnify the cedent
for covered catastrophe losses exceeding
the attachment point up to the treaty limit.
        """,
    },

    {
        "document_id": "DOC-0005",
        "document_name": "cat_event_response_guide.txt",
        "document_type": "CAT Response Guide",
        "business_unit": "CAT Analytics",
        "data_sensitivity": "internal",
        "source_system": "cat_response_repository",
        "content": """
CATASTROPHE RESPONSE GUIDE

Following a catastrophe event:

1. Activate CAT response procedures
2. Monitor claim surge activity
3. Escalate severe losses
4. Notify reinsurance partners
5. Track regional exposure accumulation

Priority CAT events include:
- Hurricanes
- Wildfires
- Earthquakes
- Tornado outbreaks

CAT analytics teams should continuously monitor:
- Loss trends
- Geographic concentration
- Reinsurance exhaustion risk
- Operational capacity
        """,
    },
]


def create_document_metadata(document: dict) -> dict:
    """
    Creates metadata record for document governance.
    """

    return {
        "document_id": document["document_id"],
        "document_name": document["document_name"],
        "document_type": document["document_type"],
        "business_unit": document["business_unit"],
        "data_sensitivity": document["data_sensitivity"],
        "source_system": document["source_system"],
        "created_timestamp": datetime.now().isoformat(),
        "last_reviewed_timestamp": datetime.now().isoformat(),
        "approved_by": random.choice(
            [
                "document_admin",
                "governance_officer",
                "business_owner",
            ]
        ),
    }


def save_documents():
    """
    Saves all unstructured documents and metadata.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metadata_records = []

    for document in DOCUMENTS:

        file_path = OUTPUT_DIR / document["document_name"]

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(document["content"].strip())

        metadata_records.append(
            create_document_metadata(document)
        )

    with open(METADATA_FILE, "w") as f:
        json.dump(metadata_records, f, indent=4)

    print(
        "Unstructured documents generated successfully."
    )

    print(f"Total documents: {len(DOCUMENTS)}")


if __name__ == "__main__":

    save_documents()