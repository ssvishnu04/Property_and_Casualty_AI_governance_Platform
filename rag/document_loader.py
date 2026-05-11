"""
document_loader.py

Purpose:
Dynamic document loader for enterprise RAG.

Supports multiple unstructured/semi-structured formats
without breaking the pipeline when unsupported files appear.
"""

from pathlib import Path
import json
import csv
import xml.etree.ElementTree as ET

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".xml",
    ".pdf",
}


def load_text_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore")


def load_csv_file(file_path: Path) -> str:
    rows = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row_text = ", ".join(
                [f"{key}: {value}" for key, value in row.items()]
            )
            rows.append(row_text)

    return "\n".join(rows)


def load_json_file(file_path: Path) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        data = json.load(file)

    return json.dumps(data, indent=2)


def load_xml_file(file_path: Path) -> str:
    tree = ET.parse(file_path)
    root = tree.getroot()

    text_parts = []

    for elem in root.iter():
        if elem.text and elem.text.strip():
            text_parts.append(elem.text.strip())

    return "\n".join(text_parts)


def load_pdf_file(file_path: Path) -> str:
    reader = PdfReader(str(file_path))

    pages = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages.append(page_text)

    return "\n".join(pages)


def load_document_text(file_path: Path) -> dict:
    """
    Loads document text based on extension.

    Returns:
    {
        "status": "loaded" | "skipped" | "failed",
        "text": "...",
        "source": "...",
        "extension": ".txt",
        "message": "..."
    }
    """

    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        return {
            "status": "skipped",
            "text": "",
            "source": str(file_path),
            "extension": extension,
            "message": f"Unsupported file type: {extension}",
        }

    try:
        if extension in [".txt", ".md"]:
            text = load_text_file(file_path)

        elif extension == ".csv":
            text = load_csv_file(file_path)

        elif extension == ".json":
            text = load_json_file(file_path)

        elif extension == ".xml":
            text = load_xml_file(file_path)

        elif extension == ".pdf":
            text = load_pdf_file(file_path)

        else:
            text = ""

        return {
            "status": "loaded",
            "text": text,
            "source": str(file_path),
            "extension": extension,
            "message": "Loaded successfully",
        }

    except Exception as error:
        return {
            "status": "failed",
            "text": "",
            "source": str(file_path),
            "extension": extension,
            "message": str(error),
        }


def load_all_documents_from_folder(folder_path: Path) -> list[dict]:
    """
    Loads all files in a folder safely.

    Unsupported files are skipped, not failed.
    """

    results = []

    if not folder_path.exists():
        return results

    for file_path in folder_path.rglob("*"):
        if file_path.is_file():
            results.append(
                load_document_text(file_path)
            )

    return results