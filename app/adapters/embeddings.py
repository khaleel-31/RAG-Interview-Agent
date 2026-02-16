from app.config import get_config
from app.logging import get_logger
from langchain_huggingface import HuggingFaceEndpointEmbeddings


_log = get_logger(__name__)


def get_embeddings() -> HuggingFaceEndpointEmbeddings:
    """Factory for embeddings adapter used by RAG context.

    Reads tokens from the centralized config and returns a configured
    HuggingFaceEndpointEmbeddings instance.
    """
    cfg = get_config()
    _log.info("Initializing HuggingFace embeddings adapter")
    return HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        huggingfacehub_api_token=cfg.huggingface_token,
    )
