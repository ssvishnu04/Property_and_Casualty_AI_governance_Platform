"""
reinsurance_agent.py

Purpose:
Enterprise Reinsurance Treaty Agent powered by
structured treaty data and Multi-RAG guidance.
"""

from pathlib import Path
import re

import pandas as pd

from rag.multi_rag_service import ask_rag_question


TREATY_FILE = Path("data/structured/reinsurance_treaties.csv")


def load_treaty_data() -> pd.DataFrame:
    if not TREATY_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(TREATY_FILE)


def extract_treaty_id(prompt: str) -> str | None:
    match = re.search(r"TRT-\d{6}", prompt.upper())

    if match:
        return match.group(0)

    return None


def get_sample_treaty_ids(
    treaty_df: pd.DataFrame,
    limit: int = 5,
) -> list:
    if treaty_df.empty or "treaty_id" not in treaty_df.columns:
        return []

    return treaty_df["treaty_id"].head(limit).tolist()


def classify_treaty_risk(
    limit_amount: float,
    attachment_point: float,
    cat_exposure_score: float,
) -> str:
    if (
        limit_amount >= 50000000
        or attachment_point <= 1000000
        or cat_exposure_score >= 0.75
    ):
        return "High"

    if (
        limit_amount >= 10000000
        or attachment_point <= 5000000
        or cat_exposure_score >= 0.40
    ):
        return "Medium"

    return "Low"


def build_rag_metadata(rag_result: dict) -> dict:
    return {
        "rag_domain": "reinsurance",
        "retrieved_sources": rag_result.get("retrieved_sources", []),
        "retrieved_chunk_count": rag_result.get("retrieved_chunk_count", 0),
        "retrieval_latency_seconds": rag_result.get(
            "retrieval_latency_seconds",
            0,
        ),
    }


def format_treaty_response(
    treaty: pd.Series,
    rag_answer: str,
    rag_sources: list,
) -> str:
    limit_amount = float(treaty["limit_amount"])
    attachment_point = float(treaty["attachment_point"])
    retention_amount = float(treaty["retention_amount"])
    reinsurer_share = float(treaty["reinsurer_share"])
    cat_exposure_score = float(treaty["cat_exposure_score"])

    risk_level = classify_treaty_risk(
        limit_amount=limit_amount,
        attachment_point=attachment_point,
        cat_exposure_score=cat_exposure_score,
    )

    response = (
        "Reinsurance Treaty Agent Response:\n\n"
        f"Treaty ID: {treaty['treaty_id']}\n"
        f"Treaty Name: {treaty['treaty_name']}\n"
        f"Treaty Type: {treaty['treaty_type']}\n"
        f"Line of Business: {treaty['line_of_business']}\n"
        f"Coverage Region: {treaty['coverage_region']}\n"
        f"CAT Region: {treaty['cat_region']}\n"
        f"Attachment Point: ${attachment_point:,.2f}\n"
        f"Limit Amount: ${limit_amount:,.2f}\n"
        f"Retention Amount: ${retention_amount:,.2f}\n"
        f"Reinsurer Share: {reinsurer_share:.2f}%\n"
        f"CAT Exposure Score: {cat_exposure_score:.2f}\n"
        f"Reinstatement Terms: {treaty['reinstatement_terms']}\n"
        f"Treaty Status: {treaty['treaty_status']}\n"
        f"Treaty Risk Level: {risk_level}\n\n"
        "Structured Treaty Assessment:\n"
    )

    if risk_level == "High":
        response += (
            "- This treaty presents elevated catastrophe aggregation exposure.\n"
            "- Recoverable monitoring and exhaustion tracking are recommended.\n"
            "- CAT accumulation and reinstatement calculations should be reviewed.\n"
        )

    elif risk_level == "Medium":
        response += (
            "- This treaty presents moderate exposure concentration.\n"
            "- Attachment, recoverable, and CAT exposure assumptions should be validated.\n"
        )

    else:
        response += (
            "- Treaty exposure appears within normal monitoring thresholds.\n"
            "- Continue standard treaty oversight and recoverable tracking.\n"
        )

    response += (
        "\nReinsurance Guidance from RAG:\n"
        f"{rag_answer}\n\n"
    )

    if rag_sources:
        response += "Retrieved Reinsurance Sources:\n"

        unique_sources = []

        for doc in rag_sources:
            source = doc.metadata.get("source", "Unknown Source")

            if source not in unique_sources:
                unique_sources.append(source)

        for source in unique_sources:
            response += f"- {source}\n"

    response += (
        "\nRecommended Next Steps:\n"
        "- Validate treaty attachment and exhaustion assumptions.\n"
        "- Review catastrophe aggregation exposure.\n"
        "- Estimate potential recoverables.\n"
        "- Review reinstatement and retention terms.\n\n"
        "Governance Note:\n"
        "This AI-generated treaty assessment is advisory and should not replace "
        "formal actuarial review, treaty interpretation, legal review, "
        "or enterprise reinsurance oversight."
    )

    return response


def run_reinsurance_agent(prompt: str) -> dict:
    treaty_df = load_treaty_data()

    if treaty_df.empty:
        return {
            "response": (
                "Reinsurance Treaty Agent Response:\n\n"
                "No treaty data was available."
            ),
            "rag_metadata": {},
        }

    treaty_id = extract_treaty_id(prompt)

    if treaty_id is None:
        sample_ids = get_sample_treaty_ids(treaty_df)

        return {
            "response": (
                "Reinsurance Treaty Agent Response:\n\n"
                "Please provide a specific treaty ID.\n\n"
                "Example prompt:\n"
                f"Review treaty {sample_ids[0]} and summarize CAT exposure.\n\n"
                "Sample treaty IDs:\n"
                + "\n".join([f"- {sid}" for sid in sample_ids])
            ),
            "rag_metadata": {},
        }

    matching_treaties = treaty_df[
        treaty_df["treaty_id"].str.upper() == treaty_id
    ]

    if matching_treaties.empty:
        sample_ids = get_sample_treaty_ids(treaty_df)

        return {
            "response": (
                "Reinsurance Treaty Agent Response:\n\n"
                f"Treaty ID {treaty_id} was not found.\n\n"
                "Sample treaty IDs:\n"
                + "\n".join([f"- {sid}" for sid in sample_ids])
            ),
            "rag_metadata": {},
        }

    treaty = matching_treaties.iloc[0]

    rag_result = ask_rag_question(
        domain="reinsurance",
        question=prompt,
    )

    response = format_treaty_response(
        treaty=treaty,
        rag_answer=rag_result.get("answer", "No treaty guidance retrieved."),
        rag_sources=rag_result.get("source_documents", []),
    )

    return {
        "response": response,
        "rag_metadata": build_rag_metadata(rag_result),
    }