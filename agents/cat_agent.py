"""
cat_agent.py

Purpose:
Enterprise CAT Event Agent powered by
structured catastrophe event data and Multi-RAG guidance.
"""

from pathlib import Path
import re

import pandas as pd

from rag.multi_rag_service import ask_rag_question


CAT_FILE = Path("data/structured/cat_events.csv")


def load_cat_data() -> pd.DataFrame:
    if not CAT_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(CAT_FILE)


def extract_cat_event_id(prompt: str) -> str | None:
    match = re.search(r"CAT-\d{6}", prompt.upper())

    if match:
        return match.group(0)

    return None


def get_sample_cat_ids(cat_df: pd.DataFrame, limit: int = 5) -> list:
    if cat_df.empty or "cat_event_id" not in cat_df.columns:
        return []

    return cat_df["cat_event_id"].head(limit).tolist()


def classify_cat_severity(
    estimated_loss: float,
    affected_claims: int,
) -> str:
    if estimated_loss >= 50000000 or affected_claims >= 1000:
        return "High"

    if estimated_loss >= 10000000 or affected_claims >= 250:
        return "Medium"

    return "Low"


def build_rag_metadata(rag_result: dict) -> dict:
    return {
        "rag_domain": "cat",
        "retrieved_sources": rag_result.get("retrieved_sources", []),
        "retrieved_chunk_count": rag_result.get("retrieved_chunk_count", 0),
        "retrieval_latency_seconds": rag_result.get(
            "retrieval_latency_seconds",
            0,
        ),
    }


def format_cat_response(
    cat_event: pd.Series,
    rag_answer: str,
    rag_sources: list,
) -> str:
    estimated_loss = float(cat_event["estimated_loss_amount"])
    affected_claims = int(cat_event["affected_claim_count"])

    severity = classify_cat_severity(
        estimated_loss=estimated_loss,
        affected_claims=affected_claims,
    )

    response = (
        "CAT Event Agent Response:\n\n"
        f"CAT Event ID: {cat_event['cat_event_id']}\n"
        f"Event Name: {cat_event['event_name']}\n"
        f"Event Type: {cat_event['event_type']}\n"
        f"Region: {cat_event['region']}\n"
        f"Event Status: {cat_event['event_status']}\n"
        f"Estimated Loss Amount: ${estimated_loss:,.2f}\n"
        f"Affected Claim Count: {affected_claims:,}\n"
        f"CAT Severity Level: {severity}\n\n"
        "Structured CAT Assessment:\n"
    )

    if severity == "High":
        response += (
            "- This CAT event presents significant operational and financial exposure.\n"
            "- CAT escalation procedures should be activated.\n"
            "- Reserve adequacy and catastrophe aggregation should be reviewed.\n"
            "- Reinsurance recoverable monitoring is recommended.\n"
        )

    elif severity == "Medium":
        response += (
            "- This CAT event presents moderate operational impact.\n"
            "- Claims surge monitoring and reserve tracking are recommended.\n"
        )

    else:
        response += (
            "- CAT activity appears within manageable operational thresholds.\n"
            "- Continue standard CAT monitoring and reporting.\n"
        )

    response += (
        "\nCAT Guidance from RAG:\n"
        f"{rag_answer}\n\n"
    )

    if rag_sources:
        response += "Retrieved CAT Sources:\n"

        unique_sources = []

        for doc in rag_sources:
            source = doc.metadata.get("source", "Unknown Source")

            if source not in unique_sources:
                unique_sources.append(source)

        for source in unique_sources:
            response += f"- {source}\n"

    response += (
        "\nRecommended Next Steps:\n"
        "- Monitor catastrophe claim volume trends.\n"
        "- Validate CAT reserve adequacy.\n"
        "- Review operational staffing requirements.\n"
        "- Assess reinsurance recovery implications.\n\n"
        "Governance Note:\n"
        "This AI-generated catastrophe assessment is advisory and should not replace "
        "formal catastrophe response procedures, actuarial review, "
        "claims authority, or enterprise risk oversight."
    )

    return response


def run_cat_agent(prompt: str) -> dict:
    cat_df = load_cat_data()

    if cat_df.empty:
        return {
            "response": (
                "CAT Event Agent Response:\n\n"
                "No catastrophe event data was available."
            ),
            "rag_metadata": {},
        }

    cat_event_id = extract_cat_event_id(prompt)

    if cat_event_id is None:
        sample_ids = get_sample_cat_ids(cat_df)

        return {
            "response": (
                "CAT Event Agent Response:\n\n"
                "Please provide a specific CAT event ID.\n\n"
                "Example prompt:\n"
                f"Review CAT event {sample_ids[0]} and summarize operational impact.\n\n"
                "Sample CAT Event IDs:\n"
                + "\n".join([f"- {sid}" for sid in sample_ids])
            ),
            "rag_metadata": {},
        }

    matching_events = cat_df[
        cat_df["cat_event_id"].str.upper() == cat_event_id
    ]

    if matching_events.empty:
        sample_ids = get_sample_cat_ids(cat_df)

        return {
            "response": (
                "CAT Event Agent Response:\n\n"
                f"CAT Event ID {cat_event_id} was not found.\n\n"
                "Sample CAT Event IDs:\n"
                + "\n".join([f"- {sid}" for sid in sample_ids])
            ),
            "rag_metadata": {},
        }

    cat_event = matching_events.iloc[0]

    rag_result = ask_rag_question(
        domain="cat",
        question=prompt,
    )

    response = format_cat_response(
        cat_event=cat_event,
        rag_answer=rag_result.get("answer", "No CAT guidance retrieved."),
        rag_sources=rag_result.get("source_documents", []),
    )

    return {
        "response": response,
        "rag_metadata": build_rag_metadata(rag_result),
    }