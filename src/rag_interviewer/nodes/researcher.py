import logging

from dotenv import load_dotenv
from langchain_chroma import Chroma

from rag_interviewer.adapters.embeddings import get_embeddings

load_dotenv()

# Embeddings adapter (DI-friendly)
_embeddings = get_embeddings()
_logger = logging.getLogger(__name__)

def researcher_node(state):
    _logger.info("\n--- 🔍 RESEARCHING CONTEXT ---")

    jd = state.get("job_description", "")
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
            _logger.info("--- ⚠️ DOMAIN MISMATCH: No relevant RAG context found ---")
            return {"tech_context": "FALLBACK_TO_GENERAL"}
        retrieved_context = "\n\n---\n\n".join([doc.page_content for doc in valid_docs])
        _logger.info(f"--- ✅ RAG Context Retrieved ({len(valid_docs)} chunks) ---")
    except Exception as e:
        _logger.error(f"ChromaDB Error: {e}")
        return {"tech_context": "FALLBACK_TO_GENERAL"}
    return {"tech_context": retrieved_context}
