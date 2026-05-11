"""
generate_claims_data.py

Purpose:
Creates synthetic P&C insurance claims data for the local Streamlit demo.

This represents STRUCTURED data.

Output:
data/structured/claims.csv
"""

from pathlib import Path
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker


fake = Faker()

OUTPUT_DIR = Path("data/structured")
OUTPUT_FILE = OUTPUT_DIR / "claims.csv"


LOSS_TYPES = [
    "Water Damage",
    "Fire",
    "Windstorm",
    "Hail",
    "Theft",
    "General Liability",
    "Auto Liability",
    "Workers Compensation",
    "Property Damage",
]

CLAIM_STATUSES = [
    "Open",
    "Closed",
    "In Review",
    "Pending Documents",
    "Litigation",
    "Denied",
]

LINES_OF_BUSINESS = [
    "Commercial Property",
    "General Liability",
    "Commercial Auto",
    "Workers Compensation",
    "Umbrella",
]


SOURCE_SYSTEMS = [
    "claims_core_system",
    "fnol_portal",
    "adjuster_workbench",
]


def random_date_within_last_days(days: int = 730) -> datetime:
    """
    Creates a random datetime within the last N days.

    Why this matters:
    Claims dashboards need dates to show trends such as:
    - claims opened this month
    - claims by loss year
    - recent claim activity
    """
    today = datetime.now()
    random_days = random.randint(0, days)
    return today - timedelta(days=random_days)


def generate_claims_data(num_records: int = 500) -> pd.DataFrame:
    """
    Generates synthetic claims records.

    Each record represents one insurance claim.
    """

    records = []

    for i in range(1, num_records + 1):
        claim_id = f"CLM-{i:06d}"
        policy_id = f"POL-{random.randint(1, 300):06d}"

        loss_date = random_date_within_last_days(900)
        created_timestamp = loss_date + timedelta(days=random.randint(0, 10))
        updated_timestamp = created_timestamp + timedelta(days=random.randint(0, 120))

        reserve_amount = round(random.uniform(5_000, 500_000), 2)
        paid_amount = round(random.uniform(0, reserve_amount), 2)

        litigation_flag = random.choice([True, False, False, False])

        loss_type = random.choice(LOSS_TYPES)
        claim_status = random.choice(CLAIM_STATUSES)

        if litigation_flag:
            claim_status = "Litigation"

        record = {
            "claim_id": claim_id,
            "policy_id": policy_id,
            "insured_name": fake.company(),
            "line_of_business": random.choice(LINES_OF_BUSINESS),
            "loss_date": loss_date.date().isoformat(),
            "loss_type": loss_type,
            "claim_status": claim_status,
            "reserve_amount": reserve_amount,
            "paid_amount": paid_amount,
            "adjuster_notes": generate_adjuster_note(loss_type, claim_status),
            "litigation_flag": litigation_flag,
            "pii_flag": random.choice([True, False, False]),
            "data_sensitivity": random.choice(["internal", "confidential", "restricted"]),
            "source_system": random.choice(SOURCE_SYSTEMS),
            "created_timestamp": created_timestamp.isoformat(),
            "updated_timestamp": updated_timestamp.isoformat(),
            "created_by": random.choice(
                ["claims_adjuster_001", "claims_adjuster_002", "claims_manager_001"]
            ),
            "updated_by": random.choice(
                ["claims_adjuster_001", "claims_adjuster_002", "claims_manager_001"]
            ),
        }

        records.append(record)

    return pd.DataFrame(records)


def generate_adjuster_note(loss_type: str, claim_status: str) -> str:
    """
    Creates a short synthetic adjuster note.

    This is still stored in a structured CSV, but the note itself is text.
    Later, Claims Summary Agent can summarize this field.
    """

    note_templates = [
        f"Initial review completed for {loss_type}. Claim status is currently {claim_status}.",
        f"Additional documentation requested from insured regarding {loss_type}.",
        f"Coverage review in progress. Adjuster evaluating damages related to {loss_type}.",
        f"Claim file updated after inspection. Current status: {claim_status}.",
        f"Pending supervisor review due to complexity of {loss_type} claim.",
    ]

    return random.choice(note_templates)


def save_claims_data(df: pd.DataFrame) -> None:
    """
    Saves generated claims data into data/structured/claims.csv.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Claims data generated successfully: {OUTPUT_FILE}")
    print(f"Total records: {len(df)}")


if __name__ == "__main__":
    claims_df = generate_claims_data(num_records=500)
    save_claims_data(claims_df)