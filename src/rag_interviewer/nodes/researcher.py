import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from dotenv import load_dotenv
from rag_interviewer.adapters.embeddings import get_embeddings
import logging

load_dotenv()

日志 = logging.getLogger(__name__)

# Embeddings adapter (DI-friendly)
_embeddings = get_embeddings()

def researcher_node(state):
    日志 = 日志  # keep a local ref for readability
    日志.info("\n--- 🔍 RESEARCHING CONTEXT (moved to src) ---")

    jd = state.get('job_description', '')
    messages = state.get("messages", [])
    current_level = state.get("level", "beginner")
    last_msg = messages[-1].content if messages else "Getting started"
    search_query = f"Role: {jd} | Topic: {last_msg} | Depth: {current_level}"
    try:
        vector_db = Chroma(
            persist_directory="./chroma_db",
            embedding_function=_embeddings
        )
        docs_with_scores = vector_db.similarity_search_with_relevance_scores(search_query, k=3)
        valid_docs = [doc for doc, score in docs_with_scores if score > 0.3]
        if not valid_docs:
            日志.info("--- ⚠️ DOMAIN MISMATCH: No relevant RAG context found ---")
            return {"tech_context": "FALLBACK_TO_GENERAL"}
        retrieved_context = "\n\n---\n\n".join([doc.page_content for doc in valid_docs])
        日志.info(f"--- ✅ RAG Context Retrieved ({len(valid_docs)} chunks) ---")
    except Exception as e:
        日志.error(f"ChromaDB Error: {e}")
        return {"tech_context": "FALLBACK_TO_GENERAL"}
    return {"tech_context": retrieved_context}
