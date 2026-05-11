"""
generate_underwriting_data.py

Purpose:
Creates synthetic underwriting submission data.

This represents STRUCTURED insurance underwriting data.

Output:
data/structured/underwriting_submissions.csv
"""

from pathlib import Path
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker


fake = Faker()

OUTPUT_DIR = Path("data/structured")
OUTPUT_FILE = OUTPUT_DIR / "underwriting_submissions.csv"


# -------------------------------------------------------------------
# Industry categories
# -------------------------------------------------------------------

INDUSTRIES = [
    "Manufacturing",
    "Hospitality",
    "Retail",
    "Healthcare",
    "Construction",
    "Technology",
    "Transportation",
    "Energy",
    "Real Estate",
]


# -------------------------------------------------------------------
# High-risk industries
# -------------------------------------------------------------------

HIGH_RISK_INDUSTRIES = [
    "Manufacturing",
    "Construction",
    "Energy",
    "Transportation",
]


# -------------------------------------------------------------------
# US states
# -------------------------------------------------------------------

US_STATES = [
    "TX",
    "FL",
    "CA",
    "LA",
    "NY",
    "IL",
    "OK",
    "CO",
    "GA",
    "NC",
]


# -------------------------------------------------------------------
# CAT exposure mapping
# -------------------------------------------------------------------

CAT_ZONE_MAPPING = {
    "FL": "Hurricane High",
    "LA": "Hurricane High",
    "CA": "Wildfire / Earthquake High",
    "TX": "Hail / Windstorm",
    "OK": "Tornado High",
    "CO": "Hail Moderate",
    "GA": "Windstorm Moderate",
    "NC": "Hurricane Moderate",
    "NY": "Low CAT",
    "IL": "Low CAT",
}


SOURCE_SYSTEMS = [
    "broker_submission_portal",
    "underwriting_workbench",
    "policy_admin_system",
]


SUBMISSION_STATUSES = [
    "New Submission",
    "In Review",
    "Quoted",
    "Bound",
    "Declined",
]


def random_date_within_last_days(days: int = 365) -> datetime:
    """
    Creates a random datetime within the last N days.
    """

    today = datetime.now()

    random_days = random.randint(0, days)

    return today - timedelta(days=random_days)


def derive_cat_zone(state: str) -> str:
    """
    Derives CAT zone from state.

    This simulates enterprise CAT exposure logic.
    """

    return CAT_ZONE_MAPPING.get(state, "Low CAT")


def calculate_risk_score(
    industry: str,
    insured_value: float,
    prior_losses: int,
    cat_zone: str,
) -> tuple:
    """
    Calculates underwriting risk score.

    This simulates underwriting scoring logic.

    Returns:
        risk_score
        risk_tier
    """

    score = 20

    # ---------------------------------------------------------------
    # Industry risk
    # ---------------------------------------------------------------

    if industry in HIGH_RISK_INDUSTRIES:
        score += 20

    # ---------------------------------------------------------------
    # High insured value
    # ---------------------------------------------------------------

    if insured_value > 5_000_000:
        score += 20

    elif insured_value > 1_000_000:
        score += 10

    # ---------------------------------------------------------------
    # Prior losses
    # ---------------------------------------------------------------

    if prior_losses >= 5:
        score += 25

    elif prior_losses >= 3:
        score += 15

    elif prior_losses >= 1:
        score += 5

    # ---------------------------------------------------------------
    # CAT exposure
    # ---------------------------------------------------------------

    if "High" in cat_zone:
        score += 25

    elif "Moderate" in cat_zone:
        score += 10

    # ---------------------------------------------------------------
    # Risk tier
    # ---------------------------------------------------------------

    if score >= 75:
        risk_tier = "High"

    elif score >= 45:
        risk_tier = "Medium"

    else:
        risk_tier = "Low"

    return score, risk_tier


def generate_broker_note(industry: str, risk_tier: str) -> str:
    """
    Creates synthetic broker notes.
    """

    templates = [
        f"Broker submitted updated loss runs for {industry} account.",
        f"Insured requesting competitive pricing for upcoming renewal.",
        f"Underwriter requested additional inspection reports.",
        f"Submission categorized as {risk_tier} risk based on exposure profile.",
        f"Broker highlighted recent operational improvements reducing risk exposure.",
    ]

    return random.choice(templates)


def generate_underwriting_data(
    num_records: int = 200,
) -> pd.DataFrame:
    """
    Generates underwriting submission records.
    """

    records = []

    for i in range(1, num_records + 1):

        submission_id = f"SUB-{i:06d}"

        policy_id = f"POL-{random.randint(1, 300):06d}"

        state = random.choice(US_STATES)

        industry = random.choice(INDUSTRIES)

        insured_value = round(
            random.uniform(250_000, 10_000_000),
            2
        )

        prior_losses = random.randint(0, 7)

        cat_zone = derive_cat_zone(state)

        risk_score, risk_tier = calculate_risk_score(
            industry=industry,
            insured_value=insured_value,
            prior_losses=prior_losses,
            cat_zone=cat_zone,
        )

        submission_timestamp = random_date_within_last_days(365)

        updated_timestamp = (
            submission_timestamp
            + timedelta(days=random.randint(1, 45))
        )

        record = {
            "submission_id": submission_id,
            "policy_id": policy_id,
            "insured_name": fake.company(),
            "industry": industry,
            "state": state,
            "insured_value": insured_value,
            "prior_losses": prior_losses,
            "cat_zone": cat_zone,
            "risk_score": risk_score,
            "risk_tier": risk_tier,
            "submission_status": random.choice(
                SUBMISSION_STATUSES
            ),
            "broker_name": fake.company(),
            "broker_notes": generate_broker_note(
                industry,
                risk_tier,
            ),
            "source_system": random.choice(
                SOURCE_SYSTEMS
            ),
            "data_sensitivity": random.choice(
                ["internal", "confidential", "restricted"]
            ),
            "submission_timestamp": submission_timestamp.isoformat(),
            "updated_timestamp": updated_timestamp.isoformat(),
            "created_by": random.choice(
                ["underwriter_001", "underwriter_002"]
            ),
            "updated_by": random.choice(
                ["underwriter_001", "underwriter_002"]
            ),
        }

        records.append(record)

    return pd.DataFrame(records)


def save_underwriting_data(df: pd.DataFrame) -> None:
    """
    Saves underwriting data to CSV.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print(
        f"Underwriting data generated successfully: {OUTPUT_FILE}"
    )

    print(f"Total records: {len(df)}")


if __name__ == "__main__":

    underwriting_df = generate_underwriting_data(
        num_records=200
    )

    save_underwriting_data(underwriting_df)