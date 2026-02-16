from rag_interviewer.utils.models import get_model
from langchain_core.messages import SystemMessage
import logging
from rag_interviewer.logging import get_logger

log = get_logger(__name__)


def interviewer_node(state):
    model = get_model()
    jd = state.get("job_description", "Technical Role")
    current_level = state.get("level", "beginner")
    tech_context = state.get("tech_context", "")
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
    messages = [SystemMessage(content=system_content)] + state["messages"]
    response = model.invoke(messages)
    return {
        "messages": [response],
        "skill_gap": []
    }
