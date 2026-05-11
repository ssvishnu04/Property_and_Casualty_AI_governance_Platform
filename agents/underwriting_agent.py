"""
underwriting_agent.py

Purpose:
Enterprise Underwriting Copilot powered by
structured underwriting data and Multi-RAG guidance.
"""

from pathlib import Path
import re

import pandas as pd

from rag.multi_rag_service import ask_rag_question


UNDERWRITING_FILE = Path("data/structured/underwriting_submissions.csv")


def load_underwriting_data() -> pd.DataFrame:
    if not UNDERWRITING_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(UNDERWRITING_FILE)


def extract_submission_id(prompt: str) -> str | None:
    match = re.search(r"(SUB|UWS)-\d{6}", prompt.upper())

    if match:
        return match.group(0)

    return None


def get_sample_submission_ids(
    underwriting_df: pd.DataFrame,
    limit: int = 5,
) -> list:
    if underwriting_df.empty or "submission_id" not in underwriting_df.columns:
        return []

    return underwriting_df["submission_id"].head(limit).tolist()


def classify_underwriting_risk(
    tiv_amount: float,
    catastrophe_score: float,
) -> str:
    if tiv_amount >= 10000000 or catastrophe_score >= 0.75:
        return "High"

    if tiv_amount >= 3000000 or catastrophe_score >= 0.40:
        return "Medium"

    return "Low"


def build_rag_metadata(rag_result: dict) -> dict:
    return {
        "rag_domain": "underwriting",
        "retrieved_sources": rag_result.get("retrieved_sources", []),
        "retrieved_chunk_count": rag_result.get("retrieved_chunk_count", 0),
        "retrieval_latency_seconds": rag_result.get(
            "retrieval_latency_seconds",
            0,
        ),
    }


def format_underwriting_response(
    submission: pd.Series,
    rag_answer: str,
    rag_sources: list,
) -> str:
    tiv_amount = float(submission["tiv_amount"])
    catastrophe_score = float(submission["catastrophe_score"])
    requested_limit = float(submission["requested_limit"])
    deductible = float(submission["deductible"])

    risk_level = classify_underwriting_risk(
        tiv_amount=tiv_amount,
        catastrophe_score=catastrophe_score,
    )

    response = (
        "Underwriting Copilot Response:\n\n"
        f"Submission ID: {submission['submission_id']}\n"
        f"Applicant Name: {submission['applicant_name']}\n"
        f"Industry: {submission['industry']}\n"
        f"Location: {submission['location']}\n"
        f"TIV Amount: ${tiv_amount:,.2f}\n"
        f"Requested Limit: ${requested_limit:,.2f}\n"
        f"Deductible: ${deductible:,.2f}\n"
        f"Catastrophe Score: {catastrophe_score:.2f}\n"
        f"Underwriting Risk Level: {risk_level}\n\n"
        "Structured Underwriting Assessment:\n"
    )

    if risk_level == "High":
        response += (
            "- This submission presents elevated underwriting exposure.\n"
            "- Secondary underwriting review is recommended.\n"
            "- CAT aggregation and pricing adequacy should be reviewed.\n"
            "- Risk engineering review may be required.\n"
        )

    elif risk_level == "Medium":
        response += (
            "- This submission presents moderate underwriting risk.\n"
            "- Additional documentation review may be appropriate.\n"
            "- Exposure accumulation should be monitored.\n"
        )

    else:
        response += (
            "- This submission appears within standard underwriting thresholds.\n"
            "- Continue standard underwriting review workflow.\n"
        )

    response += (
        "\nUnderwriting Guidance from RAG:\n"
        f"{rag_answer}\n\n"
    )

    if rag_sources:
        response += "Retrieved Underwriting Sources:\n"

        unique_sources = []

        for doc in rag_sources:
            source = doc.metadata.get("source", "Unknown Source")

            if source not in unique_sources:
                unique_sources.append(source)

        for source in unique_sources:
            response += f"- {source}\n"

    response += (
        "\nRecommended Next Steps:\n"
        "- Review underwriting guidelines and risk appetite.\n"
        "- Validate CAT exposure and geographic concentration.\n"
        "- Assess pricing adequacy and requested limits.\n"
        "- Review inspection and valuation documentation.\n\n"
        "Governance Note:\n"
        "This AI-generated underwriting assessment is advisory and should not replace "
        "licensed underwriting authority, actuarial review, or enterprise risk oversight."
    )

    return response


def run_underwriting_agent(prompt: str) -> dict:
    underwriting_df = load_underwriting_data()

    if underwriting_df.empty:
        return {
            "response": (
                "Underwriting Copilot Response:\n\n"
                "No underwriting submission data was available."
            ),
            "rag_metadata": {},
        }

    submission_id = extract_submission_id(prompt)

    if submission_id is None:
        sample_ids = get_sample_submission_ids(underwriting_df)

        return {
            "response": (
                "Underwriting Copilot Response:\n\n"
                "Please provide a specific underwriting submission ID.\n\n"
                "Example prompt:\n"
                f"Review underwriting submission {sample_ids[0]} and summarize underwriting concerns.\n\n"
                "Sample submission IDs:\n"
                + "\n".join([f"- {sid}" for sid in sample_ids])
            ),
            "rag_metadata": {},
        }

    matching_submissions = underwriting_df[
        underwriting_df["submission_id"].str.upper() == submission_id
    ]

    if matching_submissions.empty:
        sample_ids = get_sample_submission_ids(underwriting_df)

        return {
            "response": (
                "Underwriting Copilot Response:\n\n"
                f"Submission ID {submission_id} was not found.\n\n"
                "Sample submission IDs:\n"
                + "\n".join([f"- {sid}" for sid in sample_ids])
            ),
            "rag_metadata": {},
        }

    submission = matching_submissions.iloc[0]

    rag_result = ask_rag_question(
        domain="underwriting",
        question=prompt,
    )

    response = format_underwriting_response(
        submission=submission,
        rag_answer=rag_result.get("answer", "No underwriting guidance retrieved."),
        rag_sources=rag_result.get("source_documents", []),
    )

    return {
        "response": response,
        "rag_metadata": build_rag_metadata(rag_result),
    }