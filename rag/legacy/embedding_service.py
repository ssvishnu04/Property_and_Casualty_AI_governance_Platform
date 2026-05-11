"""
embedding_service.py

Purpose:
Generates embeddings for chunked enterprise documents.

This is a foundational enterprise RAG component.
"""

from pathlib import Path
import json
import pickle

from sentence_transformers import SentenceTransformer
import numpy as np


CHUNK_DIR = Path("rag/chunks")
VECTOR_OUTPUT_DIR = Path("rag/faiss_index")

VECTOR_OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_embedding_model():
    """
    Loads embedding model.
    """

    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Embedding model loaded.")

    return model


def load_chunk_records(chunk_file: str) -> list:
    """
    Loads chunk records from JSON.
    """

    path = CHUNK_DIR / chunk_file

    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_embeddings(
    chunk_records: list,
    model,
):
    """
    Generates embeddings for chunk text.
    """

    chunk_texts = [
        chunk["chunk_text"]
        for chunk in chunk_records
    ]

    embeddings = model.encode(
        chunk_texts,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    return embeddings


def save_embeddings(
    chunk_records: list,
    embeddings: np.ndarray,
    output_name: str,
):
    """
    Saves embeddings + metadata locally.
    """

    output_path = VECTOR_OUTPUT_DIR / output_name

    records = []

    for idx, chunk in enumerate(chunk_records):

        records.append(
            {
                "chunk_id": chunk["chunk_id"],
                "chunk_text": chunk["chunk_text"],
                "embedding": embeddings[idx],
            }
        )

    with open(output_path, "wb") as f:
        pickle.dump(records, f)

    print(f"Saved embeddings to: {output_path}")


def process_embeddings(
    chunk_file: str,
    output_name: str,
):
    """
    End-to-end embedding generation.
    """

    model = load_embedding_model()

    chunk_records = load_chunk_records(chunk_file)

    if not chunk_records:
        print("No chunk records found.")
        return

    embeddings = generate_embeddings(
        chunk_records=chunk_records,
        model=model,
    )

    print(f"Generated embeddings shape: {embeddings.shape}")

    save_embeddings(
        chunk_records=chunk_records,
        embeddings=embeddings,
        output_name=output_name,
    )


if __name__ == "__main__":

    process_embeddings(
        chunk_file="commercial_property_policy_wording_chunks.json",
        output_name="policy_embeddings.pkl",
    )