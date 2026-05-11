"""
generate_reinsurance_data.py

Purpose:
Creates synthetic reinsurance treaty data.

This represents STRUCTURED reinsurance data.

Output:
data/structured/reinsurance_treaties.csv
"""

from pathlib import Path
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker


fake = Faker()

OUTPUT_DIR = Path("data/structured")
OUTPUT_FILE = OUTPUT_DIR / "reinsurance_treaties.csv"


TREATY_TYPES = [
    "Quota Share",
    "Surplus Share",
    "Excess of Loss",
    "Catastrophe XOL",
]


LINES_OF_BUSINESS = [
    "Commercial Property",
    "General Liability",
    "Commercial Auto",
    "Workers Compensation",
    "Cyber",
]


TERRITORIES = [
    "North America",
    "United States",
    "Southeast US",
    "Gulf Coast",
    "Global",
]


EXCLUSIONS = [
    "Cyber Exclusion",
    "War Exclusion",
    "Nuclear Exclusion",
    "Pandemic Exclusion",
    "Terrorism Exclusion",
]


SOURCE_SYSTEMS = [
    "reinsurance_admin_system",
    "treaty_management_platform",
    "ceded_reinsurance_portal",
]


def random_date_within_last_days(days: int = 1000) -> datetime:
    """
    Creates a random datetime within the last N days.
    """

    today = datetime.now()

    random_days = random.randint(0, days)

    return today - timedelta(days=random_days)


def derive_risk_tier(
    treaty_limit: float,
    cession_percent: float,
    treaty_type: str,
) -> str:
    """
    Derives treaty risk tier.

    Larger treaties and CAT treaties
    are considered higher risk.
    """

    score = 0

    if treaty_limit >= 50_000_000:
        score += 40

    elif treaty_limit >= 10_000_000:
        score += 20

    if cession_percent >= 75:
        score += 20

    elif cession_percent >= 40:
        score += 10

    if treaty_type == "Catastrophe XOL":
        score += 30

    if score >= 60:
        return "High"

    elif score >= 30:
        return "Medium"

    return "Low"


def generate_treaty_summary(
    treaty_type: str,
    territory: str,
) -> str:
    """
    Creates synthetic treaty summary text.
    """

    summaries = [
        f"{treaty_type} treaty covering exposures in {territory}.",
        f"Treaty includes catastrophe protection for {territory}.",
        f"Reinsurance agreement structured for multi-line protection.",
        f"Treaty designed to reduce retained underwriting volatility.",
        f"Coverage includes regional catastrophe aggregation management.",
    ]

    return random.choice(summaries)


def generate_reinsurance_data(
    num_records: int = 100,
) -> pd.DataFrame:
    """
    Generates synthetic reinsurance treaty data.
    """

    records = []

    for i in range(1, num_records + 1):

        treaty_id = f"TRT-{i:06d}"

        treaty_type = random.choice(TREATY_TYPES)

        treaty_limit = random.choice(
            [
                5_000_000,
                10_000_000,
                25_000_000,
                50_000_000,
                100_000_000,
            ]
        )

        attachment_point = round(
            treaty_limit * random.uniform(0.05, 0.25),
            2
        )

        cession_percent = random.choice(
            [10, 20, 30, 40, 50, 75, 90]
        )

        territory = random.choice(TERRITORIES)

        risk_tier = derive_risk_tier(
            treaty_limit=treaty_limit,
            cession_percent=cession_percent,
            treaty_type=treaty_type,
        )

        effective_date = random_date_within_last_days(1200)

        expiration_date = (
            effective_date + timedelta(days=365)
        )

        created_timestamp = (
            effective_date - timedelta(days=30)
        )

        updated_timestamp = (
            effective_date + timedelta(days=90)
        )

        selected_exclusions = random.sample(
            EXCLUSIONS,
            k=random.randint(1, 2)
        )

        record = {
            "treaty_id": treaty_id,
            "cedent_company": fake.company(),
            "reinsurer_company": fake.company(),
            "treaty_type": treaty_type,
            "line_of_business": random.choice(
                LINES_OF_BUSINESS
            ),
            "territory": territory,
            "treaty_limit": treaty_limit,
            "attachment_point": attachment_point,
            "cession_percent": cession_percent,
            "risk_tier": risk_tier,
            "exclusions": ", ".join(
                selected_exclusions
            ),
            "treaty_summary": generate_treaty_summary(
                treaty_type,
                territory,
            ),
            "source_system": random.choice(
                SOURCE_SYSTEMS
            ),
            "data_sensitivity": random.choice(
                ["internal", "confidential", "restricted"]
            ),
            "effective_date": effective_date.date().isoformat(),
            "expiration_date": expiration_date.date().isoformat(),
            "created_timestamp": created_timestamp.isoformat(),
            "updated_timestamp": updated_timestamp.isoformat(),
            "created_by": random.choice(
                ["reinsurance_analyst_001", "ri_manager_001"]
            ),
            "updated_by": random.choice(
                ["reinsurance_analyst_001", "ri_manager_001"]
            ),
        }

        records.append(record)

    return pd.DataFrame(records)


def save_reinsurance_data(df: pd.DataFrame) -> None:
    """
    Saves reinsurance data to CSV.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print(
        f"Reinsurance data generated successfully: {OUTPUT_FILE}"
    )

    print(f"Total records: {len(df)}")


if __name__ == "__main__":

    reinsurance_df = generate_reinsurance_data(
        num_records=100
    )

    save_reinsurance_data(reinsurance_df)