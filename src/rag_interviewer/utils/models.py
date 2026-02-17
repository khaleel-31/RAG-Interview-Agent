import logging
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

log = logging.getLogger(__name__)

def get_model():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.4
    )
