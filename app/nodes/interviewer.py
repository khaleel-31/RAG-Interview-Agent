from app.utils.models import get_model
from langchain_core.messages import SystemMessage
import streamlit as st

def interviewer_node(state):
    model = get_model()
    
    # 1. Fetching essential state
    jd = state.get("job_description", "Technical Role")
    current_level = state.get("level", "beginner")
    tech_context = state.get("tech_context", "")
    
    # 2. Simplified prompt to prevent "Chatter"
    system_content = (
        f"You are a Senior Technical Interviewer for: {jd}. "
        f"\n\n--- 📖 TECH DATA ---"
        f"\n{tech_context}"
        f"\n\n--- 🛡️ RULES ---"
        f"\n1. Ask exactly ONE targeted question. Do not provide code."
        f"\n2. DO NOT repeat the assessment or feedback already provided."
        f"\n3. DO NOT use filler like 'Next Question', 'Let's move on', or 'It was a pleasure'."
        f"\n4. DO NOT conclude the interview. Just ask the question and stop."
        f"\n\nInterview Level: {current_level}."
    )

    # 3. Message Assembly
    messages = [SystemMessage(content=system_content)] + state["messages"]
    
    # 4. Invoke model
    response = model.invoke(messages)
    
    return {
        "messages": [response],
        "skill_gap": [] 
    }