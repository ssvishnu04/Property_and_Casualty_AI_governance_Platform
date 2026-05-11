"""
multi_rag_service.py

Purpose:
Centralized enterprise multi-agent RAG service
with persistent FAISS indexes and retrieval observability.

Features:
- Multi-domain RAG
- Persistent FAISS indexes
- Dynamic document loading
- Multi-format support
- Cached embeddings
- Cached vector stores
- Retrieval metadata for auditability
"""

from pathlib import Path
from functools import lru_cache
import os
import time

from dotenv import load_dotenv

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage

from langchain_community.vectorstores import (
    FAISS,
)

from langchain_huggingface import (
    HuggingFaceEmbeddings,
)

from langchain_groq import ChatGroq

from rag.document_loader import (
    load_all_documents_from_folder,
)


load_dotenv()


EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

LLM_MODEL = "llama-3.3-70b-versatile"


RAG_DOMAIN_PATHS = {
    "claims": Path("data/unstructured/claims"),
    "policy": Path("data/unstructured/policy"),
    "underwriting": Path("data/unstructured/underwriting"),
    "reinsurance": Path("data/unstructured/reinsurance"),
    "cat": Path("data/unstructured/cat"),
    "governance": Path("data/unstructured/governance"),
}


FAISS_INDEX_BASE_PATH = Path(
    "rag/faiss_indexes"
)

FAISS_INDEX_BASE_PATH.mkdir(
    parents=True,
    exist_ok=True,
)


def get_faiss_index_path(
    domain: str,
) -> Path:
    """
    Returns FAISS folder path
    for a specific RAG domain.
    """

    return (
        FAISS_INDEX_BASE_PATH / domain
    )


@lru_cache(maxsize=1)
def get_embeddings():
    """
    Loads embeddings once.
    """

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


def load_domain_documents(
    domain: str,
) -> list[Document]:
    """
    Loads all supported documents
    for a RAG domain.
    """

    domain_path = RAG_DOMAIN_PATHS.get(
        domain
    )

    if domain_path is None:
        print(
            f"Unknown RAG domain: {domain}"
        )
        return []

    if not domain_path.exists():
        print(
            f"RAG folder not found: {domain_path}"
        )
        return []

    documents = []

    text_splitter = (
        RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
        )
    )

    loaded_files = (
        load_all_documents_from_folder(
            domain_path
        )
    )

    for loaded_file in loaded_files:

        if (
            loaded_file["status"]
            != "loaded"
        ):

            print(
                f"Skipped/failed file: "
                f"{loaded_file['source']} | "
                f"{loaded_file['message']}"
            )

            continue

        text = loaded_file["text"]

        if not text.strip():

            print(
                f"Skipped empty file: "
                f"{loaded_file['source']}"
            )

            continue

        chunks = (
            text_splitter.split_text(
                text
            )
        )

        for idx, chunk in enumerate(
            chunks
        ):

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": loaded_file[
                            "source"
                        ],
                        "file_type": loaded_file[
                            "extension"
                        ],
                        "chunk_number": idx + 1,
                        "domain": domain,
                    },
                )
            )

    return documents


def build_and_save_faiss_index(
    domain: str,
):
    """
    Builds FAISS index
    and persists to disk.
    """

    print(
        f"Building FAISS index "
        f"for domain: {domain}"
    )

    documents = (
        load_domain_documents(domain)
    )

    if not documents:

        print(
            f"No documents found "
            f"for domain: {domain}"
        )

        return None

    embeddings = get_embeddings()

    vector_store = (
        FAISS.from_documents(
            documents,
            embeddings,
        )
    )

    index_path = (
        get_faiss_index_path(domain)
    )

    index_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    vector_store.save_local(
        str(index_path)
    )

    print(
        f"Saved FAISS index "
        f"for domain: {domain}"
    )

    return vector_store


@lru_cache(maxsize=10)
def get_domain_vector_store(
    domain: str,
):
    """
    Loads or builds persistent
    FAISS vector store.
    """

    index_path = (
        get_faiss_index_path(domain)
    )

    embeddings = get_embeddings()

    faiss_file = (
        index_path / "index.faiss"
    )

    pkl_file = (
        index_path / "index.pkl"
    )

    if (
        faiss_file.exists()
        and pkl_file.exists()
    ):

        try:

            print(
                f"Loading existing "
                f"FAISS index for: {domain}"
            )

            vector_store = (
                FAISS.load_local(
                    str(index_path),
                    embeddings,
                    allow_dangerous_deserialization=True,
                )
            )

            return vector_store

        except Exception as exc:

            print(
                f"Failed loading "
                f"existing index: {exc}"
            )

            print(
                f"Rebuilding index "
                f"for domain: {domain}"
            )

    return build_and_save_faiss_index(
        domain
    )


@lru_cache(maxsize=1)
def get_llm():
    """
    Loads Groq LLM once.
    """

    groq_api_key = os.getenv(
        "GROQ_API_KEY"
    )

    if not groq_api_key:

        raise ValueError(
            "Missing GROQ_API_KEY "
            "in .env"
        )

    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name=LLM_MODEL,
        temperature=0,
    )

    return llm


