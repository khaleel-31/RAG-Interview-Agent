import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Singleton embeddings to prevent re-initialization
_embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=st.secrets.get("HUGGINGFACEHUB_API_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
)

def researcher_node(state):
    print("\n--- 🔍 RESEARCHING CONTEXT ---")
    
    jd = state.get('job_description', '')
    messages = state.get("messages", [])
    current_level = state.get("level", "beginner")
    last_msg = messages[-1].content if messages else "Getting started"
    
    # 1. Hybrid Search Query
    search_query = f"Role: {jd} | Topic: {last_msg} | Depth: {current_level}"

    try:
        # 2. Connect to Chroma
        vector_db = Chroma(
            persist_directory="./chroma_db",
            embedding_function=_embeddings
        )

        # 3. Retrieve with a relevance threshold
        # We fetch more chunks initially to ensure we find high-quality matches
        docs_with_scores = vector_db.similarity_search_with_relevance_scores(search_query, k=3)
        
        # 4. Filter by score (0.0 to 1.0)
        # If the top result is lower than 0.3, it's likely irrelevant (like Pharmacist vs AI docs)
        valid_docs = [doc for doc, score in docs_with_scores if score > 0.3]

        if not valid_docs:
            print("--- ⚠️ DOMAIN MISMATCH: No relevant RAG context found ---")
            return {"tech_context": "FALLBACK_TO_GENERAL"}

        retrieved_context = "\n\n---\n\n".join([doc.page_content for doc in valid_docs])
        print(f"--- ✅ RAG Context Retrieved ({len(valid_docs)} chunks) ---")

    except Exception as e:
        print(f"❌ ChromaDB Error: {e}")
        # On error, we fallback to general knowledge so the interview doesn't crash
        return {"tech_context": "FALLBACK_TO_GENERAL"}

    return {
        "tech_context": retrieved_context
    }