"""
claims_agent.py

Purpose:
Data-aware Claims Summary Agent powered by structured claims data
and Multi-Domain RAG claims guidance.
"""

from pathlib import Path
import re

import pandas as pd

from rag.multi_rag_service import ask_rag_question


CLAIMS_FILE = Path("data/structured/claims.csv")


def load_claims_data() -> pd.DataFrame:
    if not CLAIMS_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(CLAIMS_FILE)


def extract_claim_id(prompt: str) -> str | None:
    match = re.search(r"CLM-\d{6}", prompt.upper())

    if match:
        return match.group(0)

    return None


def get_sample_claim_ids(
    claims_df: pd.DataFrame,
    limit: int = 5,
) -> list:
    if claims_df.empty or "claim_id" not in claims_df.columns:
        return []

    return claims_df["claim_id"].head(limit).tolist()


def classify_claim_severity(
    reserve_amount: float,
    litigation_flag,
) -> str:
    litigation = str(litigation_flag).lower() in [
        "true",
        "1",
        "yes",
    ]

    if reserve_amount >= 500000 or litigation:
        return "High"

    if reserve_amount >= 100000:
        return "Medium"

    return "Low"


def build_rag_metadata(rag_result: dict) -> dict:
    return {
        "rag_domain": "claims",
        "retrieved_sources": rag_result.get("retrieved_sources", []),
        "retrieved_chunk_count": rag_result.get("retrieved_chunk_count", 0),
        "retrieval_latency_seconds": rag_result.get(
            "retrieval_latency_seconds",
            0,
        ),
    }


def format_claim_summary(
    claim: pd.Series,
    rag_answer: str,
    rag_sources: list,
) -> str:
    reserve_amount = float(claim["reserve_amount"])
    paid_amount = float(claim["paid_amount"])

    severity = classify_claim_severity(
        reserve_amount=reserve_amount,
        litigation_flag=claim["litigation_flag"],
    )

    response = (
        "Claims Summary Agent Response:\n\n"
        f"Claim ID: {claim['claim_id']}\n"
        f"Policy ID: {claim['policy_id']}\n"
        f"Insured Name: {claim['insured_name']}\n"
        f"Line of Business: {claim['line_of_business']}\n"
        f"Loss Type: {claim['loss_type']}\n"
        f"Claim Status: {claim['claim_status']}\n"
        f"Reserve Amount: ${reserve_amount:,.2f}\n"
        f"Paid Amount: ${paid_amount:,.2f}\n"
        f"Litigation Flag: {claim['litigation_flag']}\n"
        f"Claim Severity: {severity}\n\n"
        "Structured Claim Assessment:\n"
    )

    if severity == "High":
        response += (
            "- This claim presents elevated severity or litigation exposure.\n"
            "- Escalation to senior claims management is recommended.\n"
            "- Reserve adequacy and legal involvement should be reviewed.\n"
        )

    elif severity == "Medium":
        response += (
            "- This claim presents moderate severity.\n"
            "- Continued reserve monitoring and documentation review are recommended.\n"
        )

    else:
        response += (
            "- This claim appears to be within normal handling thresholds.\n"
            "- Continue standard claims review and documentation validation.\n"
        )

    response += (
        "\nClaims Handling Guidance from RAG:\n"
        f"{rag_answer}\n\n"
    )

    if rag_sources:
        response += "Retrieved Claims Sources:\n"

        unique_sources = []

        for doc in rag_sources:
            source = doc.metadata.get("source", "Unknown Source")

            if source not in unique_sources:
                unique_sources.append(source)

        for source in unique_sources:
            response += f"- {source}\n"

    response += (
        "\nRecommended Next Steps:\n"
        "- Validate policy coverage and effective dates.\n"
        "- Review supporting claim documentation.\n"
        "- Confirm reserve adequacy.\n"
        "- Escalate if litigation, large-loss, or high-severity indicators are present.\n\n"
        "Governance Note:\n"
        "This AI-generated claims summary is advisory and should not replace "
        "licensed adjuster judgment, legal review, or formal claims authority workflows."
    )

    return response


def run_claims_agent(prompt: str) -> dict:
    claims_df = load_claims_data()

    if claims_df.empty:
        return {
            "response": (
                "Claims Summary Agent Response:\n\n"
                "No claims data was available for review."
            ),
            "rag_metadata": {},
        }

    claim_id = extract_claim_id(prompt)

    if claim_id is None:
        sample_claim_ids = get_sample_claim_ids(claims_df)

        return {
            "response": (
                "Claims Summary Agent Response:\n\n"
                "Please provide a specific claim ID so I can review the correct claim.\n\n"
                "Example prompt:\n"
                f"Summarize claim {sample_claim_ids[0]} and identify next steps.\n\n"
                "Sample claim IDs:\n"
                + "\n".join([f"- {cid}" for cid in sample_claim_ids])
            ),
            "rag_metadata": {},
        }

    matching_claims = claims_df[
        claims_df["claim_id"].str.upper() == claim_id
    ]

    if matching_claims.empty:
        sample_claim_ids = get_sample_claim_ids(claims_df)

        return {
            "response": (
                "Claims Summary Agent Response:\n\n"
                f"I could not find claim ID {claim_id} in the available claims dataset.\n\n"
                "Please try one of these sample claim IDs:\n"
                + "\n".join([f"- {cid}" for cid in sample_claim_ids])
            ),
            "rag_metadata": {},
        }

    claim = matching_claims.iloc[0]

    rag_result = ask_rag_question(
        domain="claims",
        question=prompt,
    )

    response = format_claim_summary(
        claim=claim,
        rag_answer=rag_result.get("answer", "No claims guidance was retrieved."),
        rag_sources=rag_result.get("source_documents", []),
    )

    return {
        "response": response,
        "rag_metadata": build_rag_metadata(rag_result),
    }