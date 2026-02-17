"""Advanced MCP-enhanced researcher node with multi-server support.

Fetches context from multiple MCP servers including:
- Python documentation
- GitHub repositories
- Stack Overflow
- Internal knowledge base
"""
import logging
from typing import Dict, List, Any, Optional
import asyncio

from rag_interviewer.adapters.embeddings import get_embeddings
from rag_interviewer.logging import get_logger
from rag_interviewer.mcp_multi_client import (
    MultiServerMCPClient,
    fetch_documentation,
    search_code_examples
)
from rag_interviewer.mcp_config import get_mcp_registry

_logger = get_logger(__name__)


def extract_tech_keywords(text: str) -> List[str]:
    """Extract technology keywords from job description or messages.
    
    Args:
        text: Input text to analyze
        
    Returns:
        List of detected technology keywords
    """
    # Comprehensive tech keyword database
    tech_keywords = {
        # Languages
        "python", "javascript", "typescript", "java", "go", "rust", "cpp", "c++", "c#",
        "ruby", "php", "swift", "kotlin", "scala", "r", "julia", "dart",
        
        # Frameworks & Libraries
        "django", "flask", "fastapi", "tornado", "pyramid",
        "react", "vue", "angular", "svelte", "nextjs", "nuxt",
        "spring", "express", "nest", "laravel", "rails",
        "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
        
        # Databases
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "cassandra", "dynamodb", "firebase", "sqlite", "neo4j",
        
        # Infrastructure & DevOps
        "kubernetes", "docker", "aws", "azure", "gcp", "terraform",
        "jenkins", "gitlab-ci", "github-actions", "circleci", "travis",
        "nginx", "apache", "cdn", "load-balancer",
        
        # Concepts
        "microservices", "api", "graphql", "rest", "grpc", "websocket",
        "oauth", "jwt", "authentication", "authorization",
        "ci/cd", "devops", "sre", "agile", "scrum", "kanban",
        "machine learning", "ai", "ml", "deep learning", "nlp",
        "data science", "big data", "etl", "data pipeline",
        "blockchain", "smart contracts", "web3",
        "serverless", "faas", "lambda", "cloud functions",
        
        # Tools
        "git", "github", "gitlab", "bitbucket",
        "jira", "confluence", "trello", "notion",
        "vscode", "intellij", "pycharm", "vim",
    }
    
    text_lower = text.lower()
    detected = []
    
    for keyword in tech_keywords:
        if keyword in text_lower:
            detected.append(keyword)
    
    return detected


def _get_local_context(
    jd: str,
    messages: List[Any],
    current_level: str,
    embeddings: Any
) -> Optional[str]:
    """Fetch context from local ChromaDB."""
    if embeddings is None:
        return None
    
    try:
        from langchain_chroma import Chroma
        
        last_msg = messages[-1].content if messages else "Getting started"
        search_query = f"Role: {jd} | Topic: {last_msg} | Depth: {current_level}"
        
        vector_db = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings
        )
        
        docs_with_scores = vector_db.similarity_search_with_relevance_scores(
            search_query, k=3
        )
        valid_docs = [doc for doc, score in docs_with_scores if score > 0.3]
        
        if valid_docs:
            return "\n\n---\n\n".join([doc.page_content for doc in valid_docs])
        
    except Exception as e:
        _logger.warning(f"Local RAG failed: {e}")
    
    return None


def _get_mcp_context_sync(tech_keywords: List[str]) -> Dict[str, Any]:
    """Fetch context from MCP servers synchronously.
    
    Args:
        tech_keywords: List of detected technology keywords
        
    Returns:
        Dict with documentation and examples from various sources
    """
    context = {
        "documentation": [],
        "code_examples": [],
        "trends": [],
        "sources": []
    }
    
    # Get enabled MCP servers
    registry = get_mcp_registry()
    enabled_servers = registry.get_enabled_servers()
    
    if not enabled_servers:
        _logger.info("No MCP servers enabled, skipping MCP context")
        return context
    
    _logger.info(f"Fetching MCP context from {len(enabled_servers)} servers...")
    
    try:
        # For each tech keyword, try to fetch docs and examples
        for keyword in tech_keywords[:3]:  # Limit to top 3
            _logger.info(f"  Searching MCP for: {keyword}")
            
            # Fetch documentation (async -> sync wrapper)
            try:
                docs_result = asyncio.run(
                    fetch_documentation(
                        f"{keyword} best practices",
                        sources=["python_docs", "stackoverflow"]
                    )
                )
                
                for source, docs in docs_result.items():
                    if docs:
                        context["documentation"].append({
                            "keyword": keyword,
                            "source": source,
                            "content": docs[0]["content"][:1000]  # Limit length
                        })
                        if source not in context["sources"]:
                            context["sources"].append(source)
                
            except Exception as e:
                _logger.warning(f"    Docs fetch failed for {keyword}: {e}")
            
            # Search code examples
            try:
                examples = asyncio.run(
                    search_code_examples(keyword, language="python")
                )
                
                for example in examples[:2]:  # Top 2 examples
                    context["code_examples"].append({
                        "keyword": keyword,
                        "source": example["source"],
                        "language": example["language"],
                        "content": example["content"][:800]
                    })
                    if example["source"] not in context["sources"]:
                        context["sources"].append(example["source"])
                
            except Exception as e:
                _logger.warning(f"    Code search failed for {keyword}: {e}")
    
    except Exception as e:
        _logger.error(f"MCP context fetch failed: {e}")
    
    return context


