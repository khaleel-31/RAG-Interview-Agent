def get_embeddings():
    """DI-friendly embeddings factory.

    Tries to create a HuggingFace embeddings adapter using centralized config.
    Falls back to None if dependencies/config are unavailable.
    """
    try:
        from langchain_huggingface import HuggingFaceEndpointEmbeddings
        from rag_interviewer.config import get_config

        cfg = get_config()
        return HuggingFaceEndpointEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2",
            huggingfacehub_api_token=cfg.huggingface_token,
        )
    except Exception:
        return None
