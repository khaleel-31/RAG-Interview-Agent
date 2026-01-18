from app.utils.models import get_model
from langchain_core.messages import SystemMessage

def interviewer_node(state):
    model = get_model()
    
    # Get the Job Description from state
    jd = state.get("job_description", "Technical Role")
    current_level = state.get("level", "beginner")
    
    if state.get("skill_gap"):
        # TEACHER MODE - CONCEPTUAL ONLY
        print("--- Node: Interviewer (TEACHING) ---")
        system_content = (
            f"You are a Technical Mentor for the role: {jd}. "
            f"The user is struggling with: {state['skill_gap']}. "
            f"Explain the THEORY and LOGIC behind these concepts. "
            f"STRICT RULE: Do not provide code examples. Use analogies and high-level descriptions."
        )
    else:
        # INTERVIEWER MODE - CONCEPTUAL GUARDRAILS
        print(f"--- Node: Interviewer (INTERVIEWING - {current_level}) ---")
        system_content = (
            f"You are a Senior Technical Interviewer for: {jd}. "
            f"Context: {state.get('tech_context', '')}. "
            f"\n\n--- 🛡️ INTERVIEW GUARDRAILS ---"
            f"\n1. NEVER ask the candidate to write, complete, or debug code."
            f"\n2. NEVER ask about specific programming syntax (e.g., 'What is the keyword for...')."
            f"\n3. FOCUS EXCLUSIVELY on architectural patterns, system design, theoretical principles, and performance trade-offs."
            f"\n4. If the provided context contains code, translate the logic of that code into a high-level conceptual question."
            f"\n5. Ask exactly ONE question. Level: {current_level}."
        )

    # 2. Build the message list
    messages = [SystemMessage(content=system_content)] + state["messages"]
    
    # 3. Get LLM response
    response = model.invoke(messages)
    
    # 4. Return updates (Ensure skill_gap is cleared to avoid teaching loops)
    return {
        "messages": [response],
        "skill_gap": [] 
    }