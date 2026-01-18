import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def get_model():
    # llama-3.3-70b-versatile is arguably the best "smart" model on Groq right now
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.4
    )