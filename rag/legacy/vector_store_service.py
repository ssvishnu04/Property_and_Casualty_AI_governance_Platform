"""
vector_store_service.py

Purpose:
Creates and queries FAISS vector index for semantic retrieval.

This is a core enterprise RAG component.
"""

from pathlib import Path
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


VECTOR_DIR = Path("rag/faiss_index")

EMBEDDING_FILE = VECTOR_DIR / "policy_embeddings.pkl"
FAISS_INDEX_FILE = VECTOR_DIR / "policy_faiss.index"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_embedding_model():
    """
    Loads embedding model.
    """

    model = SentenceTransformer(MODEL_NAME)

    return model


def load_embedding_records():
    """
    Loads saved embedding records.
    """

    if not EMBEDDING_FILE.exists():
        return []

    with open(EMBEDDING_FILE, "rb") as f:
        return pickle.load(f)


def build_faiss_index():
    """
    Builds FAISS vector index from embeddings.
    """

    records = load_embedding_records()

    if not records:
        print("No embedding records found.")
        return

    embeddings = np.array(
        [record["embedding"] for record in records],
        dtype="float32",
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    faiss.write_index(
        index,
        str(FAISS_INDEX_FILE),
    )

    print(f"FAISS index created with {len(records)} vectors.")
    print(f"Saved index to: {FAISS_INDEX_FILE}")


def load_faiss_index():
    """
    Loads FAISS vector index.
    """

    if not FAISS_INDEX_FILE.exists():
        return None

    return faiss.read_index(str(FAISS_INDEX_FILE))


def semantic_search(
    query: str,
    top_k: int = 3,
):
    """
    Performs semantic similarity search.
    """

    records = load_embedding_records()

    if not records:
        return []

    index = load_faiss_index()

    if index is None:
        return []

    model = load_embedding_model()

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
    ).astype("float32")

    distances, indices = index.search(
        query_embedding,
        top_k,
    )

    results = []

    for idx, distance in zip(indices[0], distances[0]):

        record = records[idx]

        results.append(
            {
                "chunk_id": record["chunk_id"],
                "chunk_text": record["chunk_text"],
                "distance": round(float(distance), 4),
            }
        )

    return results


if __name__ == "__main__":

    build_faiss_index()

    print("\nSemantic Search Results:\n")

    results = semantic_search(
        query="Does this policy cover flood damage?",
        top_k=3,
    )

    for result in results:

        print("=" * 80)
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Distance: {result['distance']}")
        print(result["chunk_text"])
        print("=" * 80)