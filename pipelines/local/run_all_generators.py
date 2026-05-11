"""
run_all_generators.py

Purpose:
Runs all synthetic data generators in sequence.

This simulates enterprise pipeline orchestration.
"""

import subprocess
import sys
from pathlib import Path


PIPELINE_SCRIPTS = [
    "generate_claims_data.py",
    "generate_policy_data.py",
    "generate_underwriting_data.py",
    "generate_reinsurance_data.py",
    "generate_catastrophe_data.py",
    "generate_users_data.py",
    "generate_agents_registry.py",
    "generate_tools_registry.py",
    "generate_ai_events.py",
    "generate_unstructured_docs.py",
]


PIPELINE_DIR = Path("pipelines/local")


def run_pipeline(script_name: str):
    """
    Executes one pipeline script.
    """

    script_path = PIPELINE_DIR / script_name

    print("\n" + "=" * 70)
    print(f"RUNNING: {script_name}")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
    )

    print(result.stdout)

    if result.stderr:
        print("ERRORS:")
        print(result.stderr)


def run_all_pipelines():
    """
    Runs all synthetic data pipelines.
    """

    print("\nStarting Enterprise AI Governance Data Pipelines...\n")

    for script in PIPELINE_SCRIPTS:
        run_pipeline(script)

    print("\nAll pipelines completed successfully.\n")


if __name__ == "__main__":

    run_all_pipelines()