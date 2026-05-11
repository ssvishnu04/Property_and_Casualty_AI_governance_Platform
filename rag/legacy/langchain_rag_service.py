"""
langchain_rag_service.py

Purpose:
Enterprise LangChain RAG orchestration service.

Uses:
- LangChain document objects
- LangChain text splitter
- FAISS vector store
- HuggingFace embeddings
- Groq LLM
- Cached vector store for faster repeated queries
"""

from pathlib import Path
import os
from functools import lru_cache

from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq


load_dotenv()


POLICY_DOC_FILE = Path(
    "data/unstructured/commercial_property_policy_wording.txt"
)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

LLM_MODEL = "llama-3.3-70b-versatile"


def load_policy_document() -> str:
    """
    Loads policy wording document.
    """

    if not POLICY_DOC_FILE.exists():
        return ""

    return POLICY_DOC_FILE.read_text(encoding="utf-8")


def build_documents(document_text: str) -> list[Document]:
    """
    Splits document into LangChain document chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = splitter.split_text(document_text)

    documents = [
        Document(
            page_content=chunk,
            metadata={
                "source": str(POLICY_DOC_FILE),
                "chunk_number": idx + 1,
            },
        )
        for idx, chunk in enumerate(chunks)
    ]

    return documents


def build_vector_store(documents: list[Document]):
    """
    Builds FAISS vector store from LangChain documents.
    """

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vector_store = FAISS.from_documents(
        documents,
        embeddings,
    )

    return vector_store


@lru_cache(maxsize=1)
def get_cached_vector_store():
    """
    Builds vector store once and reuses it.

    This avoids rebuilding embeddings and FAISS index
    on every user request.
    """

    print("Building cached vector store...")

    document_text = load_policy_document()

    if not document_text:
        return None

    documents = build_documents(document_text)

    vector_store = build_vector_store(documents)

    print("Cached vector store ready.")

    return vector_store


@lru_cache(maxsize=1)
def get_cached_llm():
    """
    Builds Groq LLM client once and reuses it.
    """

    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Please add it to your .env file."
        )

    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name=LLM_MODEL,
        temperature=0,
    )

    return llm


def build_grounded_prompt(
    question: str,
    retrieved_docs: list[Document],
) -> str:
    """
    Builds controlled enterprise RAG prompt.
    """

    context = "\n\n".join(
        [
            f"Source Chunk {idx + 1}:\n{doc.page_content}"
            for idx, doc in enumerate(retrieved_docs)
        ]
    )

    prompt = f"""
You are a Policy Coverage Agent for an insurance and reinsurance enterprise AI governance platform.

Answer the user's question using ONLY the retrieved policy wording context below.

Rules:
- Do not invent coverage.
- If the answer is not clearly supported by the context, say that the policy wording is insufficient.
- Mention exclusions or endorsements when relevant.
- Do not provide legal advice.
- Keep the answer clear, concise, and suitable for a claims or underwriting user.

Retrieved Policy Context:
{context}

User Question:
{question}

Grounded Answer:
"""

    return prompt


def ask_policy_question(question: str) -> dict:
    """
    Executes retrieval + LLM grounded response.
    """

    vector_store = get_cached_vector_store()

    if vector_store is None:
        return {
            "answer": "No policy wording document was available for review.",
            "source_documents": [],
        }

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}
    )

    retrieved_docs = retriever.invoke(question)

    llm = get_cached_llm()

    prompt = build_grounded_prompt(
        question=question,
        retrieved_docs=retrieved_docs,
    )

    response = llm.invoke(
        [
            HumanMessage(content=prompt)
        ]
    )

    return {
        "answer": response.content,
        "source_documents": retrieved_docs,
    }


if __name__ == "__main__":

    question = "Does this policy cover flood damage?"

    result = ask_policy_question(question)

    print("\nQUESTION:\n")
    print(question)

    print("\nANSWER:\n")
    print(result["answer"])

    print("\nSOURCE DOCUMENTS:\n")

    for idx, doc in enumerate(
        result["source_documents"],
        start=1,
    ):
        print("=" * 80)
        print(f"Source Chunk {idx}")
        print(doc.page_content)
        print("=" * 80)