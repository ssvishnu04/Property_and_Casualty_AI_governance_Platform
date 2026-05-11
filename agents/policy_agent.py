"""
policy_agent.py

Purpose:
Enterprise Policy Coverage Agent
powered by Multi-Domain RAG.
"""

from rag.multi_rag_service import (
    ask_rag_question,
)


def run_policy_agent(
    prompt: str,
) -> dict:
    """
    Executes policy coverage RAG workflow.
    """

    rag_result = ask_rag_question(
        domain="policy",
        question=prompt,
    )

    answer = rag_result.get(
        "answer",
        "No policy guidance retrieved.",
    )

    source_documents = rag_result.get(
        "source_documents",
        [],
    )

    retrieved_sources = rag_result.get(
        "retrieved_sources",
        [],
    )

    retrieval_latency_seconds = (
        rag_result.get(
            "retrieval_latency_seconds",
            0,
        )
    )

    retrieved_chunk_count = (
        rag_result.get(
            "retrieved_chunk_count",
            0,
        )
    )

    response = (
        "Policy Coverage Agent Response:\n\n"
        f"{answer}\n\n"
    )

    if source_documents:

        response += (
            "Retrieved Policy Sources:\n"
        )

        unique_sources = []

        for doc in source_documents:

            source = doc.metadata.get(
                "source",
                "Unknown Source",
            )

            if source not in unique_sources:
                unique_sources.append(source)

        for source in unique_sources:
            response += f"- {source}\n"

    response += (
        "\nGovernance Note:\n"
        "This AI-generated policy interpretation is advisory and "
        "should not replace formal claims, underwriting, legal, "
        "or compliance review."
    )

    return {
        "response": response,
        "rag_metadata": {
            "rag_domain": "policy",
            "retrieved_sources": (
                retrieved_sources
            ),
            "retrieved_chunk_count": (
                retrieved_chunk_count
            ),
            "retrieval_latency_seconds": (
                retrieval_latency_seconds
            ),
        },
    }