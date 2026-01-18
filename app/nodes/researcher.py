import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from dotenv import load_dotenv

load_dotenv()

def researcher_node(state):
    print("--- 🔍 RESEARCHING CONTEXT ---")
    
    # 1. Improved Query Construction
    # We prioritize the Job Description (JD) to ensure the retrieved context 
    # aligns with the role requirements, even if the user's last message is short.
    jd = state.get('job_description', '')
    last_msg = state["messages"][-1].content
    
    # We create a 'hybrid' query that focuses on the JD requirements 
    # filtered by the current conversation topic.
    search_query = f"Job Requirements: {jd} | Current Topic: {last_msg}"

    # 2. Initialize Embeddings
    embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
    )

    # 3. Connect to ChromaDB
    vector_db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )

    # 4. Retrieve Context
    # Increase k to 3 or 4. Since JDs are broad, pulling a bit more context 
    # helps the Interviewer stay grounded in the PDF data.
    docs = vector_db.similarity_search(search_query, k=3)
    
    retrieved_context = "\n".join([doc.page_content for doc in docs])

    print(f"--- ✅ Context Retrieved ({len(retrieved_context)} chars) ---")

    # 5. Return updated state
    return {
        "tech_context": retrieved_context
    }