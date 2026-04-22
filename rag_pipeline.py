"""
AutoStream AI Agent - RAG Pipeline
Loads the JSON knowledge base, chunks it into documents, builds a local
FAISS vector store, and exposes a retriever for grounded responses.
"""

import json
import logging
from typing import List

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import KNOWLEDGE_BASE_PATH

logger = logging.getLogger("autostream.rag")


# ---------------------------------------------------------------------------
# Document loader
# ---------------------------------------------------------------------------

def _load_documents() -> List[Document]:
    """Read `knowledge_base.json` and convert every logical section into a
    LangChain Document with metadata."""

    logger.info("Loading knowledge base from %s", KNOWLEDGE_BASE_PATH)

    with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as fh:
        kb = json.load(fh)

    docs: List[Document] = []

    # -- Products / Pricing --------------------------------------------------
    for product in kb.get("products", []):
        features = "\n  • ".join(product["features"])
        text = (
            f"Plan: {product['plan']}\n"
            f"Price: {product['price']}\n"
            f"Features:\n  • {features}"
        )
        docs.append(
            Document(page_content=text, metadata={"source": "pricing", "plan": product["plan"]})
        )

    # -- Policies -------------------------------------------------------------
    for policy in kb.get("policies", []):
        text = f"{policy['topic']}:\n{policy['details']}"
        docs.append(
            Document(page_content=text, metadata={"source": "policy", "topic": policy["topic"]})
        )

    # -- FAQs -----------------------------------------------------------------
    for faq in kb.get("faqs", []):
        text = f"Q: {faq['question']}\nA: {faq['answer']}"
        docs.append(
            Document(page_content=text, metadata={"source": "faq"})
        )

    logger.info("Loaded %d documents from knowledge base", len(docs))
    return docs


# ---------------------------------------------------------------------------
# Vector store & retriever
# ---------------------------------------------------------------------------

_vectorstore = None  # module-level cache


def get_retriever(k: int = 3):
    """Return a FAISS-backed retriever. The vector store is built once and
    cached for the lifetime of the process."""

    global _vectorstore

    if _vectorstore is None:
        logger.info("Building FAISS vector store (first call)…")
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        documents = _load_documents()
        _vectorstore = FAISS.from_documents(documents, embeddings)
        logger.info("Vector store ready (%d vectors)", len(documents))

    return _vectorstore.as_retriever(search_kwargs={"k": k})


def retrieve_context(query: str, k: int = 3) -> str:
    """Convenience helper: retrieve top-k docs and return them as a single
    formatted context string."""

    retriever = get_retriever(k=k)
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant information found in the knowledge base."

    context_parts = []
    for i, doc in enumerate(docs, 1):
        context_parts.append(f"[Source {i} — {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}")

    context = "\n\n---\n\n".join(context_parts)
    logger.debug("Retrieved %d documents for query: %s", len(docs), query[:80])
    return context
