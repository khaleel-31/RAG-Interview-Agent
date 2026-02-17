"""MCP-enhanced researcher node with live documentation fetching."""
import logging
from typing import Dict, List, Any

from dotenv import load_dotenv
from langchain_chroma import Chroma

from rag_interviewer.adapters.embeddings import get_embeddings
from rag_interviewer.mcp_client import get_tech_trends_sync

load_dotenv()

# Embeddings adapter (DI-friendly)
_embeddings = get_embeddings()
_logger = logging.getLogger(__name__)


def extract_tech_keywords(text: str) -> List[str]:
    """Extract technology keywords from job description or messages.
    
    Args:
        text: Input text to analyze
        
    Returns:
        List of detected technology keywords
    """
    # Common tech keywords to detect
    tech_keywords = [
        "python", "javascript", "typescript", "java", "go", "rust", "cpp", "c++",
        "react", "vue", "angular", "django", "flask", "fastapi", "spring",
        "kubernetes", "docker", "aws", "azure", "gcp", "terraform",
        "machine learning", "ai", "ml", "data science", "llm", "rag",
        "sql", "postgresql", "mongodb", "redis", "elasticsearch",
        "microservices", "api", "graphql", "rest", "grpc",
        "git", "ci/cd", "devops", "agile", "scrum"
    ]
    
    text_lower = text.lower()
    detected = []
    for keyword in tech_keywords:
        if keyword in text_lower:
            detected.append(keyword)
    
    return detected


def researcher_node_enhanced(state: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced researcher node with MCP integration.
    
    Combines ChromaDB RAG with live MCP documentation fetching.
    
    Args:
        state: Interview state with job_description, messages, level
        
    Returns:
        Updated state with enhanced tech_context
    """
    _logger.info("\n--- 🔍 RESEARCHING CONTEXT (MCP-Enhanced) ---")

    jd = state.get("job_description", "")
    messages = state.get("messages", [])
    current_level = state.get("level", "beginner")
    last_msg = messages[-1].content if messages else "Getting started"
    
    # Combine JD and last message for context search
    search_context = f"{jd} {last_msg}"
    
    # 1. Extract tech keywords for MCP lookup
    tech_keywords = extract_tech_keywords(search_context)
    _logger.info(f"Detected technologies: {tech_keywords}")
    
    # 2. Fetch local RAG context from ChromaDB
    local_context = ""
    try:
        vector_db = Chroma(
            persist_directory="./chroma_db",
            embedding_function=_embeddings
        )
        search_query = f"Role: {jd} | Topic: {last_msg} | Depth: {current_level}"
        docs_with_scores = vector_db.similarity_search_with_relevance_scores(
            search_query, k=3
        )
        valid_docs = [doc for doc, score in docs_with_scores if score > 0.3]
        if valid_docs:
            local_context = "\n\n---\n\n".join([doc.page_content for doc in valid_docs])
            _logger.info(f"--- ✅ RAG Context Retrieved ({len(valid_docs)} chunks) ---")
        else:
            _logger.info("--- ⚠️ No local RAG context found ---")
    except Exception as e:
        _logger.error(f"ChromaDB Error: {e}")
    
    # 3. Fetch live tech trends via MCP
    mcp_context = ""
    if tech_keywords:
        _logger.info("--- 🌐 Fetching live tech trends via MCP ---")
        trends_sections = []
        for keyword in tech_keywords[:3]:  # Limit to top 3
            try:
                trends = get_tech_trends_sync(keyword)
                if trends and trends != [f"Current trends in {keyword}"]:
                    trends_sections.append(f"**{keyword.title()} Trends:** {', '.join(trends)}")
            except Exception as e:
                _logger.warning(f"MCP fetch failed for {keyword}: {e}")
        
        if trends_sections:
            mcp_context = "\n\n".join(trends_sections)
            _logger.info("--- ✅ Live trends retrieved via MCP ---")
    
    # 4. Combine contexts
    combined_context = ""
    if local_context:
        combined_context += f"## Local Knowledge Base\n{local_context}\n\n"
    if mcp_context:
        combined_context += f"## Current Industry Trends (via MCP)\n{mcp_context}\n\n"
    
    if not combined_context:
        _logger.warning("--- ⚠️ No context available, using fallback ---")
        return {"tech_context": "FALLBACK_TO_GENERAL"}
    
    _logger.info("--- ✅ Combined context ready (RAG + MCP) ---")
    return {"tech_context": combined_context}


# Alias for backward compatibility
researcher_node = researcher_node_enhanced
