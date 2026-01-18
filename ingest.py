import os
# Force Python to ignore the broken DLL if any traces remain
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

def run_ingestion():
    print("--- 🚀 Starting Cloud Ingestion ---")
    
    # 1. Load documents
    loader = DirectoryLoader('./data', glob="./*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()
    print(f"Loaded {len(docs)} documents.")

    # 2. Split documents (using a simpler splitter to avoid torch imports)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)

    # 3. Cloud Embeddings
    embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
    )

    # 4. Save to ChromaDB
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print(f"--- ✅ Success! {len(chunks)} chunks saved to ./chroma_db ---")

if __name__ == "__main__":
    run_ingestion()