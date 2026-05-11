"""
generate_users_data.py

Purpose:
Creates synthetic enterprise user data.

This represents STRUCTURED user and RBAC data.

Output:
data/structured/users.csv
"""

from pathlib import Path
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker


fake = Faker()

OUTPUT_DIR = Path("data/structured")
OUTPUT_FILE = OUTPUT_DIR / "users.csv"


ROLES = {
    "Claims Adjuster": {
        "department": "Claims",
        "access_level": "Medium",
    },
    "Claims Manager": {
        "department": "Claims",
        "access_level": "High",
    },
    "Underwriter": {
        "department": "Underwriting",
        "access_level": "Medium",
    },
    "Underwriting Manager": {
        "department": "Underwriting",
        "access_level": "High",
    },
    "Reinsurance Analyst": {
        "department": "Reinsurance",
        "access_level": "Medium",
    },
    "Reinsurance Manager": {
        "department": "Reinsurance",
        "access_level": "High",
    },
    "Audit Reviewer": {
        "department": "Audit",
        "access_level": "High",
    },
    "Security Analyst": {
        "department": "Security",
        "access_level": "High",
    },
    "AI Platform Admin": {
        "department": "AI Platform",
        "access_level": "Critical",
    },
}


SOURCE_SYSTEMS = [
    "identity_management_system",
    "hr_system",
    "rbac_platform",
]


def random_date_within_last_days(days: int = 1000) -> datetime:
    """
    Creates random historical dates.
    """

    today = datetime.now()

    random_days = random.randint(0, days)

    return today - timedelta(days=random_days)


def generate_email(first_name: str, last_name: str) -> str:
    """
    Creates enterprise-style email address.
    """

    return (
        f"{first_name.lower()}."
        f"{last_name.lower()}@testinsurancecorp.com"
    )


def generate_users_data(
    num_records: int = 50,
) -> pd.DataFrame:
    """
    Generates enterprise user records.
    """

    records = []

    role_names = list(ROLES.keys())

    for i in range(1, num_records + 1):

        role = random.choice(role_names)

        role_details = ROLES[role]

        first_name = fake.first_name()

        last_name = fake.last_name()

        created_timestamp = random_date_within_last_days(
            1200
        )

        last_login_timestamp = (
            created_timestamp
            + timedelta(days=random.randint(1, 365))
        )

        user_id = f"USR-{i:05d}"

        record = {
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": generate_email(
                first_name,
                last_name,
            ),
            "role": role,
            "department": role_details["department"],
            "access_level": role_details["access_level"],
            "account_status": random.choice(
                ["Active", "Active", "Active", "Disabled"]
            ),
            "mfa_enabled": random.choice(
                [True, True, True, False]
            ),
            "data_sensitivity_access": random.choice(
                ["internal", "confidential", "restricted"]
            ),
            "source_system": random.choice(
                SOURCE_SYSTEMS
            ),
            "created_timestamp": created_timestamp.isoformat(),
            "last_login_timestamp": (
                last_login_timestamp.isoformat()
            ),
            "created_by": "identity_admin_system",
        }

        records.append(record)

    return pd.DataFrame(records)


def save_users_data(df: pd.DataFrame) -> None:
    """
    Saves user data to CSV.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print(
        f"Users data generated successfully: {OUTPUT_FILE}"
    )

    print(f"Total records: {len(df)}")


if __name__ == "__main__":

    users_df = generate_users_data(
        num_records=50
    )

    save_users_data(users_df)