def build_rag_prompt(
    domain: str,
    question: str,
    retrieved_docs: list[Document],
) -> str:
    """
    Builds stricter grounded RAG prompt.
    """

    context = "\n\n".join(
        [
            (
                f"Source Chunk {idx + 1}\n"
                f"Source: {doc.metadata.get('source')}\n"
                f"File Type: {doc.metadata.get('file_type')}\n"
                f"Content:\n{doc.page_content}"
            )
            for idx, doc in enumerate(retrieved_docs)
        ]
    )

    prompt = f"""
You are an enterprise insurance AI assistant.

Domain:
{domain.upper()}

Answer the user question using ONLY the retrieved context.

Strict rules:
- Do not invent facts.
- Do not use outside knowledge.
- Do not assume missing details.
- If a requested detail is not found, say: "Not available in retrieved context."
- Keep the answer concise and directly aligned to the user question.
- Prefer bullet points.
- Mention source-based reasoning only when supported by retrieved context.
- Do not provide legal advice.
- Include concise next steps when they are directly supported by retrieved context.
- Use important terms from the retrieved context such as coverage review, reserve adequacy, pricing adequacy, CAT aggregation, recoverable estimate, and operational impact when relevant.

Retrieved Context:
{context}

User Question:
{question}

Grounded Answer:
"""

    return prompt


def build_retrieved_sources_metadata(
    retrieved_results: list,
) -> list[dict]:
    """
    Builds source-level retrieval metadata
    for observability and audit logging.
    """

    retrieved_sources = []

    for doc, score in retrieved_results:

        retrieved_sources.append(
            {
                "source": doc.metadata.get(
                    "source",
                    "Unknown Source",
                ),
                "file_type": doc.metadata.get(
                    "file_type",
                    "unknown",
                ),
                "chunk_number": doc.metadata.get(
                    "chunk_number",
                    "unknown",
                ),
                "domain": doc.metadata.get(
                    "domain",
                    "unknown",
                ),
                "similarity_score": round(
                    float(score),
                    4,
                ),
            }
        )

    return retrieved_sources


def ask_rag_question(
    domain: str,
    question: str,
) -> dict:
    """
    Executes enterprise RAG workflow.
    """

    retrieval_start = time.time()

    vector_store = (
        get_domain_vector_store(
            domain
        )
    )

    if vector_store is None:

        return {
            "answer": (
                f"No RAG documents "
                f"available for domain "
                f"'{domain}'."
            ),
            "source_documents": [],
            "retrieved_sources": [],
            "retrieved_chunk_count": 0,
            "retrieval_latency_seconds": 0,
        }

    retrieved_results = (
        vector_store.similarity_search_with_score(
            question,
            k=3,
        )
    )

    retrieved_docs = [
        result[0]
        for result in retrieved_results
    ]

    retrieved_sources = (
        build_retrieved_sources_metadata(
            retrieved_results
        )
    )

    retrieval_latency = (
        time.time() - retrieval_start
    )

    if not retrieved_docs:

        return {
            "answer": (
                "No relevant RAG context "
                "was retrieved."
            ),
            "source_documents": [],
            "retrieved_sources": [],
            "retrieved_chunk_count": 0,
            "retrieval_latency_seconds": (
                retrieval_latency
            ),
        }

    llm = get_llm()

    prompt = build_rag_prompt(
        domain=domain,
        question=question,
        retrieved_docs=retrieved_docs,
    )

    response = llm.invoke(
        [
            HumanMessage(
                content=prompt
            )
        ]
    )

    return {
        "answer": response.content,
        "source_documents": retrieved_docs,
        "retrieved_sources": retrieved_sources,
        "retrieved_chunk_count": len(
            retrieved_docs
        ),
        "retrieval_latency_seconds": (
            retrieval_latency
        ),
    }


def rebuild_domain_index(
    domain: str,
):
    """
    Forces rebuild of a domain index.
    """

    print(
        f"Rebuilding domain index: "
        f"{domain}"
    )

    get_domain_vector_store.cache_clear()

    return build_and_save_faiss_index(
        domain
    )


def rebuild_all_indexes():
    """
    Rebuilds all domain indexes.
    """

    get_domain_vector_store.cache_clear()

    for domain in (
        RAG_DOMAIN_PATHS.keys()
    ):

        rebuild_domain_index(
            domain
        )


if __name__ == "__main__":

    rebuild_all_indexes()

    result = ask_rag_question(
        domain="claims",
        question=(
            "What are escalation "
            "requirements for "
            "large-loss claims?"
        ),
    )

    print("\nANSWER:\n")
    print(result["answer"])

    print("\nRETRIEVAL LATENCY:\n")
    print(
        result[
            "retrieval_latency_seconds"
        ]
    )

    print("\nRETRIEVED SOURCES METADATA:\n")
    for source in result[
        "retrieved_sources"
    ]:

        print(source)

    print("\nSOURCE CHUNKS:\n")

    for doc in result[
        "source_documents"
    ]:

        print("=" * 80)
        print(doc.metadata)
        print(doc.page_content[:500])