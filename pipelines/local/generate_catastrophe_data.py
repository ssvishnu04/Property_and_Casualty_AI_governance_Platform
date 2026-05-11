"""
generate_catastrophe_data.py

Purpose:
Creates synthetic catastrophe (CAT) event data.

This represents STRUCTURED catastrophe event data.

Output:
data/structured/cat_events.csv
"""

from pathlib import Path
import random
from datetime import datetime, timedelta

import pandas as pd


OUTPUT_DIR = Path("data/structured")
OUTPUT_FILE = OUTPUT_DIR / "cat_events.csv"


EVENT_TYPES = [
    "Hurricane",
    "Wildfire",
    "Earthquake",
    "Flood",
    "Tornado",
    "Hailstorm",
    "Winter Storm",
]


US_REGIONS = [
    "Texas",
    "Florida",
    "California",
    "Louisiana",
    "Oklahoma",
    "Colorado",
    "Georgia",
    "North Carolina",
]


SEVERITY_LEVELS = [
    "Low",
    "Moderate",
    "High",
    "Extreme",
]


SOURCE_SYSTEMS = [
    "cat_model_platform",
    "weather_event_feed",
    "exposure_aggregation_system",
]


def random_date_within_last_days(days: int = 900) -> datetime:
    """
    Creates a random catastrophe event date.
    """

    today = datetime.now()

    random_days = random.randint(0, days)

    return today - timedelta(days=random_days)


def derive_estimated_loss(severity: str) -> float:
    """
    Derives estimated loss based on CAT severity.

    This simulates catastrophe modeling logic.
    """

    if severity == "Low":
        return round(random.uniform(500_000, 5_000_000), 2)

    elif severity == "Moderate":
        return round(random.uniform(5_000_000, 25_000_000), 2)

    elif severity == "High":
        return round(random.uniform(25_000_000, 150_000_000), 2)

    return round(random.uniform(150_000_000, 1_000_000_000), 2)


def derive_claims_volume(severity: str) -> int:
    """
    Derives expected claim volume.

    Severe CAT events produce more claims.
    """

    if severity == "Low":
        return random.randint(50, 300)

    elif severity == "Moderate":
        return random.randint(300, 1500)

    elif severity == "High":
        return random.randint(1500, 7000)

    return random.randint(7000, 25000)


def generate_event_summary(
    event_type: str,
    severity: str,
    region: str,
) -> str:
    """
    Creates synthetic CAT event summary.
    """

    summaries = [
        f"{severity} severity {event_type} impacted {region}.",
        f"CAT event caused widespread operational disruption across {region}.",
        f"Insured losses expected to increase following {event_type} event.",
        f"Claims surge anticipated due to severe weather conditions.",
        f"Exposure monitoring initiated after {event_type} activity in {region}.",
    ]

    return random.choice(summaries)


def generate_catastrophe_data(
    num_records: int = 50,
) -> pd.DataFrame:
    """
    Generates catastrophe event records.
    """

    records = []

    for i in range(1, num_records + 1):

        event_id = f"CAT-{i:06d}"

        event_type = random.choice(EVENT_TYPES)

        region = random.choice(US_REGIONS)

        severity = random.choice(SEVERITY_LEVELS)

        estimated_loss = derive_estimated_loss(severity)

        expected_claims_volume = derive_claims_volume(
            severity
        )

        event_date = random_date_within_last_days(900)

        ingestion_timestamp = (
            event_date + timedelta(hours=random.randint(1, 48))
        )

        record = {
            "event_id": event_id,
            "event_name": f"{event_type} Event {i}",
            "event_type": event_type,
            "severity": severity,
            "region": region,
            "estimated_loss": estimated_loss,
            "expected_claims_volume": expected_claims_volume,
            "event_summary": generate_event_summary(
                event_type,
                severity,
                region,
            ),
            "source_system": random.choice(
                SOURCE_SYSTEMS
            ),
            "data_sensitivity": random.choice(
                ["internal", "confidential"]
            ),
            "event_date": event_date.date().isoformat(),
            "event_timestamp": event_date.isoformat(),
            "ingestion_timestamp": ingestion_timestamp.isoformat(),
            "created_by": "cat_monitoring_system",
        }

        records.append(record)

    return pd.DataFrame(records)


def save_catastrophe_data(df: pd.DataFrame) -> None:
    """
    Saves CAT event data to CSV.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print(
        f"CAT event data generated successfully: {OUTPUT_FILE}"
    )

    print(f"Total records: {len(df)}")


if __name__ == "__main__":

    cat_df = generate_catastrophe_data(
        num_records=50
    )

    save_catastrophe_data(cat_df)