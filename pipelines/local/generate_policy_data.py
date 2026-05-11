"""
generate_policy_data.py

Purpose:
Creates synthetic insurance policy data.

This represents STRUCTURED data.

Output:
data/structured/policies.csv
"""

from pathlib import Path
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker


fake = Faker()

OUTPUT_DIR = Path("data/structured")
OUTPUT_FILE = OUTPUT_DIR / "policies.csv"


LINES_OF_BUSINESS = [
    "Commercial Property",
    "General Liability",
    "Commercial Auto",
    "Workers Compensation",
    "Umbrella",
    "Cyber",
]


POLICY_STATUSES = [
    "Active",
    "Expired",
    "Cancelled",
    "Pending Renewal",
]


ENDORSEMENTS = [
    "Flood Coverage",
    "Cyber Extension",
    "Equipment Breakdown",
    "Business Interruption",
    "Windstorm Coverage",
    "Earthquake Endorsement",
]


EXCLUSIONS = [
    "Flood Exclusion",
    "War Exclusion",
    "Cyber Exclusion",
    "Mold Exclusion",
    "Terrorism Exclusion",
]


SOURCE_SYSTEMS = [
    "policy_admin_system",
    "underwriting_platform",
    "broker_submission_portal",
]


def random_date_within_last_days(days: int = 1000) -> datetime:
    """
    Creates a random historical date.

    Policies require effective and expiration dates
    for policy lifecycle tracking.
    """

    today = datetime.now()
    random_days = random.randint(0, days)

    return today - timedelta(days=random_days)


def generate_policy_data(num_records: int = 300) -> pd.DataFrame:
    """
    Generates synthetic policy records.
    """

    records = []

    for i in range(1, num_records + 1):

        policy_id = f"POL-{i:06d}"

        effective_date = random_date_within_last_days(1200)

        expiration_date = effective_date + timedelta(days=365)

        created_timestamp = effective_date - timedelta(days=random.randint(1, 30))

        updated_timestamp = expiration_date - timedelta(days=random.randint(1, 60))

        coverage_limit = random.choice(
            [100000, 250000, 500000, 1000000, 5000000]
        )

        deductible = random.choice(
            [1000, 2500, 5000, 10000, 25000]
        )

        selected_endorsements = random.sample(
            ENDORSEMENTS,
            k=random.randint(1, 3)
        )

        selected_exclusions = random.sample(
            EXCLUSIONS,
            k=random.randint(1, 2)
        )

        record = {
            "policy_id": policy_id,
            "insured_name": fake.company(),
            "line_of_business": random.choice(LINES_OF_BUSINESS),
            "policy_status": random.choice(POLICY_STATUSES),
            "effective_date": effective_date.date().isoformat(),
            "expiration_date": expiration_date.date().isoformat(),
            "coverage_limit": coverage_limit,
            "deductible": deductible,
            "endorsements": ", ".join(selected_endorsements),
            "exclusions": ", ".join(selected_exclusions),
            "underwriter_name": fake.name(),
            "broker_name": fake.company(),
            "risk_tier": random.choice(
                ["Low", "Medium", "High"]
            ),
            "data_sensitivity": random.choice(
                ["internal", "confidential", "restricted"]
            ),
            "source_system": random.choice(SOURCE_SYSTEMS),
            "created_timestamp": created_timestamp.isoformat(),
            "updated_timestamp": updated_timestamp.isoformat(),
            "created_by": random.choice(
                ["underwriter_001", "underwriter_002", "uw_manager_001"]
            ),
            "updated_by": random.choice(
                ["underwriter_001", "underwriter_002", "uw_manager_001"]
            ),
        }

        records.append(record)

    return pd.DataFrame(records)


def save_policy_data(df: pd.DataFrame) -> None:
    """
    Saves policy data into CSV.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Policy data generated successfully: {OUTPUT_FILE}")
    print(f"Total records: {len(df)}")


if __name__ == "__main__":

    policies_df = generate_policy_data(num_records=300)

    save_policy_data(policies_df)