def researcher_node_multi_mcp(state: Dict[str, Any]) -> Dict[str, Any]:
    """Advanced researcher node with multi-server MCP support.
    
    Combines local ChromaDB with multiple MCP sources:
    - Local RAG (ChromaDB)
    - Python documentation via MCP
    - Stack Overflow via MCP
    - GitHub examples via MCP
    - Internal knowledge base via MCP
    
    Args:
        state: Interview state with job_description, messages, level
        
    Returns:
        Updated state with enhanced tech_context
    """
    _logger.info("\n" + "="*60)
    _logger.info("🔍 ADVANCED RESEARCHER (Multi-Server MCP)")
    _logger.info("="*60)
    
    jd = state.get("job_description", "")
    messages = state.get("messages", [])
    current_level = state.get("level", "beginner")
    
    _logger.info(f"Job Description: {jd[:100]}...")
    _logger.info(f"Current Level: {current_level}")
    
    # 1. Extract tech keywords
    _logger.info("\n📋 Extracting Technology Keywords...")
    tech_keywords = extract_tech_keywords(jd)
    _logger.info(f"   Found: {', '.join(tech_keywords) if tech_keywords else 'None'}")
    
    # 2. Get local RAG context
    _logger.info("\n💾 Fetching Local RAG Context...")
    embeddings = get_embeddings()
    local_context = _get_local_context(jd, messages, current_level, embeddings)
    
    if local_context:
        _logger.info(f"   ✓ Retrieved {len(local_context)} chars from local DB")
    else:
        _logger.info("   ⚠ No local context available")
    
    # 3. Get MCP context from multiple servers
    mcp_context = None
    if tech_keywords:
        _logger.info("\n🌐 Fetching MCP Context from Multiple Sources...")
        mcp_data = _get_mcp_context_sync(tech_keywords)
        
        # Format MCP context
        mcp_sections = []
        
        if mcp_data["documentation"]:
            mcp_sections.append("## Documentation from MCP Sources")
            for doc in mcp_data["documentation"]:
                mcp_sections.append(f"\n**{doc['keyword']}** ({doc['source']}):\n{doc['content']}")
        
        if mcp_data["code_examples"]:
            mcp_sections.append("\n## Code Examples from MCP Sources")
            for ex in mcp_data["code_examples"]:
                mcp_sections.append(f"\n**{ex['keyword']}** ({ex['source']}):\n```{ex['language']}\n{ex['content']}\n```")
        
        if mcp_sections:
            mcp_context = "\n".join(mcp_sections)
            _logger.info(f"   ✓ Retrieved context from: {', '.join(mcp_data['sources'])}")
        else:
            _logger.info("   ⚠ No MCP context retrieved")
    
    # 4. Combine all contexts
    _logger.info("\n📊 Combining Contexts...")
    combined_sections = []
    
    if local_context:
        combined_sections.append("## Internal Knowledge Base\n" + local_context)
    
    if mcp_context:
        combined_sections.append(mcp_context)
    
    if not combined_sections:
        _logger.warning("   ⚠ No context available, using fallback")
        return {"tech_context": "FALLBACK_TO_GENERAL"}
    
    final_context = "\n\n---\n\n".join(combined_sections)
    
    _logger.info(f"\n✅ Final Context: {len(final_context)} characters")
    _logger.info(f"   Sources: {'Local DB' if local_context else ''} " +
                f"{'+ MCP' if mcp_context else ''}")
    _logger.info("="*60 + "\n")
    
    return {"tech_context": final_context}


# Backward compatibility alias
researcher_node = researcher_node_multi_mcp
