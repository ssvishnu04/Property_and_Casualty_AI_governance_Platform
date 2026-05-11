"""
retrieval_service.py

Purpose:
Loads chunked enterprise documents and retrieves
the most relevant chunks for a user query.

This is a lightweight retrieval layer before embeddings/vector search.
"""

from pathlib import Path
import json


CHUNK_DIR = Path("rag/chunks")


def load_chunk_file(chunk_file: str) -> list:
    """
    Loads chunk JSON file.
    """

    path = CHUNK_DIR / chunk_file

    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def keyword_match_score(
    query: str,
    chunk_text: str,
) -> int:
    """
    Simple keyword overlap scoring.

    Later this will be replaced by embeddings similarity.
    """

    query_words = query.lower().split()

    chunk_lower = chunk_text.lower()

    score = 0

    for word in query_words:
        if word in chunk_lower:
            score += 1

    return score


def retrieve_relevant_chunks(
    query: str,
    chunk_file: str,
    top_k: int = 3,
) -> list:
    """
    Retrieves top matching chunks.
    """

    chunk_records = load_chunk_file(chunk_file)

    if not chunk_records:
        return []

    scored_chunks = []

    for chunk in chunk_records:

        score = keyword_match_score(
            query=query,
            chunk_text=chunk["chunk_text"],
        )

        scored_chunks.append(
            {
                "chunk_id": chunk["chunk_id"],
                "chunk_text": chunk["chunk_text"],
                "score": score,
            }
        )

    scored_chunks = sorted(
        scored_chunks,
        key=lambda x: x["score"],
        reverse=True,
    )

    relevant_chunks = [
        chunk
        for chunk in scored_chunks
        if chunk["score"] > 0
    ]

    return relevant_chunks[:top_k]


if __name__ == "__main__":

    results = retrieve_relevant_chunks(
        query="Does this policy cover flood damage?",
        chunk_file="commercial_property_policy_wording_chunks.json",
        top_k=3,
    )

    print("\nRetrieved Chunks:\n")

    for result in results:

        print("=" * 80)
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Score: {result['score']}")
        print(result["chunk_text"])
        print("=" * 80)