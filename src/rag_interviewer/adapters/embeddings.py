"""Embeddings adapter for vector database operations."""
import os
from typing import Optional

from rag_interviewer.logging import get_logger

logger = get_logger(__name__)


def get_embeddings():
    """Get or create embeddings model.
    
    Returns:
        HuggingFace embeddings model or None if not available
    """
    try:
        from langchain_huggingface import HuggingFaceEndpointEmbeddings
        
        # Try to get API token from environment
        api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        
        if api_token:
            embeddings = HuggingFaceEndpointEmbeddings(
                model="sentence-transformers/all-MiniLM-L6-v2",
                huggingfacehub_api_token=api_token
            )
            logger.info("Embeddings model initialized successfully")
            return embeddings
        else:
            logger.warning("HUGGINGFACEHUB_API_TOKEN not set, embeddings not available")
            return None
    except ImportError:
        logger.warning("langchain_huggingface not installed, embeddings not available")
        return None
    except Exception as e:
        logger.error(f"Error initializing embeddings: {e}")
        return None
