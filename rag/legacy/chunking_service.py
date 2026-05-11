"""
chunking_service.py

Purpose:
Splits enterprise documents into smaller chunks for retrieval.

This is a foundational RAG component.
"""

from pathlib import Path
import json


CHUNK_OUTPUT_DIR = Path("rag/chunks")

CHUNK_OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def load_document(file_path: str) -> str:
    """
    Loads text document content.
    """

    path = Path(file_path)

    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8")


def chunk_document(
    document_text: str,
    chunk_size: int = 500,
    overlap: int = 100,
) -> list:
    """
    Splits document into overlapping chunks.

    Why overlap matters:
    - preserves context continuity
    - avoids cutting important sentences
    - improves retrieval quality
    """

    chunks = []

    start = 0

    while start < len(document_text):

        end = start + chunk_size

        chunk = document_text[start:end]

        chunks.append(chunk.strip())

        start += chunk_size - overlap

    return chunks


def save_chunks(
    chunks: list,
    source_document: str,
):
    """
    Saves chunks into JSON format.

    Enterprise systems usually store:
    - chunk text
    - metadata
    - source reference
    """

    chunk_records = []

    for idx, chunk in enumerate(chunks):

        chunk_records.append(
            {
                "chunk_id": f"CHK-{idx + 1:05d}",
                "source_document": source_document,
                "chunk_text": chunk,
                "chunk_length": len(chunk),
            }
        )

    output_file = (
        CHUNK_OUTPUT_DIR
        / f"{Path(source_document).stem}_chunks.json"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            chunk_records,
            f,
            indent=4,
        )

    return output_file


def process_document(
    file_path: str,
    chunk_size: int = 500,
    overlap: int = 100,
):
    """
    End-to-end chunking process.
    """

    document_text = load_document(file_path)

    if not document_text:
        print("No document content found.")
        return

    chunks = chunk_document(
        document_text=document_text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    output_file = save_chunks(
        chunks=chunks,
        source_document=file_path,
    )

    print(f"Generated {len(chunks)} chunks.")
    print(f"Saved chunk file to: {output_file}")


if __name__ == "__main__":

    process_document(
        "data/unstructured/commercial_property_policy_wording.txt"
    )